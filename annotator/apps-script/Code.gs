const SHEETS = {
  TASKS: 'Tasks',
  ANNOTATIONS: 'Annotations',
  ANNOTATORS: 'Annotators',
  ASSIGNMENTS: 'Assignments',
};

const VALIDATION_TERMS_VERSION = 'romanbench-validation-v1';
const DEFAULT_BUNDLE_SIZE = 5;
const MAX_BUNDLE_SIZE = 8;
const LEASE_TTL_MS = 30 * 60 * 1000;
const TASK_CACHE_SECONDS = 60;
const SITE_URL = 'https://vishwanath-gowda.github.io/KannadaLLMBench';

const HEADERS = {
  Tasks: [
    'task_id', 'semantic_family_id', 'kannada', 'roman', 'variant_type',
    'source_type', 'source_id', 'source_author_id', 'batch_id', 'target_votes', 'active'
  ],
  Annotations: [
    'timestamp', 'request_id', 'task_id', 'semantic_family_id', 'annotator_id', 'batch_id',
    'meaning_correct', 'typeable_romanization', 'skipped', 'instructions_version', 'terms_version', 'client_time'
  ],
  Annotators: ['annotator_id', 'token_sha256', 'active', 'batches', 'max_tasks', 'note'],
  Assignments: [
    'assignment_id', 'task_id', 'semantic_family_id', 'annotator_id', 'batch_id',
    'status', 'leased_at', 'expires_at'
  ],
};

function doGet(e) {
  let result;
  try {
    const params = (e && e.parameter) || {};
    const action = clean_(params.action) || 'next';
    if (action === 'ping') result = { ok: true, pong: true, server_time: new Date().toISOString() };
    else if (action === 'resolve') result = resolveIdentity_(params);
    else if (action === 'next') result = nextTasks_(params);
    else result = { ok: false, error: 'Unsupported GET action' };
  } catch (error) {
    result = { ok: false, error: String(error && error.message || error) };
  }

  const prefix = clean_(e && e.parameter && e.parameter.prefix);
  if (prefix) return jsonp_(prefix, result);
  return json_(result);
}

function doPost(e) {
  try {
    const payload = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (payload.action !== 'submit') return json_({ ok: false, error: 'Unsupported POST action' });
    return json_(submitAnnotation_(payload));
  } catch (error) {
    return json_({ ok: false, error: String(error && error.message || error) });
  }
}

function setupAnnotationSheets() {
  const ss = SpreadsheetApp.getActive();
  Object.keys(HEADERS).forEach((name) => {
    let sheet = ss.getSheetByName(name);
    if (!sheet) sheet = ss.insertSheet(name);
    const headers = HEADERS[name];
    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
      sheet.setFrozenRows(1);
      sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    } else {
      const current = sheet.getRange(1, 1, 1, headers.length).getValues()[0];
      if (headers.some((header, index) => current[index] !== header)) {
        throw new Error(`${name} headers do not match the expected schema.`);
      }
    }
  });
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('RomanBench')
    .addItem('Set up annotation sheets', 'setupAnnotationSheets')
    .addItem('Create pilot annotators', 'createPilotAnnotators')
    .addToUi();
}

function createAnnotator(annotatorId, siteUrl, batches, maxTasks) {
  setupAnnotationSheets();
  annotatorId = clean_(annotatorId);
  if (!annotatorId) throw new Error('annotatorId is required');

  const token = Utilities.getUuid().replace(/-/g, '') + Utilities.getUuid().replace(/-/g, '');
  const tokenHash = sha256_(token);
  const ss = SpreadsheetApp.getActive();
  const sheet = requireSheet_(ss, SHEETS.ANNOTATORS);
  const rows = rowsAsObjects_(sheet);
  const existing = rows.find((row) => clean_(row.annotator_id) === annotatorId);
  const requestedMax = clean_(maxTasks);
  const effectiveMax = requestedMax || (existing ? existing.max_tasks : '');
  const note = `access_token=${token}`;

  if (existing) {
    sheet.getRange(existing.__row, 2, 1, 5).setValues([[
      tokenHash,
      true,
      batches || '',
      effectiveMax,
      note
    ]]);
  } else {
    sheet.appendRow([annotatorId, tokenHash, true, batches || '', effectiveMax, note]);
  }

  const base = String(siteUrl || '').replace(/\/$/, '');
  const firstBatch = String(batches || 'default').split(',')[0].trim() || 'default';
  const url = `${base}/?annotator=${encodeURIComponent(annotatorId)}&token=${encodeURIComponent(token)}&batch=${encodeURIComponent(firstBatch)}`;
  console.log(`${annotatorId} token: ${token}`);
  console.log(`${annotatorId} legacy URL: ${url}`);
  return token;
}

function createVishwanathAnnotator() {
  return createAnnotator('vishwanath', SITE_URL, 'pilot-v1');
}

function createSharathAnnotator() {
  return createAnnotator('sharath', SITE_URL, 'pilot-v1');
}

function createPilotAnnotators() {
  const vishwanath = createVishwanathAnnotator();
  const sharath = createSharathAnnotator();
  return { vishwanath, sharath };
}

function resolveIdentity_(params) {
  const token = clean_(params.token);
  if (!token) throw new Error('Enter your annotator token');

  const ss = SpreadsheetApp.getActive();
  const sheet = requireSheet_(ss, SHEETS.ANNOTATORS);
  const tokenHash = sha256_(token);
  const row = rowsAsObjects_(sheet).find((candidate) => (
    truthy_(candidate.active) && clean_(candidate.token_sha256) === tokenHash
  ));
  if (!row) throw new Error('Invalid or inactive annotator token');

  const requestedBatch = clean_(params.batch);
  const allowed = clean_(row.batches);
  const allowedBatches = allowed
    ? allowed.split(',').map((value) => value.trim()).filter(Boolean)
    : [];

  if (requestedBatch && allowedBatches.length && !allowedBatches.includes(requestedBatch)) {
    throw new Error('Annotator is not assigned to this batch');
  }

  return {
    ok: true,
    annotator: clean_(row.annotator_id),
    batch: requestedBatch || allowedBatches[0] || 'default',
  };
}

function nextTasks_(params) {
  const annotatorId = clean_(params.annotator);
  const token = clean_(params.token);
  const requestedBatch = clean_(params.batch) || 'default';
  const clientId = clean_(params.client_id);
  if (!clientId) throw new Error('Missing browser session id. Hard-refresh this annotation page.');
  const clientKey = clientLeaseKey_(clientId);
  const requestedCount = Math.max(
    1,
    Math.min(MAX_BUNDLE_SIZE, Math.floor(numberOr_(params.count, DEFAULT_BUNDLE_SIZE)))
  );

  const ss = SpreadsheetApp.getActive();
  const annotator = authenticate_(ss, annotatorId, token, requestedBatch);
  const tasks = tasksForBatch_(ss, requestedBatch);
  const taskById = {};
  tasks.forEach((task) => {
    const taskId = clean_(task.task_id);
    if (taskId) taskById[taskId] = task;
  });

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const annotationSheet = requireSheet_(ss, SHEETS.ANNOTATIONS);
    const assignmentSheet = requireSheet_(ss, SHEETS.ASSIGNMENTS);
    const annotations = rowsAsObjects_(annotationSheet);
    const assignments = rowsAsObjects_(assignmentSheet);
    const now = Date.now();

    const annotationKeys = new Set();
    annotations.forEach((row) => {
      const rowBatch = clean_(row.batch_id) || 'default';
      if (rowBatch !== requestedBatch) return;
      const rowAnnotator = clean_(row.annotator_id);
      const taskId = clean_(row.task_id);
      if (rowAnnotator && taskId) annotationKeys.add(`${rowAnnotator}|${taskId}|${rowBatch}`);
    });

    const mine = annotations.filter((row) => (
      clean_(row.annotator_id) === annotatorId
      && (clean_(row.batch_id) || 'default') === requestedBatch
    ));
    const seenFamilies = new Set(mine.map((row) => clean_(row.semantic_family_id)).filter(Boolean));
    const completedTasks = mine.filter((row) => !truthy_(row.skipped)).length;
    const maxTasks = numberOr_(annotator.max_tasks, 0);

    const activeAssignments = assignments.filter((row) => {
      if (clean_(row.status).toLowerCase() !== 'leased') return false;
      if ((clean_(row.batch_id) || 'default') !== requestedBatch) return false;
      if (dateMs_(row.expires_at) <= now) return false;

      const taskId = clean_(row.task_id);
      const task = taskById[taskId];
      if (!task || !truthy_(task.active)) return false;

      const rowAnnotator = clean_(row.annotator_id);
      return !annotationKeys.has(`${rowAnnotator}|${taskId}|${requestedBatch}`);
    });

    const mineLeases = activeAssignments
      .filter((row) => clean_(row.annotator_id) === annotatorId)
      .sort((a, b) => dateMs_(a.leased_at) - dateMs_(b.leased_at));

    // Leases created before browser-scoped leasing have plain UUID assignment IDs.
    // The first refreshed browser to contact the backend claims those legacy leases.
    mineLeases.forEach((row) => {
      if (assignmentClientKey_(row.assignment_id)) return;
      const legacyId = clean_(row.assignment_id) || Utilities.getUuid();
      const claimedId = makeClientAssignmentId_(clientKey, legacyId);
      assignmentSheet.getRange(row.__row, 1).setValue(claimedId);
      row.assignment_id = claimedId;
    });

    const clientLeases = mineLeases.filter((row) => assignmentClientKey_(row.assignment_id) === clientKey);

    // Families leased by this annotator on any browser remain reserved for the annotator,
    // but only leases belonging to this browser are re-served to this browser.
    mineLeases.forEach((row) => {
      const familyId = clean_(row.semantic_family_id);
      if (familyId) seenFamilies.add(familyId);
    });

    const voteCounts = {};
    annotations.forEach((row) => {
      if ((clean_(row.batch_id) || 'default') !== requestedBatch) return;
      if (truthy_(row.skipped)) return;
      const taskId = clean_(row.task_id);
      if (taskId) voteCounts[taskId] = (voteCounts[taskId] || 0) + 1;
    });

    const leaseCounts = {};
    activeAssignments.forEach((row) => {
      const taskId = clean_(row.task_id);
      if (taskId) leaseCounts[taskId] = (leaseCounts[taskId] || 0) + 1;
    });

    const responseTasks = [];
    const responseTaskIds = new Set();
    clientLeases.forEach((lease) => {
      if (responseTasks.length >= requestedCount) return;
      const taskId = clean_(lease.task_id);
      const task = taskById[taskId];
      if (!task || responseTaskIds.has(taskId)) return;
      responseTasks.push(publicTask_(task));
      responseTaskIds.add(taskId);
    });

    const capacityForNew = maxTasks > 0
      ? Math.max(0, maxTasks - completedTasks - mineLeases.length)
      : requestedCount;
    const neededNew = Math.max(0, Math.min(requestedCount - responseTasks.length, capacityForNew));

    const reservedFamilies = new Set(seenFamilies);
    const eligible = tasks.filter((task) => {
      const taskId = clean_(task.task_id);
      const familyId = clean_(task.semantic_family_id);
      const author = clean_(task.source_author_id);
      const target = Math.max(1, numberOr_(task.target_votes, 2));
      const effectiveVotes = (voteCounts[taskId] || 0) + (leaseCounts[taskId] || 0);

      return taskId && familyId
        && truthy_(task.active)
        && !reservedFamilies.has(familyId)
        && (!author || author !== annotatorId)
        && effectiveVotes < target;
    });

    eligible.sort((a, b) => {
      const aId = clean_(a.task_id);
      const bId = clean_(b.task_id);
      const av = (voteCounts[aId] || 0) + (leaseCounts[aId] || 0);
      const bv = (voteCounts[bId] || 0) + (leaseCounts[bId] || 0);
      if (av !== bv) return av - bv;
      return stableScore_(annotatorId + '|' + aId) - stableScore_(annotatorId + '|' + bId);
    });

    const newAssignments = [];
    const leasedAt = new Date(now);
    const expiresAt = new Date(now + LEASE_TTL_MS);

    for (const task of eligible) {
      if (newAssignments.length >= neededNew) break;
      const taskId = clean_(task.task_id);
      const familyId = clean_(task.semantic_family_id);
      if (reservedFamilies.has(familyId)) continue;

      const target = Math.max(1, numberOr_(task.target_votes, 2));
      const effectiveVotes = (voteCounts[taskId] || 0) + (leaseCounts[taskId] || 0);
      if (effectiveVotes >= target) continue;

      newAssignments.push([
        makeClientAssignmentId_(clientKey),
        taskId,
        familyId,
        annotatorId,
        requestedBatch,
        'leased',
        leasedAt,
        expiresAt,
      ]);
      leaseCounts[taskId] = (leaseCounts[taskId] || 0) + 1;
      reservedFamilies.add(familyId);
      responseTasks.push(publicTask_(task));
      responseTaskIds.add(taskId);
    }

    if (newAssignments.length) {
      assignmentSheet
        .getRange(assignmentSheet.getLastRow() + 1, 1, newAssignments.length, HEADERS.Assignments.length)
        .setValues(newAssignments);
    }

    const remainingFamilies = new Set(
      eligible
        .map((task) => clean_(task.semantic_family_id))
        .filter((familyId) => familyId && !reservedFamilies.has(familyId))
    ).size;
    const totalForAnnotator = maxTasks > 0
      ? maxTasks
      : completedTasks + mineLeases.length + newAssignments.length + remainingFamilies;
    const annotatorDone = maxTasks > 0
      ? completedTasks >= maxTasks
      : responseTasks.length === 0 && mineLeases.length === 0 && remainingFamilies === 0;

    return {
      ok: true,
      done: annotatorDone,
      tasks: responseTasks,
      task: responseTasks[0] || null,
      lease_seconds: Math.floor(LEASE_TTL_MS / 1000),
      progress: {
        completed: completedTasks,
        total: Math.max(completedTasks, totalForAnnotator),
        buffered: responseTasks.length,
      },
    };
  } finally {
    lock.releaseLock();
  }
}

function submitAnnotation_(payload) {
  const annotatorId = clean_(payload.annotator);
  const token = clean_(payload.token);
  const batch = clean_(payload.batch) || 'default';
  const ss = SpreadsheetApp.getActive();
  authenticate_(ss, annotatorId, token, batch);

  const requestId = clean_(payload.request_id);
  const taskId = clean_(payload.task_id);
  const familyId = clean_(payload.semantic_family_id);
  if (!requestId || !taskId || !familyId) {
    throw new Error('Missing request_id, task_id, or semantic_family_id');
  }

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const annotationSheet = requireSheet_(ss, SHEETS.ANNOTATIONS);
    const assignmentSheet = requireSheet_(ss, SHEETS.ASSIGNMENTS);
    const annotations = rowsAsObjects_(annotationSheet);
    const assignments = rowsAsObjects_(assignmentSheet);

    const duplicateRequest = annotations.find((row) => clean_(row.request_id) === requestId);
    if (duplicateRequest) {
      settleAssignment_(assignmentSheet, assignments, annotatorId, taskId, batch, truthy_(duplicateRequest.skipped));
      return { ok: true, duplicate: true };
    }

    const duplicateFamily = annotations.find((row) => (
      clean_(row.annotator_id) === annotatorId
      && clean_(row.semantic_family_id) === familyId
      && (clean_(row.batch_id) || 'default') === batch
    ));
    if (duplicateFamily) {
      settleAssignment_(assignmentSheet, assignments, annotatorId, taskId, batch, truthy_(duplicateFamily.skipped));
      return { ok: true, duplicate_family: true };
    }

    const taskSheet = requireSheet_(ss, SHEETS.TASKS);
    const task = rowsAsObjects_(taskSheet).find((row) => (
      clean_(row.task_id) === taskId
      && clean_(row.semantic_family_id) === familyId
      && (clean_(row.batch_id) || 'default') === batch
    ));
    if (!task || !truthy_(task.active)) throw new Error('Task is missing or inactive');
    if (clean_(task.source_author_id) && clean_(task.source_author_id) === annotatorId) {
      throw new Error('Annotator cannot judge a family they authored');
    }

    const skipped = Boolean(payload.skipped);
    const meaning = clean_(payload.meaning_correct).toLowerCase();
    let typing = clean_(payload.typeable_romanization).toLowerCase();
    if (!skipped && !['yes', 'no'].includes(meaning)) {
      throw new Error('meaning_correct must be yes or no');
    }
    if (!skipped && meaning === 'yes' && !['yes', 'no'].includes(typing)) {
      throw new Error('typeable_romanization must be yes or no when meaning_correct=yes');
    }
    if (skipped || meaning !== 'yes') typing = '';

    annotationSheet.getRange(annotationSheet.getLastRow() + 1, 1, 1, HEADERS.Annotations.length).setValues([[
      new Date(), requestId, taskId, familyId, annotatorId, batch,
      skipped ? '' : meaning,
      typing,
      skipped,
      clean_(payload.instructions_version),
      VALIDATION_TERMS_VERSION,
      clean_(payload.client_time),
    ]]);

    settleAssignment_(assignmentSheet, assignments, annotatorId, taskId, batch, skipped);
    return { ok: true };
  } finally {
    lock.releaseLock();
  }
}

function settleAssignment_(sheet, assignments, annotatorId, taskId, batch, skipped) {
  const match = assignments.find((row) => (
    clean_(row.annotator_id) === annotatorId
    && clean_(row.task_id) === taskId
    && (clean_(row.batch_id) || 'default') === batch
    && clean_(row.status).toLowerCase() === 'leased'
  ));
  if (!match) return;
  sheet.getRange(match.__row, 6).setValue(skipped ? 'skipped' : 'submitted');
}

function authenticate_(ss, annotatorId, token, requestedBatch) {
  if (!annotatorId || !token) throw new Error('Missing annotator credentials');
  const sheet = requireSheet_(ss, SHEETS.ANNOTATORS);
  const row = rowsAsObjects_(sheet).find((candidate) => clean_(candidate.annotator_id) === annotatorId);
  if (!row || !truthy_(row.active)) throw new Error('Unknown or inactive annotator');
  if (clean_(row.token_sha256) !== sha256_(token)) throw new Error('Invalid annotation token');

  const allowed = clean_(row.batches);
  if (allowed) {
    const allowedBatches = new Set(allowed.split(',').map((value) => value.trim()).filter(Boolean));
    if (!allowedBatches.has(requestedBatch)) throw new Error('Annotator is not assigned to this batch');
  }
  return row;
}

function tasksForBatch_(ss, batch) {
  const cache = CacheService.getScriptCache();
  const key = `romanbench:tasks:${batch}`;
  const cached = cache.get(key);
  if (cached) {
    try {
      const rows = JSON.parse(cached);
      if (Array.isArray(rows)) return rows;
    } catch (_) {
      cache.remove(key);
    }
  }

  const sheet = requireSheet_(ss, SHEETS.TASKS);
  const rows = rowsAsObjects_(sheet).filter((row) => (
    (clean_(row.batch_id) || 'default') === batch
  ));
  try {
    cache.put(key, JSON.stringify(rows.map(stripRowMetadata_)), TASK_CACHE_SECONDS);
  } catch (_) {
    // Cache is only a latency optimization. Sheet reads remain authoritative.
  }
  return rows;
}

function stripRowMetadata_(row) {
  const result = {};
  Object.keys(row).forEach((key) => {
    if (key !== '__row') result[key] = row[key];
  });
  return result;
}

function publicTask_(task) {
  return {
    task_id: clean_(task.task_id),
    semantic_family_id: clean_(task.semantic_family_id),
    kannada: String(task.kannada || ''),
    roman: String(task.roman || ''),
  };
}

function requireSheet_(ss, name) {
  const sheet = ss.getSheetByName(name);
  if (!sheet) {
    throw new Error(`Missing ${name} sheet. Run setupAnnotationSheets() once from the Apps Script editor.`);
  }
  return sheet;
}

function rowsAsObjects_(sheet) {
  if (!sheet || sheet.getLastRow() < 2) return [];
  const values = sheet.getDataRange().getValues();
  const headers = values[0].map(String);
  return values.slice(1).map((row, index) => {
    const result = { __row: index + 2 };
    headers.forEach((header, column) => result[header] = row[column]);
    return result;
  });
}

function json_(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}

function jsonp_(prefix, value) {
  if (!/^[A-Za-z_$][0-9A-Za-z_$]{0,80}$/.test(prefix)) {
    return ContentService
      .createTextOutput('throw new Error("Invalid JSONP callback");')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService
    .createTextOutput(`${prefix}(${JSON.stringify(value)});`)
    .setMimeType(ContentService.MimeType.JAVASCRIPT);
}

function clean_(value) {
  return value === null || value === undefined ? '' : String(value).trim();
}

function numberOr_(value, fallback) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function truthy_(value) {
  if (value === true || value === 1) return true;
  return ['true', 'yes', '1', 'y'].includes(clean_(value).toLowerCase());
}

function dateMs_(value) {
  if (value instanceof Date) return value.getTime();
  const parsed = Date.parse(String(value || ''));
  return Number.isFinite(parsed) ? parsed : 0;
}

function sha256_(value) {
  const bytes = Utilities.computeDigest(
    Utilities.DigestAlgorithm.SHA_256,
    String(value),
    Utilities.Charset.UTF_8
  );
  return bytes.map((byte) => ('0' + ((byte < 0 ? byte + 256 : byte).toString(16))).slice(-2)).join('');
}

function clientLeaseKey_(clientId) {
  return sha256_(clientId).slice(0, 16);
}

function assignmentClientKey_(assignmentId) {
  const match = clean_(assignmentId).match(/^c:([0-9a-f]{16}):/);
  return match ? match[1] : '';
}

function makeClientAssignmentId_(clientKey, suffix) {
  return `c:${clientKey}:${clean_(suffix) || Utilities.getUuid()}`;
}

function stableScore_(value) {
  const digest = Utilities.computeDigest(
    Utilities.DigestAlgorithm.MD5,
    String(value),
    Utilities.Charset.UTF_8
  );
  return digest.slice(0, 4).reduce((score, byte) => (
    score * 257 + (byte < 0 ? byte + 256 : byte)
  ), 0);
}
