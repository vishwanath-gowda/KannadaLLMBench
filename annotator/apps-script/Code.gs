const SHEETS = {
  TASKS: 'Tasks',
  ANNOTATIONS: 'Annotations',
  ANNOTATORS: 'Annotators',
};

const VALIDATION_TERMS_VERSION = 'romanbench-validation-v1';

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
};

function doGet(e) {
  let result;
  try {
    const action = clean_(e && e.parameter && e.parameter.action) || 'next';
    if (action !== 'next') result = { ok: false, error: 'Unsupported GET action' };
    else result = nextTask_(e.parameter);
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
    .addToUi();
}

/**
 * Run from the Apps Script editor to create or rotate an annotator token.
 * The plaintext token is returned/logged once; only its SHA-256 hash is stored.
 *
 * Example:
 * createAnnotator('KN001', 'https://YOUR_GITHUB_USER.github.io/KannadaLLMBench/', 'pilot')
 */
function createAnnotator(annotatorId, siteUrl, batches) {
  setupAnnotationSheets();
  annotatorId = clean_(annotatorId);
  if (!annotatorId) throw new Error('annotatorId is required');
  const token = Utilities.getUuid().replace(/-/g, '') + Utilities.getUuid().replace(/-/g, '');
  const tokenHash = sha256_(token);
  const sheet = SpreadsheetApp.getActive().getSheetByName(SHEETS.ANNOTATORS);
  const rows = rowsAsObjects_(sheet);
  const existing = rows.find((row) => clean_(row.annotator_id) === annotatorId);
  if (existing) {
    sheet.getRange(existing.__row, 2, 1, 5).setValues([[tokenHash, true, batches || '', '', 'token rotated']]);
  } else {
    sheet.appendRow([annotatorId, tokenHash, true, batches || '', '', '']);
  }
  const base = String(siteUrl || '').replace(/\/$/, '');
  const firstBatch = String(batches || 'default').split(',')[0].trim() || 'default';
  const url = `${base}/?annotator=${encodeURIComponent(annotatorId)}&token=${encodeURIComponent(token)}&batch=${encodeURIComponent(firstBatch)}`;
  console.log(url);
  return url;
}

function nextTask_(params) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    setupAnnotationSheets();
    const annotatorId = clean_(params.annotator);
    const token = clean_(params.token);
    const requestedBatch = clean_(params.batch) || 'default';
    const annotator = authenticate_(annotatorId, token, requestedBatch);

    const taskSheet = SpreadsheetApp.getActive().getSheetByName(SHEETS.TASKS);
    const annotationSheet = SpreadsheetApp.getActive().getSheetByName(SHEETS.ANNOTATIONS);
    const tasks = rowsAsObjects_(taskSheet);
    const annotations = rowsAsObjects_(annotationSheet);

    const mine = annotations.filter((row) => clean_(row.annotator_id) === annotatorId);
    const seenFamilies = new Set(mine.map((row) => clean_(row.semantic_family_id)).filter(Boolean));
    const completedTasks = mine.filter((row) => !truthy_(row.skipped)).length;
    const maxTasks = numberOr_(annotator.max_tasks, 0);
    if (maxTasks > 0 && completedTasks >= maxTasks) {
      return { ok: true, done: true, progress: { completed: completedTasks, total: maxTasks } };
    }

    const voteCounts = {};
    annotations.forEach((row) => {
      if (truthy_(row.skipped)) return;
      const taskId = clean_(row.task_id);
      if (taskId) voteCounts[taskId] = (voteCounts[taskId] || 0) + 1;
    });

    const eligible = tasks.filter((task) => {
      const taskId = clean_(task.task_id);
      const familyId = clean_(task.semantic_family_id);
      const batch = clean_(task.batch_id) || 'default';
      const author = clean_(task.source_author_id);
      const target = Math.max(1, numberOr_(task.target_votes, 2));
      return taskId && familyId
        && truthy_(task.active)
        && batch === requestedBatch
        && !seenFamilies.has(familyId)
        && (!author || author !== annotatorId)
        && (voteCounts[taskId] || 0) < target;
    });

    eligible.sort((a, b) => {
      const av = voteCounts[clean_(a.task_id)] || 0;
      const bv = voteCounts[clean_(b.task_id)] || 0;
      if (av !== bv) return av - bv;
      return stableScore_(annotatorId + '|' + clean_(a.task_id)) - stableScore_(annotatorId + '|' + clean_(b.task_id));
    });

    if (!eligible.length) {
      return { ok: true, done: true, progress: { completed: completedTasks, total: completedTasks } };
    }

    const task = eligible[0];
    const totalForAnnotator = maxTasks > 0 ? maxTasks : completedTasks + eligible.length;
    return {
      ok: true,
      done: false,
      task: {
        task_id: clean_(task.task_id),
        semantic_family_id: clean_(task.semantic_family_id),
        kannada: String(task.kannada || ''),
        roman: String(task.roman || ''),
      },
      progress: { completed: completedTasks, total: totalForAnnotator },
    };
  } finally {
    lock.releaseLock();
  }
}

function submitAnnotation_(payload) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    setupAnnotationSheets();
    const annotatorId = clean_(payload.annotator);
    const token = clean_(payload.token);
    const batch = clean_(payload.batch) || 'default';
    authenticate_(annotatorId, token, batch);

    const requestId = clean_(payload.request_id);
    const taskId = clean_(payload.task_id);
    const familyId = clean_(payload.semantic_family_id);
    if (!requestId || !taskId || !familyId) throw new Error('Missing request_id, task_id, or semantic_family_id');

    const annotationSheet = SpreadsheetApp.getActive().getSheetByName(SHEETS.ANNOTATIONS);
    const annotations = rowsAsObjects_(annotationSheet);
    const duplicateRequest = annotations.find((row) => clean_(row.request_id) === requestId);
    if (duplicateRequest) return { ok: true, duplicate: true };
    const duplicateFamily = annotations.find((row) => clean_(row.annotator_id) === annotatorId && clean_(row.semantic_family_id) === familyId);
    if (duplicateFamily) return { ok: true, duplicate_family: true };

    const taskSheet = SpreadsheetApp.getActive().getSheetByName(SHEETS.TASKS);
    const task = rowsAsObjects_(taskSheet).find((row) => clean_(row.task_id) === taskId && clean_(row.semantic_family_id) === familyId);
    if (!task || !truthy_(task.active)) throw new Error('Task is missing or inactive');
    if ((clean_(task.batch_id) || 'default') !== batch) throw new Error('Task is not in this batch');
    if (clean_(task.source_author_id) && clean_(task.source_author_id) === annotatorId) {
      throw new Error('Annotator cannot judge a family they authored');
    }

    const skipped = Boolean(payload.skipped);
    const meaning = clean_(payload.meaning_correct).toLowerCase();
    const typing = clean_(payload.typeable_romanization).toLowerCase();
    if (!skipped && !['yes', 'no'].includes(meaning)) throw new Error('meaning_correct must be yes or no');
    if (!skipped && !['yes', 'no'].includes(typing)) throw new Error('typeable_romanization must be yes or no');

    annotationSheet.appendRow([
      new Date(), requestId, taskId, familyId, annotatorId, batch,
      skipped ? '' : meaning,
      skipped ? '' : typing,
      skipped,
      clean_(payload.instructions_version),
      VALIDATION_TERMS_VERSION,
      clean_(payload.client_time),
    ]);
    return { ok: true };
  } finally {
    lock.releaseLock();
  }
}

function authenticate_(annotatorId, token, requestedBatch) {
  if (!annotatorId || !token) throw new Error('Missing annotator credentials');
  const sheet = SpreadsheetApp.getActive().getSheetByName(SHEETS.ANNOTATORS);
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

function sha256_(value) {
  const bytes = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, String(value), Utilities.Charset.UTF_8);
  return bytes.map((byte) => ('0' + ((byte < 0 ? byte + 256 : byte).toString(16))).slice(-2)).join('');
}

function stableScore_(value) {
  const digest = Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, String(value), Utilities.Charset.UTF_8);
  return digest.slice(0, 4).reduce((score, byte) => score * 257 + (byte < 0 ? byte + 256 : byte), 0);
}
