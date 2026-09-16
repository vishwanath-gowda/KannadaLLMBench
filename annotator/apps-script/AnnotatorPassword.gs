const ACCESS_TOKEN_PREFIX = 'access_token=';

/**
 * Keep token_sha256 synchronized when an organizer manually edits the
 * access_token=... value in the Annotators sheet.
 *
 * Example note cell:
 *   access_token=sharath123
 *
 * The existing backend continues authenticating with token_sha256, so the
 * plaintext password is only read when the organizer edits the Sheet.
 */
function onEdit(e) {
  if (!e || !e.range) return;

  const range = e.range;
  const sheet = range.getSheet();
  if (sheet.getName() !== SHEETS.ANNOTATORS) return;
  if (range.getRow() <= 1) return;

  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0].map(String);
  const noteColumn = headers.indexOf('note') + 1;
  const hashColumn = headers.indexOf('token_sha256') + 1;
  if (!noteColumn || !hashColumn) return;
  if (range.getColumn() !== noteColumn || range.getNumColumns() !== 1 || range.getNumRows() !== 1) return;

  const password = accessTokenFromNote_(range.getValue());
  if (!password) return;

  sheet.getRange(range.getRow(), hashColumn).setValue(sha256_(password));
}

/**
 * Preferred programmatic way to set/change an annotator password.
 * Updates both the plaintext organizer note and the authentication hash.
 */
function setAnnotatorPassword(annotatorId, password) {
  annotatorId = clean_(annotatorId);
  password = clean_(password);
  if (!annotatorId) throw new Error('annotatorId is required');
  if (!password) throw new Error('password is required');

  const ss = SpreadsheetApp.getActive();
  const sheet = requireSheet_(ss, SHEETS.ANNOTATORS);
  const row = rowsAsObjects_(sheet).find((candidate) => clean_(candidate.annotator_id) === annotatorId);
  if (!row) throw new Error(`Unknown annotator: ${annotatorId}`);

  sheet.getRange(row.__row, 2).setValue(sha256_(password));
  sheet.getRange(row.__row, 6).setValue(`${ACCESS_TOKEN_PREFIX}${password}`);
  SpreadsheetApp.flush();
  return password;
}

function accessTokenFromNote_(value) {
  const note = String(value === null || value === undefined ? '' : value);
  if (!note.startsWith(ACCESS_TOKEN_PREFIX)) return '';
  return note.slice(ACCESS_TOKEN_PREFIX.length).trim();
}
