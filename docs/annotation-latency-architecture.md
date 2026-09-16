# RomanBench low-latency annotation architecture

RomanBench keeps the zero-cost GitHub Pages + Google Apps Script + Google Sheets stack, but avoids paying an Apps Script/Sheets round trip after every judgment.

## Fast path

The frontend requests a bundle of up to five tasks. Apps Script leases those tasks to the annotator for 30 minutes and returns them in one JSONP response. The browser displays one task and keeps the remainder in memory.

After an answer:

1. the browser immediately displays the next already-leased task;
2. the completed annotation POST runs in the background;
3. when the local buffer falls to two items, the browser starts a background refill;
4. the annotator normally sees no loading screen between items.

The first request can still pay Apps Script cold-start / Sheets latency. The page sends a lightweight `ping` while the annotator reads the instructions and preconnects to the Google script hosts to reduce that initial cost.

## Assignment leases

`setupAnnotationSheets()` now creates a fourth sheet:

```text
Assignments
```

with columns:

```text
assignment_id
task_id
semantic_family_id
annotator_id
batch_id
status
leased_at
expires_at
```

A live lease counts as a temporary vote reservation. This prevents several simultaneous annotators from all being handed the same final vote slot.

Lease states are:

- `leased`: reserved and not yet submitted;
- `submitted`: completed annotation;
- `skipped`: annotator skipped the item.

Expired `leased` rows stop reserving a vote automatically. Old rows are retained as operational history; they do not count after expiry.

## Refresh / recovery

If an annotator refreshes or reopens the link while leases are still active, the backend returns their existing leased tasks before allocating new ones. This means a page refresh does not immediately lose the work allocation.

Within a running browser session, the frontend also keeps a seen-task set so a slow background POST cannot cause a just-answered lease to be displayed again.

## Selection rules

For each bundle the backend still enforces:

- valid annotator token and batch authorization;
- active tasks only;
- one semantic family per annotator;
- no self-authored family;
- batch-scoped annotation history;
- `target_votes` using completed votes plus active leases;
- lowest effective vote count first;
- optional `max_tasks` cap.

The script lock covers selection + lease creation so concurrent bundle requests cannot reserve the same remaining vote slot beyond `target_votes` under normal lease operation.

## Other latency changes

The web request path no longer calls `setupAnnotationSheets()` on every GET/POST. Schema creation/verification is an explicit setup operation only.

Task rows are cached per batch for 60 seconds because the task pool is effectively static during an annotation session. Annotations and active assignments are still read fresh so vote/lease decisions remain current.

## Creating the current pilot annotators

After pasting the current `annotator/apps-script/Code.gs` into the bound Apps Script project, either run the helpers individually:

```javascript
createVishwanathAnnotator()
createSharathAnnotator()
```

or run both at once:

```javascript
createPilotAnnotators()
```

`vishwanath` already exists, so running the helper intentionally rotates that token and prints a fresh personal URL. `sharath` is created if absent. Plaintext tokens are only printed/returned; the Sheet stores SHA-256 hashes.

Running either helper also calls `setupAnnotationSheets()`, so the new `Assignments` sheet is created automatically.

## Deployment checklist

1. Copy the complete current `annotator/apps-script/Code.gs` into Apps Script.
2. Save it.
3. Run `createPilotAnnotators()` (or `setupAnnotationSheets()` first, then the individual helpers).
4. Copy the fresh personal URLs from the execution log.
5. **Deploy → Manage deployments → Edit → New version → Deploy**.
6. Keep the existing `/exec` URL; the deployment ID does not need to change.
7. GitHub Pages deploys the matching frontend automatically after the repository change is merged.

Do not invite annotators with the buffered frontend until the Apps Script deployment has also been updated, because the frontend expects the new `Assignments`/bundle behavior.
