# RomanBench durable submission recovery

Observed during pilot-100-v1: annotator UI advanced through items while some background submissions were not durably persisted. Subsequent refills re-served still-leased tasks, but the browser session-level seen-task filter discarded them, causing repeated loading/timeouts and missing annotations.

## Fix
- Persist every answer to a browser-side outbox before advancing.
- Serialize writes to avoid Apps Script lock contention.
- Never treat a no-cors POST as success by itself.
- Add a read-only request-status endpoint to verify a request_id was persisted.
- Remove the session-wide duplicate suppression that blocks legitimate recovery; suppress only current/queued/outbox tasks.
- Retry transient refill failures rather than losing the session.
