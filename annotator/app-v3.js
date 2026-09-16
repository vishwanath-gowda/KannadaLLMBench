(() => {
  "use strict";

  const config = window.ROMANBENCH_CONFIG || {};
  const params = new URLSearchParams(window.location.search);
  const identity = {
    annotator: params.get("annotator") || "",
    token: params.get("token") || "",
    batch: params.get("batch") || "default",
  };
  const forceDemo = params.get("demo") === "1";
  const isDemo = forceDemo || (!config.apiUrl && config.demoWhenUnconfigured !== false);

  const el = (id) => document.getElementById(id);
  const ui = {
    demoBanner: el("demoBanner"),
    identityError: el("identityError"),
    welcome: el("welcome"),
    annotationCard: el("annotationCard"),
    loadingCard: el("loadingCard"),
    doneCard: el("doneCard"),
    fatalError: el("fatalError"),
    fatalErrorText: el("fatalErrorText"),
    loadingText: el("loadingText"),
    progressText: el("progressText"),
    progressBar: el("progressBar"),
    annotatorText: el("annotatorText"),
    kannadaText: el("kannadaText"),
    romanText: el("romanText"),
    typingQuestion: el("typingQuestion"),
    submitButton: el("submitButton"),
    skipButton: el("skipButton"),
    submitHint: el("submitHint"),
    startButton: el("startButton"),
    retryButton: el("retryButton"),
    instructionsButton: el("instructionsButton"),
    instructionsDialog: el("instructionsDialog"),
    closeInstructions: el("closeInstructions"),
    doneText: el("doneText"),
  };

  let currentTask = null;
  let answers = { meaning: null, typing: null };
  let demoTasks = [];
  let taskQueue = [];
  let refillPromise = null;
  let saveWorkerPromise = null;
  let backendDone = false;
  let progress = { completed: 0, total: 0 };
  let optimisticCompleted = 0;

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  function bundleSize() {
    const value = Number(config.prefetchCount || 8);
    return Math.max(1, Math.min(8, Number.isFinite(value) ? Math.floor(value) : 8));
  }

  function refillThreshold() {
    const value = Number(config.refillThreshold || 5);
    return Math.max(0, Math.min(bundleSize() - 1, Number.isFinite(value) ? Math.floor(value) : 5));
  }

  function showOnly(section) {
    [ui.welcome, ui.annotationCard, ui.loadingCard, ui.doneCard, ui.fatalError].forEach((node) => {
      node.classList.toggle("hidden", node !== section);
    });
  }

  function storageKey(name) {
    return `romanbench:${identity.annotator || "demo"}:${identity.batch}:${name}`;
  }

  function consentVersion() {
    return `${config.instructionsVersion || "v1"}|${config.termsVersion || "terms-v1"}`;
  }

  function instructionsSeen() {
    return localStorage.getItem(storageKey("instructions")) === consentVersion();
  }

  function markInstructionsSeen() {
    localStorage.setItem(storageKey("instructions"), consentVersion());
  }

  function loadOutbox() {
    try {
      const value = JSON.parse(localStorage.getItem(storageKey("outbox")) || "[]");
      return Array.isArray(value) ? value : [];
    } catch (_) {
      return [];
    }
  }

  function saveOutbox(rows) {
    localStorage.setItem(storageKey("outbox"), JSON.stringify(rows));
  }

  function outboxTaskIds() {
    return new Set(loadOutbox().map((row) => row && row.task_id).filter(Boolean));
  }

  function enqueueOutbox(payload) {
    const rows = loadOutbox();
    if (!rows.some((row) => row.request_id === payload.request_id)) rows.push(payload);
    saveOutbox(rows);
  }

  function removeOutboxRequest(requestId) {
    saveOutbox(loadOutbox().filter((row) => row.request_id !== requestId));
  }

  function resetAnswers() {
    answers = { meaning: null, typing: null };
    document.querySelectorAll(".choice").forEach((button) => button.classList.remove("selected"));
    ui.typingQuestion.classList.add("hidden");
    ui.submitButton.classList.add("hidden");
    ui.skipButton.disabled = false;
    updateSubmitState();
  }

  function updateSubmitState() {
    if (answers.meaning === null) {
      ui.typingQuestion.classList.add("hidden");
      ui.submitButton.classList.add("hidden");
      ui.submitButton.disabled = true;
      ui.submitHint.textContent = "Answer question 1 to continue.";
      return;
    }
    if (answers.meaning === "no") {
      ui.typingQuestion.classList.add("hidden");
      ui.submitButton.classList.add("hidden");
      ui.submitButton.disabled = true;
      ui.submitHint.textContent = "Meaning differs — moving on…";
      return;
    }
    ui.typingQuestion.classList.remove("hidden");
    ui.submitButton.classList.remove("hidden");
    const ready = answers.typing !== null;
    ui.submitButton.disabled = !ready;
    ui.submitHint.textContent = ready ? "Ready to submit." : "Answer question 2 to continue.";
  }

  function setChoice(question, value) {
    answers[question] = value;
    document.querySelectorAll(`[data-question="${question}"]`).forEach((button) => {
      button.classList.toggle("selected", button.dataset.value === value);
    });
    if (question === "meaning" && value !== "yes") {
      answers.typing = null;
      document.querySelectorAll('[data-question="typing"]').forEach((button) => button.classList.remove("selected"));
    }
    updateSubmitState();
  }

  function updateProgressDisplay() {
    const completed = Math.max(Number(progress.completed || 0), optimisticCompleted);
    const total = Number(progress.total || 0);
    ui.progressText.textContent = total > 0 ? `${Math.min(completed + 1, total)} of ${total}` : "Next item";
    ui.progressBar.style.width = total > 0 ? `${Math.min(100, (completed / total) * 100)}%` : "0%";
  }

  function renderTask(task) {
    currentTask = task;
    resetAnswers();
    ui.kannadaText.textContent = task.kannada;
    ui.romanText.textContent = task.roman;
    updateProgressDisplay();
    ui.annotatorText.textContent = isDemo ? "Demo" : identity.annotator;
    showOnly(ui.annotationCard);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function makeRequestId(taskId) {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return `${taskId}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  async function fetchWithTimeout(url, options = {}, timeoutMs = null) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs || config.requestTimeoutMs || 45000);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timeout);
    }
  }

  function apiGetNext(count = bundleSize()) {
    return new Promise((resolve, reject) => {
      const callback = `__romanbench_${Date.now()}_${Math.random().toString(16).slice(2)}`;
      const url = new URL(config.apiUrl);
      url.searchParams.set("action", "next");
      url.searchParams.set("annotator", identity.annotator);
      url.searchParams.set("token", identity.token);
      url.searchParams.set("batch", identity.batch);
      url.searchParams.set("count", String(count));
      url.searchParams.set("prefix", callback);
      url.searchParams.set("_", String(Date.now()));

      const script = document.createElement("script");
      const cleanup = () => {
        clearTimeout(timeout);
        script.remove();
        try { delete window[callback]; } catch (_) { window[callback] = undefined; }
      };
      const timeout = setTimeout(() => {
        cleanup();
        reject(new Error("Backend request timed out"));
      }, config.requestTimeoutMs || 45000);

      window[callback] = (data) => {
        cleanup();
        if (!data || !data.ok) reject(new Error((data && data.error) || "Backend rejected the request"));
        else resolve(data);
      };
      script.onerror = () => {
        cleanup();
        reject(new Error("Could not load the annotation backend"));
      };
      script.src = url.toString();
      document.head.appendChild(script);
    });
  }

  function warmBackend() {
    if (isDemo || !config.apiUrl) return;
    try {
      const url = new URL(config.apiUrl);
      url.searchParams.set("action", "ping");
      url.searchParams.set("_", String(Date.now()));
      fetch(url.toString(), { mode: "no-cors", cache: "no-store", keepalive: true }).catch(() => {});
    } catch (_) {}
  }

  async function apiSubmitConfirmed(payload) {
    const body = JSON.stringify(payload);
    const response = await fetchWithTimeout(config.apiUrl, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body,
      cache: "no-store",
    }, config.saveTimeoutMs || 45000);
    if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
    const data = await response.json();
    if (!data || !data.ok) throw new Error((data && data.error) || "Submission rejected");
    return data;
  }

  async function bestEffortNoCors(payload) {
    try {
      await fetch(config.apiUrl, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify(payload),
        keepalive: true,
      });
    } catch (_) {}
  }

  async function flushOutbox() {
    if (isDemo) return;
    if (saveWorkerPromise) return saveWorkerPromise;

    saveWorkerPromise = (async () => {
      let failureCount = 0;
      while (true) {
        const rows = loadOutbox();
        if (!rows.length) return;
        const payload = rows[0];
        try {
          await apiSubmitConfirmed(payload);
          removeOutboxRequest(payload.request_id);
          failureCount = 0;
          ui.identityError.classList.add("hidden");
          backgroundRefillIfNeeded();
        } catch (error) {
          failureCount += 1;
          // A write-only attempt may succeed through Apps Script's redirect path. We still keep
          // the durable outbox entry until a later readable/idempotent retry explicitly succeeds.
          bestEffortNoCors(payload);
          const delay = Math.min(15000, 700 * Math.pow(2, Math.min(failureCount, 4)));
          console.warn("RomanBench save retry", payload.request_id, error);
          await sleep(delay);
        }
      }
    })();

    try {
      return await saveWorkerPromise;
    } finally {
      saveWorkerPromise = null;
    }
  }

  function demoAnnotations() {
    try {
      return JSON.parse(localStorage.getItem(storageKey("demo-annotations")) || "[]");
    } catch (_) {
      return [];
    }
  }

  function saveDemoAnnotation(annotation) {
    const rows = demoAnnotations();
    rows.push(annotation);
    localStorage.setItem(storageKey("demo-annotations"), JSON.stringify(rows));
  }

  async function loadDemoTasks() {
    if (demoTasks.length) return;
    const response = await fetch("demo-tasks.json", { cache: "no-store" });
    demoTasks = await response.json();
  }

  async function demoBundle(count) {
    await loadDemoTasks();
    const seenFamilies = new Set(demoAnnotations().map((row) => row.semantic_family_id));
    if (currentTask) seenFamilies.add(currentTask.semantic_family_id);
    taskQueue.forEach((task) => seenFamilies.add(task.semantic_family_id));
    const tasks = demoTasks.filter((candidate) => !seenFamilies.has(candidate.semantic_family_id)).slice(0, count);
    const completed = demoAnnotations().length;
    return { ok: true, done: tasks.length === 0, tasks, progress: { completed, total: demoTasks.length } };
  }

  function enqueueTasks(tasks) {
    // Only suppress work that is currently visible/queued or has a durable unsent answer.
    // Do not suppress every task seen in this browser session: a task re-served by the backend
    // can be a legitimate recovery of an annotation that was never persisted.
    const known = outboxTaskIds();
    taskQueue.forEach((task) => known.add(task.task_id));
    if (currentTask) known.add(currentTask.task_id);
    for (const task of tasks || []) {
      if (!task || !task.task_id || known.has(task.task_id)) continue;
      taskQueue.push(task);
      known.add(task.task_id);
    }
  }

  async function requestBundle() {
    return isDemo ? demoBundle(bundleSize()) : apiGetNext(bundleSize());
  }

  async function fillQueue({ foreground = false } = {}) {
    if (refillPromise) return refillPromise;
    if (foreground && !currentTask && taskQueue.length === 0) {
      showOnly(ui.loadingCard);
      ui.loadingText.textContent = loadOutbox().length ? "Saving and loading your items…" : "Loading your items…";
    }

    refillPromise = (async () => {
      const data = await requestBundle();
      const tasks = Array.isArray(data.tasks) ? data.tasks : (data.task ? [data.task] : []);
      enqueueTasks(tasks);
      backendDone = Boolean(data.done) && tasks.length === 0;
      if (data.progress) {
        progress = data.progress;
        optimisticCompleted = Math.max(optimisticCompleted, Number(progress.completed || 0));
      }
      return data;
    })();

    try {
      return await refillPromise;
    } finally {
      refillPromise = null;
    }
  }

  function backgroundRefillIfNeeded() {
    if (isDemo && backendDone) return;
    if (taskQueue.length <= refillThreshold()) {
      fillQueue().catch((error) => console.warn("RomanBench background refill failed", error));
    }
  }

  function showDone() {
    ui.doneText.textContent = isDemo
      ? "Demo complete. Refresh after clearing this site's local storage to try it again."
      : "Thank you. Your annotations have been recorded.";
    showOnly(ui.doneCard);
  }

  async function showNextTask() {
    if (currentTask) return;
    if (taskQueue.length > 0) {
      renderTask(taskQueue.shift());
      backgroundRefillIfNeeded();
      return;
    }

    showOnly(ui.loadingCard);
    let lastError = null;
    for (let attempt = 0; attempt < 4; attempt += 1) {
      ui.loadingText.textContent = loadOutbox().length ? "Saving and loading your items…" : "Loading your items…";
      try {
        await fillQueue({ foreground: true });
        if (taskQueue.length > 0) {
          renderTask(taskQueue.shift());
          backgroundRefillIfNeeded();
          return;
        }
        if (backendDone && loadOutbox().length === 0) {
          showDone();
          return;
        }
      } catch (error) {
        lastError = error;
      }

      // Give the serialized saver time to settle leases before asking for another bundle.
      flushOutbox().catch(() => {});
      await sleep(700 * (attempt + 1));
    }

    ui.fatalErrorText.textContent = lastError
      ? `${lastError.message || lastError}. Your submitted answers are safely queued in this browser; Try again when ready.`
      : "Items are temporarily unavailable. Your submitted answers are safely queued in this browser; try again.";
    showOnly(ui.fatalError);
  }

  function submitCurrent(skipped = false) {
    if (!currentTask) return;
    if (!skipped && answers.meaning === null) return;
    if (!skipped && answers.meaning === "yes" && answers.typing === null) return;

    const task = currentTask;
    const payload = {
      action: "submit",
      request_id: makeRequestId(task.task_id),
      annotator: isDemo ? "demo" : identity.annotator,
      token: isDemo ? "demo" : identity.token,
      batch: identity.batch,
      task_id: task.task_id,
      semantic_family_id: task.semantic_family_id,
      meaning_correct: skipped ? "" : answers.meaning,
      typeable_romanization: skipped || answers.meaning !== "yes" ? "" : answers.typing,
      skipped,
      instructions_version: config.instructionsVersion || "v1",
      client_time: new Date().toISOString(),
    };

    if (isDemo) saveDemoAnnotation(payload);
    else enqueueOutbox(payload); // durable locally before the UI advances

    currentTask = null;
    if (!skipped) optimisticCompleted += 1;
    if (!isDemo) flushOutbox().catch(() => {}); // one serialized saver for the whole session
    showNextTask();
  }

  function validateIdentity() {
    if (isDemo) {
      ui.demoBanner.classList.remove("hidden");
      return true;
    }
    if (!identity.annotator || !identity.token) {
      ui.identityError.textContent = "This annotation link is incomplete. Return to the base RomanBench URL and enter your annotator token.";
      ui.identityError.classList.remove("hidden");
      return false;
    }
    return true;
  }

  document.querySelectorAll(".choice").forEach((button) => {
    button.addEventListener("click", () => {
      setChoice(button.dataset.question, button.dataset.value);
      if (button.dataset.question === "meaning" && button.dataset.value === "no") submitCurrent(false);
    });
  });
  ui.submitButton.addEventListener("click", () => submitCurrent(false));
  ui.skipButton.addEventListener("click", () => submitCurrent(true));
  ui.retryButton.addEventListener("click", () => showNextTask());
  ui.startButton.addEventListener("click", () => {
    markInstructionsSeen();
    ui.instructionsDialog.close();
    showNextTask();
  });
  ui.instructionsButton.addEventListener("click", () => ui.instructionsDialog.showModal());
  ui.closeInstructions.addEventListener("click", () => ui.instructionsDialog.close());

  async function initialize() {
    if (!validateIdentity()) return;
    warmBackend();
    if (!isDemo && loadOutbox().length) flushOutbox().catch(() => {});
    if (!instructionsSeen()) {
      showOnly(ui.welcome);
      ui.instructionsDialog.showModal();
      return;
    }
    await showNextTask();
  }

  initialize();
})();
