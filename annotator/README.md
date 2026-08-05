# RomanBench annotator

This directory is the deployable static annotation application.

- `index.html`, `styles.css`, `app.js`: mobile-first frontend.
- `config.js`: production Apps Script endpoint + instruction/terms versions.
- `demo-tasks.json`: local demo content used only when the backend is unconfigured.
- `apps-script/`: Google Sheets backend source.

The frontend asks two binary questions:

1. Does the Roman text have the same meaning as the Kannada sentence?
2. Would you type Kannada this way using English letters?

Question 2 evaluates Romanization/typing plausibility only. It is not a colloquialness judgment.

Deployment and Sheet setup: [`../docs/annotation-platform.md`](../docs/annotation-platform.md).
Research methodology: [`../docs/romanbench-annotation-strategy.md`](../docs/romanbench-annotation-strategy.md).
