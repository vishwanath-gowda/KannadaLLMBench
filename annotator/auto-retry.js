(() => {
  "use strict";

  const fatal = document.getElementById("fatalError");
  const fatalText = document.getElementById("fatalErrorText");
  const retryButton = document.getElementById("retryButton");
  const loading = document.getElementById("loadingCard");
  const loadingText = document.getElementById("loadingText");
  const annotation = document.getElementById("annotationCard");
  const done = document.getElementById("doneCard");

  if (!fatal || !fatalText || !retryButton || !loading || !loadingText) return;

  let retryTimer = null;
  let failures = 0;

  function isPermanent(message) {
    return /invalid annotation token|unknown or inactive annotator|not assigned to this batch|missing browser session id|missing annotator credentials/i.test(message || "");
  }

  function clearRetryState() {
    failures = 0;
    if (retryTimer !== null) {
      clearTimeout(retryTimer);
      retryTimer = null;
    }
  }

  function scheduleAutomaticRetry() {
    if (fatal.classList.contains("hidden")) return;

    const message = fatalText.textContent || "";
    if (isPermanent(message)) return;
    if (retryTimer !== null) return;

    failures += 1;
    const delay = Math.min(10000, 750 * Math.pow(2, Math.min(failures - 1, 4)));

    // Transient Apps Script/network failures are recoverable. Keep the annotator
    // in a passive loading state rather than asking them to manually press Retry.
    fatal.classList.add("hidden");
    loading.classList.remove("hidden");
    loadingText.textContent = failures <= 2
      ? "Loading your next item…"
      : "Connection is slow — retrying automatically…";

    retryTimer = window.setTimeout(() => {
      retryTimer = null;
      retryButton.click();
    }, delay);
  }

  const fatalObserver = new MutationObserver(scheduleAutomaticRetry);
  fatalObserver.observe(fatal, { attributes: true, attributeFilter: ["class"] });

  // A successfully rendered task or completed batch resets the retry backoff.
  [annotation, done].filter(Boolean).forEach((node) => {
    const observer = new MutationObserver(() => {
      if (!node.classList.contains("hidden")) clearRetryState();
    });
    observer.observe(node, { attributes: true, attributeFilter: ["class"] });
  });

  scheduleAutomaticRetry();
})();
