# Security policy

Do not open a public issue for a vulnerability that could expose credentials, private benchmark sets, participant information, or unreleased data.

Use GitHub's private vulnerability reporting feature for this repository when available. Include the affected revision, reproduction details, potential impact, and suggested mitigation if known.

Secrets such as Hugging Face tokens must only be provided through environment variables or CI secret stores. They must never be committed to configuration, manifests, model outputs, or test fixtures.
