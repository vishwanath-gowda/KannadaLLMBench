const PILOT100_BATCH = 'pilot-100-v1';
const PILOT100_SOURCE_ID = 'romanbench-pilot-100-v1';
const PILOT100_VARIANTS = ['ascii_relaxed', 'ascii_phonemic', 'iast'];

const PILOT100_SEED_TEXT = `
ನಾನು ಇವತ್ತು ಕೆಲಸ ಮುಗಿಸಿ ಬೇಗ ಮನೆಗೆ ಹೋಗಬೇಕು.
ನಾಳೆ ಬೆಳಿಗ್ಗೆ ಎಂಟು ಗಂಟೆಗೆ ನನ್ನನ್ನು ಎಬ್ಬಿಸು.
ಮಳೆ ಬರುತ್ತಿದೆ ಆದ್ದರಿಂದ ಹೊರಗೆ ಹೋಗುವಾಗ ಛತ್ರಿ ತೆಗೆದುಕೊಂಡು ಹೋಗು.
ಅಮ್ಮ ಇಂದು ಸಂಜೆ ತರಕಾರಿ ತರಲು ಮಾರುಕಟ್ಟೆಗೆ ಹೋಗುತ್ತಾರೆ.
ಮಗುವಿಗೆ ಹಾಲು ಕೊಟ್ಟ ನಂತರ ಸ್ವಲ್ಪ ನೀರು ಕೊಡು.
ನಾವು ವಾರಾಂತ್ಯದಲ್ಲಿ ಹತ್ತಿರದ ಉದ್ಯಾನವನಕ್ಕೆ ಹೋಗೋಣ.
ಈ ರಸ್ತೆಯಲ್ಲಿ ಸಂಜೆ ಸಮಯದಲ್ಲಿ ತುಂಬಾ ವಾಹನ ಸಂಚಾರ ಇರುತ್ತದೆ.
ದಯವಿಟ್ಟು ಬಾಗಿಲು ಮುಚ್ಚಿ ಕೀಲಿಯನ್ನು ಮೇಜಿನ ಮೇಲೆ ಇಡು.
ನನಗೆ ಈ ಊಟ ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಖಾರವಾಗಿದೆ.
ಅವನು ಇನ್ನೂ ಮನೆಗೆ ಬಂದಿಲ್ಲ ಎಂದು ಅಪ್ಪ ಹೇಳಿದರು.
ನೀನು ನಾಳೆ ಸಭೆಗೆ ಎಷ್ಟು ಗಂಟೆಗೆ ಬರುತ್ತೀಯ?
ನಾನು ಕಾಫಿ ಕುಡಿಯುವ ಮೊದಲು ಸ್ವಲ್ಪ ನೀರು ಕುಡಿಯುತ್ತೇನೆ.
ಇಂದು ರಾತ್ರಿ ಊಟಕ್ಕೆ ಏನು ಮಾಡೋಣ ಎಂದು ಯೋಚಿಸಿದ್ದೀಯ?
ಬಸ್ ಬರಲು ಇನ್ನೂ ಹತ್ತು ನಿಮಿಷ ಬೇಕಾಗಬಹುದು.
ಈ ಅಂಗಡಿಯಲ್ಲಿ ಹಣ್ಣುಗಳು ತುಂಬಾ ತಾಜಾಗಿವೆ.
ಮನೆಯ ಮುಂದೆ ಕಾರನ್ನು ನಿಲ್ಲಿಸಬೇಡ ಎಂದು ಅವರು ಹೇಳಿದರು.
ನನಗೆ ಸಮಯ ಸಿಕ್ಕರೆ ಸಂಜೆ ನಡೆದುಕೊಂಡು ಬರುತ್ತೇನೆ.
ಅವಳು ಪುಸ್ತಕವನ್ನು ಓದಿ ಮುಗಿಸಿ ನನಗೆ ಕೊಟ್ಟಳು.
ದಯವಿಟ್ಟು ಫೋನ್ ಅನ್ನು ಮೌನ ಸ್ಥಿತಿಗೆ ಇಡು.
ನಾವು ಹೊರಡುವ ಮೊದಲು ಎಲ್ಲಾ ಕಿಟಕಿಗಳನ್ನು ಮುಚ್ಚಬೇಕು.
ಮಗು ಮಧ್ಯಾಹ್ನ ಎರಡು ಗಂಟೆಗೆ ಮಲಗಿತು.
ನನ್ನ ಚೀಲವನ್ನು ಕಾರಿನ ಹಿಂಭಾಗದಲ್ಲಿ ಇಟ್ಟಿದ್ದೇನೆ.
ಇವತ್ತು ಹವಾಮಾನ ಚೆನ್ನಾಗಿದೆ ಹೊರಗೆ ಸ್ವಲ್ಪ ನಡೆಯೋಣ.
ಅಂಗಡಿಗೆ ಹೋಗುವಾಗ ಹಾಲು ಮತ್ತು ಮೊಸರು ತಂದುಕೊಡು.
ಈ ಕೆಲಸ ಮುಗಿಸಲು ನನಗೆ ಇನ್ನೊಂದು ಗಂಟೆ ಬೇಕು.
ನೀನು ಮನೆಗೆ ಬಂದ ಮೇಲೆ ನನಗೆ ಸಂದೇಶ ಕಳುಹಿಸು.
ರೈಲು ನಿಲ್ದಾಣಕ್ಕೆ ಹೋಗಲು ಯಾವ ದಾರಿ ಸುಲಭ?
ಅವನು ಪ್ರತಿದಿನ ಬೆಳಿಗ್ಗೆ ಬೇಗ ಎದ್ದು ವ್ಯಾಯಾಮ ಮಾಡುತ್ತಾನೆ.
ನಮಗೆ ಮುಂದಿನ ವಾರ ವೈದ್ಯರ ಭೇಟಿ ಇದೆ.
ಈ ಕೊಠಡಿಯಲ್ಲಿ ಸ್ವಲ್ಪ ಹೆಚ್ಚು ಚಳಿ ಇದೆ.
ಬಟ್ಟೆಗಳನ್ನು ಒಣಗಲು ಹೊರಗೆ ಹಾಕಿದ್ದೇನೆ.
ಮಳೆ ನಿಂತ ನಂತರ ನಾವು ಹೊರಗೆ ಹೋಗಬಹುದು.
ನಾನು ಇಂದು ಮಧ್ಯಾಹ್ನ ಮನೆಯಿಂದ ಕೆಲಸ ಮಾಡುತ್ತೇನೆ.
ಅವಳು ಮಕ್ಕಳಿಗಾಗಿ ಹಣ್ಣುಗಳನ್ನು ಸಣ್ಣ ತುಂಡುಗಳಾಗಿ ಕತ್ತರಿಸಿದಳು.
ನಿನ್ನ ಬಳಿ ಹೆಚ್ಚುವರಿ ನೀರಿನ ಬಾಟಲಿ ಇದೆಯಾ?
ಕಾರಿಗೆ ಇಂಧನ ತುಂಬಿಸಬೇಕು ಎಂದು ಬೆಳಿಗ್ಗೆ ನೆನಪಾಯಿತು.
ನಾವು ಊಟ ಮಾಡಿದ ನಂತರ ಪಾತ್ರೆಗಳನ್ನು ತೊಳೆಯೋಣ.
ಈ ವಾರಾಂತ್ಯದಲ್ಲಿ ಮನೆ ಸ್ವಚ್ಛಗೊಳಿಸಲು ಸಮಯ ಇಡೋಣ.
ನನಗೆ ಆ ಹಾಡು ಬಹಳ ಇಷ್ಟವಾಗಿದೆ.
ನೀನು ಕಚೇರಿಯಿಂದ ಹೊರಟಾಗ ನನಗೆ ಕರೆ ಮಾಡು.
ಇಂದು ಬೆಳಿಗ್ಗೆ ರಸ್ತೆ ತುಂಬಾ ಖಾಲಿಯಾಗಿತ್ತು.
ಅವನು ತನ್ನ ಕೀಲಿಗಳನ್ನು ಎಲ್ಲೋ ಮರೆತಿದ್ದಾನೆ.
ಮಕ್ಕಳು ಶಾಲೆಯಿಂದ ಬಂದ ನಂತರ ಹೊರಗೆ ಆಡಿದರು.
ನಾನು ನಾಳೆಯ ಪ್ರಯಾಣಕ್ಕಾಗಿ ಚೀಲ ಸಿದ್ಧಪಡಿಸುತ್ತಿದ್ದೇನೆ.
ದಯವಿಟ್ಟು ಈ ದಾಖಲೆಗಳನ್ನು ಒಮ್ಮೆ ಪರಿಶೀಲಿಸು.
ನಮಗೆ ಬೇಕಾದ ಎಲ್ಲಾ ಸಾಮಾನುಗಳನ್ನು ಪಟ್ಟಿಯಲ್ಲಿ ಬರೆದಿದ್ದೇನೆ.
ಅವಳು ಸಂಜೆ ಚಹಾ ಜೊತೆ ಬಿಸ್ಕತ್ತು ತಿಂದಳು.
ಈ ದಾರಿಯಲ್ಲಿ ಹೋದರೆ ಸಮಯ ಸ್ವಲ್ಪ ಉಳಿಯುತ್ತದೆ.
ನೀನು ಬೇಗ ಬಂದರೆ ನಾವು ಒಟ್ಟಿಗೆ ಊಟ ಮಾಡಬಹುದು.
ನಾನು ಹತ್ತು ನಿಮಿಷದಲ್ಲಿ ಕೆಳಗೆ ಬರುತ್ತೇನೆ.
ಮಗುವಿನ ಆಟಿಕೆಗಳು ಎಲ್ಲೆಲ್ಲೂ ಬಿದ್ದಿವೆ.
ಅವರು ಮುಂದಿನ ತಿಂಗಳು ಹೊಸ ಮನೆಗೆ ಸ್ಥಳಾಂತರವಾಗುತ್ತಾರೆ.
ಈ ತರಕಾರಿಯನ್ನು ಬೇಯಿಸಲು ಹೆಚ್ಚು ಸಮಯ ಬೇಕಾಗುವುದಿಲ್ಲ.
ನನಗೆ ಇಂದು ತುಂಬಾ ಕೆಲಸ ಇರುವುದರಿಂದ ತಡವಾಗಬಹುದು.
ನೀನು ಆ ಚಿತ್ರವನ್ನು ನನಗೆ ಮತ್ತೆ ಕಳುಹಿಸಬಹುದಾ?
ನಾವು ಬೆಳಿಗ್ಗೆ ಬೇಗ ಹೊರಟರೆ ಸಂಚಾರ ಕಡಿಮೆ ಇರುತ್ತದೆ.
ಅವಳು ತನ್ನ ಸ್ನೇಹಿತೆಯ ಜೊತೆ ಬಹಳ ಹೊತ್ತು ಮಾತನಾಡಿದಳು.
ಮನೆಯ ಮೇಲ್ಚಾವಣಿಯಲ್ಲಿ ಒಂದು ಸಣ್ಣ ಸೋರಿಕೆ ಇದೆ.
ನಾನು ಅಂಗಡಿಯಿಂದ ಹೊಸ ಬ್ಯಾಟರಿಗಳನ್ನು ತಂದಿದ್ದೇನೆ.
ನಾಳೆ ಮಳೆ ಬಂದರೆ ಪ್ರವಾಸವನ್ನು ಮುಂದೂಡೋಣ.
ಈ ಔಷಧಿಯನ್ನು ಊಟದ ನಂತರ ತೆಗೆದುಕೊಳ್ಳಬೇಕು.
ನನಗೆ ಸ್ವಲ್ಪ ತಲೆನೋವು ಇದೆ ಆದ್ದರಿಂದ ವಿಶ್ರಾಂತಿ ಪಡೆಯುತ್ತೇನೆ.
ಮಗುವಿಗೆ ನಿದ್ರೆ ಬಂದಾಗ ದೀಪವನ್ನು ಮಂದಗೊಳಿಸು.
ನಾವು ಹೊರಗೆ ಹೋಗುವ ಮೊದಲು ಹವಾಮಾನ ನೋಡೋಣ.
ಅವರು ಬೆಳಿಗ್ಗೆ ಒಂಬತ್ತು ಗಂಟೆಗೆ ಕಚೇರಿ ತೆರೆಯುತ್ತಾರೆ.
ನಾನು ನಿನ್ನಿಗಾಗಿ ಬಾಗಿಲಿನ ಬಳಿ ಕಾಯುತ್ತಿದ್ದೇನೆ.
ಈ ಪೆಟ್ಟಿಗೆಯನ್ನು ಮೇಲಿನ ಕೊಠಡಿಯಲ್ಲಿ ಇಡಬೇಕು.
ನೀನು ಸಮಯ ಇದ್ದಾಗ ಈ ಫೈಲ್ ನೋಡಿ ಹೇಳು.
ಇಂದು ರಾತ್ರಿ ಚಂದ್ರ ತುಂಬಾ ಚೆನ್ನಾಗಿ ಕಾಣುತ್ತಾನೆ.
ಅವನು ತನ್ನ ಮಗನನ್ನು ಶಾಲೆಗೆ ಬಿಟ್ಟು ಕಚೇರಿಗೆ ಹೋದನು.
ನಾವು ಭಾನುವಾರ ಬೆಳಿಗ್ಗೆ ದೇವಸ್ಥಾನಕ್ಕೆ ಹೋಗುತ್ತೇವೆ.
ಈ ಶರ್ಟ್ ನನಗೆ ಸ್ವಲ್ಪ ದೊಡ್ಡದಾಗಿದೆ.
ಅವಳು ಹೊಸ ಪಾಕವಿಧಾನ ಪ್ರಯತ್ನಿಸಲು ಬಯಸುತ್ತಿದ್ದಾಳೆ.
ನನಗೆ ಈ ವಿಷಯದ ಬಗ್ಗೆ ಇನ್ನಷ್ಟು ಮಾಹಿತಿ ಬೇಕು.
ದಯವಿಟ್ಟು ನೀರು ಕುದಿದ ಮೇಲೆ ಒಲೆ ಆರಿಸು.
ನೀನು ಕಾರನ್ನು ಹೊರತೆಗೆದ ನಂತರ ಗೇಟ್ ಮುಚ್ಚು.
ನಾವು ಸಂಜೆ ಆರು ಗಂಟೆಗೆ ಅಲ್ಲಿ ತಲುಪಬೇಕು.
ಈ ವಾರ ತರಕಾರಿ ಬೆಲೆ ಸ್ವಲ್ಪ ಹೆಚ್ಚಾಗಿದೆ.
ಅವನು ತನ್ನ ಕೆಲಸವನ್ನು ಸಮಯಕ್ಕೆ ಮುಗಿಸಿದ್ದಾನೆ.
ನಾನು ಹೊಸ ಚಪ್ಪಲಿಯನ್ನು ಇನ್ನೂ ಬಳಸಿಲ್ಲ.
ಮಕ್ಕಳಿಗೆ ರಾತ್ರಿ ಬೇಗ ಮಲಗುವ ಅಭ್ಯಾಸ ಮಾಡಿಸಬೇಕು.
ನಮಗೆ ಹಿಂತಿರುಗುವ ದಾರಿಯಲ್ಲಿ ಪೆಟ್ರೋಲ್ ಹಾಕಿಸಬೇಕು.
ನೀನು ಊಟಕ್ಕೆ ಮುಂಚೆ ಕೈ ತೊಳೆದುಕೋ.
ಅವಳು ಬೆಳಿಗ್ಗೆ ಉಪಹಾರಕ್ಕೆ ದೋಸೆ ಮಾಡಿದ್ದಳು.
ಈ ಕೋಣೆಯಲ್ಲಿ ಬೆಳಕು ಸಾಕಾಗುತ್ತಿಲ್ಲ.
ನಾನು ನಾಳೆ ಮಧ್ಯಾಹ್ನ ಬ್ಯಾಂಕಿಗೆ ಹೋಗಬೇಕು.
ಮಳೆ ಕಾರಣದಿಂದ ಪಂದ್ಯ ಸ್ವಲ್ಪ ತಡವಾಗಿ ಆರಂಭವಾಯಿತು.
ನಮ್ಮ ಮನೆಗೆ ಬರುವ ದಾರಿ ನಿನಗೆ ಗೊತ್ತಿದೆಯಾ?
ಅವನು ಹೊಸ ಕೆಲಸದ ಬಗ್ಗೆ ತುಂಬಾ ಉತ್ಸಾಹದಲ್ಲಿದ್ದಾನೆ.
ನಾನು ವಾರಕ್ಕೆ ಮೂರು ದಿನ ವ್ಯಾಯಾಮ ಮಾಡಲು ಪ್ರಯತ್ನಿಸುತ್ತೇನೆ.
ಈ ಹಣ್ಣು ಇನ್ನೂ ಸ್ವಲ್ಪ ಕಚ್ಚಾಗಿದೆ.
ನೀನು ಹೊರಗೆ ಹೋಗುವಾಗ ಜಾಕೆಟ್ ಹಾಕಿಕೊಳ್ಳು.
ಮಗುವಿನ ಬಟ್ಟೆಗಳನ್ನು ಬೇರೆ ಚೀಲದಲ್ಲಿ ಇಟ್ಟಿದ್ದೇನೆ.
ನಾವು ನಾಳೆ ಬೆಳಿಗ್ಗೆ ಉಪಹಾರ ಹೊರಗೆ ಮಾಡೋಣ.
ಅವಳು ಮನೆಗೆ ಬಂದ ತಕ್ಷಣ ಕೈ ತೊಳೆದಳು.
ನನಗೆ ಈ ಕುರ್ಚಿ ಹೆಚ್ಚು ಆರಾಮವಾಗಿಲ್ಲ.
ಈ ತಿಂಗಳ ವಿದ್ಯುತ್ ಬಿಲ್ ಸ್ವಲ್ಪ ಹೆಚ್ಚಾಗಿದೆ.
ನೀನು ಬಂದಾಗ ಹಳೆಯ ಪುಸ್ತಕಗಳನ್ನು ಕೂಡ ತೆಗೆದುಕೊಂಡು ಬಾ.
ನಾನು ವಾರಾಂತ್ಯಕ್ಕೆ ಕೆಲವು ಸ್ನೇಹಿತರನ್ನು ಮನೆಗೆ ಕರೆದಿದ್ದೇನೆ.
ಅವರು ಊಟ ಮುಗಿಸಿದ ನಂತರ ಸ್ವಲ್ಪ ಹೊತ್ತು ನಡೆದರು.
`.trim();

/**
 * Load a clean 100-family calibration batch and point vishwanath/sharath at it.
 * Existing tokens are preserved. Re-running is allowed only before annotations exist.
 */
function loadPilot100Samples() {
  setupAnnotationSheets();
  const ss = SpreadsheetApp.getActive();
  const controls = PILOT100_SEED_TEXT.split('\n').map((value) => value.trim()).filter(Boolean);
  if (controls.length !== 100 || new Set(controls).size !== 100) {
    throw new Error(`Pilot seed must contain exactly 100 unique controls; found ${controls.length}`);
  }

  const annotationsSheet = requireSheet_(ss, SHEETS.ANNOTATIONS);
  const existingAnnotations = rowsAsObjects_(annotationsSheet).filter((row) => (
    (clean_(row.batch_id) || 'default') === PILOT100_BATCH
  ));
  if (existingAnnotations.length) {
    throw new Error(`${PILOT100_BATCH} already has annotations; refusing to replace a live batch.`);
  }

  const taskSheet = requireSheet_(ss, SHEETS.TASKS);
  const oldTaskRows = rowsAsObjects_(taskSheet)
    .filter((row) => (clean_(row.batch_id) || 'default') === PILOT100_BATCH)
    .map((row) => row.__row)
    .sort((a, b) => b - a);
  oldTaskRows.forEach((rowNumber) => taskSheet.deleteRow(rowNumber));

  const assignmentSheet = requireSheet_(ss, SHEETS.ASSIGNMENTS);
  const oldAssignmentRows = rowsAsObjects_(assignmentSheet)
    .filter((row) => (clean_(row.batch_id) || 'default') === PILOT100_BATCH)
    .map((row) => row.__row)
    .sort((a, b) => b - a);
  oldAssignmentRows.forEach((rowNumber) => assignmentSheet.deleteRow(rowNumber));

  const rows = controls.map((control, index) => {
    const variants = pilot100RomanizationVariants_(control);
    const variantType = PILOT100_VARIANTS[index % PILOT100_VARIANTS.length];
    const familyId = `pilot100-${sha256_(control).slice(0, 12)}`;
    return [
      `${familyId}-${variantType}`,
      familyId,
      control,
      variants[variantType],
      variantType,
      'synthetic_process_calibration',
      PILOT100_SOURCE_ID,
      '',
      PILOT100_BATCH,
      2,
      true,
    ];
  });

  taskSheet.getRange(taskSheet.getLastRow() + 1, 1, rows.length, HEADERS.Tasks.length).setValues(rows);

  const annotatorSheet = requireSheet_(ss, SHEETS.ANNOTATORS);
  const annotators = rowsAsObjects_(annotatorSheet);
  ['vishwanath', 'sharath'].forEach((annotatorId) => {
    const row = annotators.find((candidate) => clean_(candidate.annotator_id) === annotatorId);
    if (!row) return;
    annotatorSheet.getRange(row.__row, 4).setValue(PILOT100_BATCH);
    annotatorSheet.getRange(row.__row, 5).setValue(100);
  });

  CacheService.getScriptCache().remove(`romanbench:tasks:${PILOT100_BATCH}`);
  SpreadsheetApp.flush();
  const result = {
    ok: true,
    batch: PILOT100_BATCH,
    tasks: rows.length,
    target_votes: 2,
    expected_judgments: rows.length * 2,
  };
  console.log(JSON.stringify(result));
  return result;
}

function pilot100RomanizationVariants_(text) {
  const iast = pilot100ToIast_(text);
  const asciiPhonemic = pilot100IastToAscii_(iast);
  let relaxed = asciiPhonemic;
  [['aa', 'a'], ['ii', 'i'], ['uu', 'u'], ['ee', 'e'], ['oo', 'o']].forEach(([source, target]) => {
    relaxed = relaxed.split(source).join(target);
  });
  return {
    iast: pilot100Normalize_(iast),
    ascii_phonemic: pilot100Normalize_(asciiPhonemic),
    ascii_relaxed: pilot100Normalize_(relaxed),
  };
}

function pilot100ToIast_(text) {
  const vowels = {
    'ಅ': 'a', 'ಆ': 'ā', 'ಇ': 'i', 'ಈ': 'ī', 'ಉ': 'u', 'ಊ': 'ū', 'ಋ': 'ṛ', 'ೠ': 'ṝ',
    'ಌ': 'ḷ', 'ೡ': 'ḹ', 'ಎ': 'e', 'ಏ': 'ē', 'ಐ': 'ai', 'ಒ': 'o', 'ಓ': 'ō', 'ಔ': 'au',
  };
  const consonants = {
    'ಕ': 'k', 'ಖ': 'kh', 'ಗ': 'g', 'ಘ': 'gh', 'ಙ': 'ṅ', 'ಚ': 'c', 'ಛ': 'ch', 'ಜ': 'j',
    'ಝ': 'jh', 'ಞ': 'ñ', 'ಟ': 'ṭ', 'ಠ': 'ṭh', 'ಡ': 'ḍ', 'ಢ': 'ḍh', 'ಣ': 'ṇ', 'ತ': 't',
    'ಥ': 'th', 'ದ': 'd', 'ಧ': 'dh', 'ನ': 'n', 'ಪ': 'p', 'ಫ': 'ph', 'ಬ': 'b', 'ಭ': 'bh',
    'ಮ': 'm', 'ಯ': 'y', 'ರ': 'r', 'ಱ': 'ṟ', 'ಲ': 'l', 'ವ': 'v', 'ಶ': 'ś', 'ಷ': 'ṣ',
    'ಸ': 's', 'ಹ': 'h', 'ಳ': 'ḷ',
  };
  const marks = {
    'ಾ': 'ā', 'ಿ': 'i', 'ೀ': 'ī', 'ು': 'u', 'ೂ': 'ū', 'ೃ': 'ṛ', 'ೄ': 'ṝ',
    'ೆ': 'e', 'ೇ': 'ē', 'ೈ': 'ai', 'ೊ': 'o', 'ೋ': 'ō', 'ೌ': 'au',
  };
  const special = { 'ಂ': 'ṃ', 'ಃ': 'ḥ', 'ಁ': 'm̐' };
  const chars = Array.from(text);
  const output = [];
  for (let index = 0; index < chars.length; index += 1) {
    const ch = chars[index];
    if (Object.prototype.hasOwnProperty.call(vowels, ch)) {
      output.push(vowels[ch]);
      continue;
    }
    if (Object.prototype.hasOwnProperty.call(consonants, ch)) {
      const next = chars[index + 1];
      if (next === '್') {
        output.push(consonants[ch]);
        index += 1;
      } else if (Object.prototype.hasOwnProperty.call(marks, next)) {
        output.push(consonants[ch] + marks[next]);
        index += 1;
      } else {
        output.push(consonants[ch] + 'a');
      }
      continue;
    }
    if (Object.prototype.hasOwnProperty.call(special, ch)) {
      output.push(special[ch]);
      continue;
    }
    if (ch === '಼' || ch === 'ಽ') continue;
    output.push(ch);
  }
  return pilot100Normalize_(output.join(''));
}

function pilot100IastToAscii_(text) {
  let value = text.toLowerCase();
  const replacements = [
    ['r̥̄', 'rr'], ['l̥̄', 'll'], ['r̥', 'r'], ['l̥', 'l'], ['ā', 'aa'], ['ī', 'ii'],
    ['ū', 'uu'], ['ē', 'ee'], ['ō', 'oo'], ['ṛ', 'r'], ['ṝ', 'rr'], ['ḷ', 'l'], ['ḹ', 'll'],
    ['ṅ', 'ng'], ['ñ', 'ny'], ['ṭ', 't'], ['ḍ', 'd'], ['ṇ', 'n'], ['ś', 'sh'], ['ṣ', 'sh'],
    ['ḻ', 'l'], ['ṃ', 'm'], ['ṁ', 'm'], ['ḥ', 'h'], ['ṟ', 'r'], ['m̐', 'm'],
  ];
  replacements.forEach(([source, target]) => {
    value = value.split(source).join(target);
  });
  value = value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
  return pilot100Normalize_(value.replace(/[^\x00-\x7F]/g, ''));
}

function pilot100Normalize_(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}
