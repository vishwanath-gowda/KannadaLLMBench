# RomanBench annotation platform

RomanBench uses a deliberately lightweight, free annotation stack for contributors known to the project:

- **frontend:** static GitHub Pages site in `annotator/`;
- **backend:** Google Apps Script web app;
- **storage:** Google Sheets;
- **identity:** pseudonymous annotator ID + random access token;
- **normal annotation interaction:** two Yes/No judgments plus Skip; no typing required.

The frontend contains no Google credentials or secrets. The Apps Script runs as the Sheet owner and validates annotator tokens before returning or accepting tasks.

## Annotator experience

Each contributor receives a personal link such as:

```text
https://<github-user>.github.io/KannadaLLMBench/?annotator=KN001&token=<random-token>&batch=pilot
```

The page shows one pair at a time:

1. Kannada sentence;
2. candidate form typed with English letters;
3. **Does the Roman text have the same meaning as the Kannada sentence?** Yes / No;
4. **Would you type Kannada this way using English letters?** Yes / No;
5. Skip.

The interface explicitly says that question 2 is about the English-letter spelling/style and **not** whether the underlying Kannada sentence is formal or colloquial.

Before the first item, contributors are shown the versioned validation contribution terms. Selecting **Start annotating** records participation under `romanbench-validation-v1`; see [`romanbench-validation-terms-v1.md`](romanbench-validation-terms-v1.md).

## Demo mode

Until `annotator/config.js` contains an Apps Script URL, the site automatically operates in demo mode.

Demo annotations remain in browser `localStorage` and are never sent anywhere. This allows the UI and instructions to be reviewed before creating a Google Sheet.

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

## 5. Connect the frontend

Edit `annotator/config.js`:

```javascript
window.ROMANBENCH_CONFIG = {
  apiUrl: "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec",
  demoWhenUnconfigured: true,
  requestTimeoutMs: 15000,
  instructionsVersion: "romanbench-annotation-v1",
  termsVersion: "romanbench-validation-v1",
};
```

Commit to `main`; the Pages workflow redeploys the static site.

Changing the annotation wording requires bumping `instructionsVersion`, so paper/release metadata can distinguish judgments collected under different instructions. Substantive changes to contributor terms require a new `termsVersion` and a corresponding terms document.

## 6. Load annotation tasks

### From RomanBench generated candidates

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
  'pilot'
)
```

The function:

1. creates a long random token;
2. stores only its SHA-256 hash in `Annotators`;
3. prints/returns the personal link containing the plaintext token.

Send that link only to the intended contributor.

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

1. enable Pages;
2. review demo mode on phone and desktop;
3. deploy the Sheet backend;
4. load approximately 50–100 candidate pairs;
5. create 3–5 annotator links;
6. collect two votes per candidate;
7. inspect skip/disagreement patterns;
8. revise wording only if needed;
9. if wording changes, increment `instructionsVersion` and run a new pilot batch.

Do not change question wording midway through a production benchmark version without recording the change.

## 12. Security model and limitations

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
