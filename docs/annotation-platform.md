# RomanBench annotation platform

RomanBench uses a deliberately lightweight, free annotation stack for contributors known to the project:

- **frontend:** static GitHub Pages site in `annotator/`;
- **backend:** Google Apps Script web app;
- **storage:** Google Sheets;
- **identity:** pseudonymous annotator ID + random access token;
- **normal annotation interaction:** one mandatory Yes/No meaning judgment, a conditional Roman-typing Yes/No judgment, plus Skip; no typing required.

The frontend contains no Google credentials or secrets. The Apps Script runs as the Sheet owner and validates annotator tokens before returning or accepting tasks.

For the operational first-pilot procedure, including personal-link sharing, 30-family task construction, and post-pilot analysis, see [`romanbench-pilot-runbook.md`](romanbench-pilot-runbook.md).

## Annotator experience

Each contributor receives a personal link such as:

```text
https://<github-user>.github.io/KannadaLLMBench/?annotator=KN001&token=<random-token>&batch=pilot-v1
```

The page shows one pair at a time:

1. Kannada sentence;
2. candidate form typed with English letters;
3. **Does the Roman text have the same meaning as the Kannada sentence?** Yes / No;
4. if Question 1 = **Yes**, **Would you type Kannada this way using English letters?** Yes / No;
5. Skip.

If Question 1 = **No**, the item is submitted immediately and the typing label is stored as N/A/blank. Typing plausibility is undefined when the Roman candidate does not preserve the source meaning.

The interface explicitly says that question 2 is about the English-letter spelling/style and **not** whether the underlying Kannada sentence is formal or colloquial.

Before the first item, contributors are shown the versioned validation contribution terms. Selecting **Start annotating** records participation under `romanbench-validation-v1`; see [`romanbench-validation-terms-v1.md`](romanbench-validation-terms-v1.md).

## Demo mode

Until `annotator/config.js` contains an Apps Script URL, the site automatically operates in demo mode.

Demo annotations remain in browser `localStorage` and are never sent anywhere. This allows the UI and instructions to be reviewed before creating a Google Sheet.

The demo intentionally includes:

- meaning-preserving, plausible Roman Kannada;
- meaning-preserving but formal/awkward transliteration;
- semantic-negative examples where the Roman candidate changes content such as today→tomorrow or six→eight;
- a colloquial Kannada example to reinforce that colloquialness is not the Roman-typing label.

To restart the demo, clear site data/local storage for the Pages site.

## 1. Deploy GitHub Pages

The repository includes `.github/workflows/pages.yml`, which publishes only the `annotator/` directory.

GitHub's current Pages custom-workflow documentation uses:

- `actions/configure-pages@v5`;
- `actions/upload-pages-artifact@v4`;
- `actions/deploy-pages@v4`;
- `pages: write` and `id-token: write` permissions.

One-time repository setup:

1. Open **Repository Settings → Pages**.
2. Set the publishing source to **GitHub Actions**.
3. Merge/push an annotator change to `main`, or manually run **Deploy RomanBench annotator** from Actions.
4. Copy the published Pages URL.

GitHub reference: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## 2. Create the Google Sheet

Create a new private Google Sheet owned by the project organizer.

The app uses three tabs:

- `Tasks`
- `Annotations`
- `Annotators`

Do not manually invent headers. The Apps Script function `setupAnnotationSheets()` creates/verifies the expected schemas.

### Tasks columns

```text
task_id
semantic_family_id
kannada
roman
variant_type
source_type
source_id
source_author_id
batch_id
target_votes
active
```

### Annotations columns

```text
timestamp
request_id
task_id
semantic_family_id
annotator_id
batch_id
meaning_correct
typeable_romanization
skipped
instructions_version
terms_version
client_time
```

When `meaning_correct=no`, `typeable_romanization` is intentionally blank.

### Annotators columns

```text
annotator_id
token_sha256
active
batches
max_tasks
note
```

Names and email addresses are intentionally not required.

## 3. Install Apps Script

From the Google Sheet:

1. Open **Extensions → Apps Script**.
2. Replace the default code with `annotator/apps-script/Code.gs`.
3. If using the manifest file directly, copy `annotator/apps-script/appsscript.json` as well; otherwise the deployment UI can set the equivalent web-app access configuration.
4. Save.
5. Run `setupAnnotationSheets()` once from the Apps Script editor and authorize the script to access the Sheet.

Google's Apps Script web-app documentation requires a `doGet(e)` or `doPost(e)` entrypoint. RomanBench implements both.

Google reference: https://developers.google.com/apps-script/guides/web

## 4. Deploy Apps Script as a web app

In Apps Script:

1. Click **Deploy → New deployment**.
2. Select **Web app**.
3. Execute as: **Me / user deploying**.
4. Access: **Anyone** (anonymous access if available for the Google account/Workspace policy).
5. Deploy and copy the URL ending in `/exec`.

The backend does not trust anonymous access by itself. Every request still needs an annotator ID and random token whose SHA-256 hash is stored in the Sheet.

If a Workspace policy does not allow anonymous Apps Script web apps, either use an account that permits it or require signed-in access. The frontend design does not otherwise change.

### Updating an existing Apps Script deployment

GitHub does not automatically synchronize `annotator/apps-script/Code.gs` into a Sheet-bound Apps Script project. After backend code changes:

1. copy the merged `Code.gs` into the Sheet's Apps Script editor;
2. save;
3. open **Deploy → Manage deployments**;
4. edit the web-app deployment;
5. create/select the new version and deploy it;
6. keep the existing `/exec` URL unless Google explicitly changes it.

The frontend and Apps Script versions must be synchronized before a production annotation batch begins.

## 5. Connect the frontend

Edit `annotator/config.js`:

```javascript
window.ROMANBENCH_CONFIG = {
  apiUrl: "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec",
  demoWhenUnconfigured: true,
  requestTimeoutMs: 15000,
  instructionsVersion: "romanbench-annotation-v2",
  termsVersion: "romanbench-validation-v1",
};
```

Commit to `main`; the Pages workflow redeploys the static site.

Changing the annotation wording or interaction semantics requires bumping `instructionsVersion`, so paper/release metadata can distinguish judgments collected under different instructions. Substantive changes to contributor terms require a new `termsVersion` and a corresponding terms document.

## 6. Load annotation tasks

### First pilot: deterministic one-candidate-per-family selection

For the first pilot, build a candidate pool and then select approximately 30 semantic families:

```bash
make romanbench-candidates \
  FAMILIES=100 \
  ROMAN_OUTPUT=data/interim/romanbench/pilot-candidates.jsonl

make romanbench-pilot \
  PILOT_INPUT=data/interim/romanbench/pilot-candidates.jsonl \
  PILOT_OUTPUT=data/interim/romanbench/pilot-v1-tasks.csv \
  PILOT_FAMILIES=30 \
  PILOT_BATCH=pilot-v1
```

The pilot builder selects exactly one Roman candidate per family, uses `target_votes=2` by default, and writes a sidecar manifest with the deterministic seed and variant counts.

### Generic generated candidates

```bash
make annotator-tasks \
  ANNOTATOR_INPUT=data/interim/romanbench/candidates.jsonl \
  ANNOTATOR_OUTPUT=data/interim/romanbench/tasks.csv \
  ANNOTATOR_BATCH=pilot \
  ANNOTATOR_VOTES=2
```

Then import/append the CSV rows into the `Tasks` sheet below the existing header.

### From an existing permissive Kannada↔Roman dataset

First convert the chosen clean subset to JSONL while retaining its original provenance. Then:

```bash
python scripts/export_annotator_tasks.py pairs.jsonl tasks.csv \
  --mode pairs \
  --task-id-field pair_id \
  --family-id-field family_id \
  --kannada-field kannada \
  --roman-field roman \
  --source-id ai4bharat/example-clean-subset \
  --batch existing-data-pilot \
  --target-votes 2
```

Existing pairs are re-annotated rather than assumed to satisfy RomanBench's task-specific definition of typing plausibility.

## 7. Create annotator links

From the Apps Script editor, run:

```javascript
createAnnotator(
  'KN001',
  'https://<github-user>.github.io/KannadaLLMBench',
  'pilot-v1'
)
```

The function:

1. creates a long random token;
2. stores only its SHA-256 hash in `Annotators`;
3. prints/returns the personal link containing the plaintext token.

Send that link only to the intended contributor. Do not send the base Pages URL by itself.

Rotating the token is as simple as calling `createAnnotator` again for the same ID.

`batches` can contain comma-separated allowed batches in the Sheet. `max_tasks` optionally caps how many completed judgments an annotator can contribute.

## 8. Assignment rules enforced by the backend

The Apps Script backend enforces:

- active annotator + valid access token;
- requested batch authorization;
- active tasks only;
- target vote count per candidate;
- lowest-vote candidates are prioritized;
- one semantic family per annotator;
- an annotator cannot judge a family whose `source_author_id` matches their ID;
- no exposure to other annotators' labels;
- skipped items do not count toward target votes;
- skipped semantic families are still not shown to that annotator again;
- duplicate `request_id` submissions are idempotent;
- script locking protects read/select/write races.

The “one family per annotator” rule is important when several Roman variants share the same Kannada sentence: seeing one spelling should not anchor that person's judgment of another spelling from the same family.

## 9. Browser ↔ Apps Script transport

Google's Content Service redirects output through a Google-hosted content URL. For reliable browser-side **read-only** task retrieval, the frontend uses JSONP with a generated callback name. Google documents JSONP as a browser-access pattern for Content Service and cautions that it should be used only for read-only information; RomanBench uses it only to retrieve the next authorized task.

Submissions use POST with JSON encoded as `text/plain`, avoiding a browser CORS preflight for the normal request shape. The frontend first attempts a response-readable POST. If a browser cannot read the redirected response after the write, it retries in `no-cors` mode with the **same request ID**. The backend's idempotency check prevents the retry from producing a second annotation row.

Google Content Service reference: https://developers.google.com/apps-script/guides/content

For a serious production run, test the exact deployed Pages origin + Apps Script deployment in the browsers annotators will use before sending a large batch.

## 10. Spreadsheet operations

Recommended practices:

- keep the Google Sheet private to benchmark maintainers;
- do not publish the Sheet to the web;
- use protected ranges for header rows;
- append tasks rather than editing IDs after annotations begin;
- set `active=false` instead of deleting problematic tasks;
- never recycle a `task_id` or `semantic_family_id` with new content;
- export immutable CSV snapshots at benchmark release time;
- hash/version snapshots in the repository release manifest.

## 11. Pilot plan

Before broad annotation:

1. enable Pages and verify the deployed site;
2. deploy the Sheet backend and perform an incognito end-to-end test;
3. make sure the demo includes plausible, awkward, and semantically incorrect candidates;
4. build 30 semantic families with one candidate each;
5. load them as `pilot-v1` with `target_votes=2`;
6. create 4–5 personal annotator links;
7. collect approximately 60 completed judgments in total;
8. export the `Annotations` tab to CSV;
9. run `make romanbench-pilot-analyze`;
10. inspect meaning agreement, typing agreement, skip rate, `Meaning=Yes/Typing=No`, and disagreement rows before changing the protocol or scaling up.

Do not change question wording midway through a production benchmark version without recording the change.

## 12. Pilot analysis

After exporting the `Annotations` tab:

```bash
make romanbench-pilot-analyze \
  PILOT_ANNOTATIONS=data/interim/romanbench/pilot-v1-annotations.csv
```

The analysis produces a JSON summary and a task-level disagreement CSV. Roman-typing agreement is computed only among judgments with `meaning_correct=yes`; `meaning_correct=no` rows have no typing label by design.

## 13. Security model and limitations

This system is intentionally lightweight because contributors are known to the project. It is not a high-security crowdsourcing platform.

Protections provided:

- random bearer token per pseudonymous annotator;
- token hashes at rest in the Sheet;
- no Google Sheet access for annotators;
- task assignment/validation on the backend;
- no secret embedded in GitHub Pages.

Limitations:

- anyone who obtains a contributor's personal link can impersonate that pseudonymous contributor;
- Apps Script/Sheets quotas make this suitable for volunteer benchmark annotation, not very high-volume public crowdsourcing;
- Google Sheet history/admin access contains annotation data and should be treated as benchmark source data.

For the current use case—known contributors and thousands rather than millions of judgments—this tradeoff keeps cost and friction close to zero.
