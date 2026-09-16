# RomanBench multi-device leasing

RomanBench assigns task bundles ahead of time so annotation stays responsive. A row with `status=leased` is therefore normal: it means the task is currently reserved but not yet submitted or skipped.

## Browser-scoped leases

Each browser stores a persistent local `client_id`. The frontend attaches it to Apps Script requests. The backend encodes a hash of that browser id into `assignment_id` as:

`c:<client-key>:<uuid>`

Existing pre-upgrade UUID-only leases are claimed by the first refreshed browser that contacts the backend after deployment. From then on, a browser is only re-served its own active leases. Other browsers using the same annotator token get different tasks.

Leases remain reserved across all browsers for the same annotator, so two devices cannot consume the same semantic family. Submitted/skipped leases are settled immediately; abandoned leases expire after the configured lease TTL.
