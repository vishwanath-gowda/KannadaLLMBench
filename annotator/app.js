(() => {
  "use strict";

  const config = window.ROMANBENCH_CONFIG || {};
  const params = new URLSearchParams(window.location.search);
  const identity = {
    annotator: params.get("annotator") || "",
    token: params.get("token") || "",
    batch: params.get("batch") || "default",
  };
  const isDemo = !config.apiUrl && config.demoWhenUnconfigured !== false;

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

  function showOnly(section) {
    [ui.welcome, ui.annotationCard, ui.loadingCard, ui.doneCard, ui.fatalError].forEach((node) => {
      node.classList.toggle("hidden", node !== section);
    });
  }

  function storageKey(name) {
    return `romanbench:${identity.annotator || "demo"}:${name}`;
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

  function resetAnswers() {
    answers = { meaning: null, typing: null };
    document.querySelectorAll(".choice").forEach((button) => button.classList.remove("selected"));
    updateSubmitState();
  }

  function updateSubmitState() {
    const ready = answers.meaning !== null && answers.typing !== null;
    ui.submitButton.disabled = !ready;
    ui.submitHint.textContent = ready ? "Ready to submit." : "Answer both questions to continue.";
  }

  function setChoice(question, value) {
    answers[question] = value;
    document.querySelectorAll(`[data-question="${question}"]`).forEach((button) => {
      button.classList.toggle("selected", button.dataset.value === value);
    });
    updateSubmitState();
  }

  function renderTask(task, progress = {}) {
    currentTask = task;
    resetAnswers();
    ui.kannadaText.textContent = task.kannada;
    ui.romanText.textContent = task.roman;
    const completed = Number(progress.completed || 0);
    const total = Number(progress.total || 0);
    ui.progressText.textContent = total > 0 ? `${completed + 1} of ${total}` : "Next item";
    ui.progressBar.style.width = total > 0 ? `${Math.min(100, (completed / total) * 100)}%` : "0%";
    ui.annotatorText.textContent = isDemo ? "Demo" : identity.annotator;
    showOnly(ui.annotationCard);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function makeRequestId(taskId) {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return `${taskId}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }

  async function fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.requestTimeoutMs || 15000);
    try {
      return await fetch(url, { ...options, signal: controller.signal });
    } finally {
      clearTimeout(timeout);
    }
  }

  function apiGetNext() {
    return new Promise((resolve, reject) => {
      const callback = `__romanbench_${Date.now()}_${Math.random().toString(16).slice(2)}`;
      const url = new URL(config.apiUrl);
      url.searchParams.set("action", "next");
      url.searchParams.set("annotator", identity.annotator);
      url.searchParams.set("token", identity.token);
      url.searchParams.set("batch", identity.batch);
      url.searchParams.set("prefix", callback);

      const script = document.createElement("script");
      const cleanup = () => {
        clearTimeout(timeout);
        script.remove();
        try { delete window[callback]; } catch (_) { window[callback] = undefined; }
      };
      const timeout = setTimeout(() => {
        cleanup();
        reject(new Error("Backend request timed out"));
      }, config.requestTimeoutMs || 15000);

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

  async function apiSubmit(payload) {
    const body = JSON.stringify(payload);
    try {
      const response = await fetchWithTimeout(config.apiUrl, {
        method: "POST",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body,
      });
      if (!response.ok) throw new Error(`Backend returned HTTP ${response.status}`);
      const data = await response.json();
      if (!data.ok) throw new Error(data.error || "Submission rejected");
      return data;
    } catch (error) {
      // Apps Script Content Service can redirect responses through another Google host.
      // Retrying as a write-only request with the same request_id is safe because the backend is idempotent.
      await fetch(config.apiUrl, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body,
      });
      return { ok: true, optimistic: true, warning: String(error) };
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

  async function demoNext() {
    await loadDemoTasks();
    const seenFamilies = new Set(demoAnnotations().map((row) => row.semantic_family_id));
    const task = demoTasks.find((candidate) => !seenFamilies.has(candidate.semantic_family_id));
    return {
      ok: true,
      done: !task,
      task,
      progress: { completed: seenFamilies.size, total: demoTasks.length },
    };
  }

  async function getNextTask() {
    showOnly(ui.loadingCard);
    ui.loadingText.textContent = "Loading your next item…";
    try {
      const data = isDemo ? await demoNext() : await apiGetNext();
      if (data.done || !data.task) {
        ui.doneText.textContent = isDemo
          ? "Demo complete. Refresh after clearing this site's local storage to try it again."
          : "Thank you. Your annotations have been recorded.";
        showOnly(ui.doneCard);
        return;
      }
      renderTask(data.task, data.progress || {});
    } catch (error) {
      ui.fatalErrorText.textContent = error.message || String(error);
      showOnly(ui.fatalError);
    }
  }

  async function submitCurrent(skipped = false) {
    if (!currentTask) return;
    if (!skipped && (answers.meaning === null || answers.typing === null)) return;

    ui.submitButton.disabled = true;
    ui.skipButton.disabled = true;
    ui.submitHint.textContent = "Saving…";

    const payload = {
      action: "submit",
      request_id: makeRequestId(currentTask.task_id),
      annotator: isDemo ? "demo" : identity.annotator,
      token: isDemo ? "demo" : identity.token,
      batch: identity.batch,
      task_id: currentTask.task_id,
      semantic_family_id: currentTask.semantic_family_id,
      meaning_correct: skipped ? "" : answers.meaning,
      typeable_romanization: skipped ? "" : answers.typing,
      skipped,
      instructions_version: config.instructionsVersion || "v1",
      client_time: new Date().toISOString(),
    };

    try {
      if (isDemo) saveDemoAnnotation(payload);
      else await apiSubmit(payload);
      currentTask = null;
      await getNextTask();
    } catch (error) {
      ui.fatalErrorText.textContent = `Your answer was not confirmed. ${error.message || error}`;
      showOnly(ui.fatalError);
    } finally {
      ui.skipButton.disabled = false;
    }
  }

  function validateIdentity() {
    if (isDemo) {
      ui.demoBanner.classList.remove("hidden");
      return true;
    }
    if (!identity.annotator || !identity.token) {
      ui.identityError.textContent = "This annotation link is incomplete. Ask the project organizer for your personal annotation link.";
      ui.identityError.classList.remove("hidden");
      return false;
    }
    return true;
  }

  document.querySelectorAll(".choice").forEach((button) => {
    button.addEventListener("click", () => setChoice(button.dataset.question, button.dataset.value));
  });
  ui.submitButton.addEventListener("click", () => submitCurrent(false));
  ui.skipButton.addEventListener("click", () => submitCurrent(true));
  ui.retryButton.addEventListener("click", getNextTask);
  ui.startButton.addEventListener("click", () => {
    markInstructionsSeen();
    getNextTask();
  });
  ui.instructionsButton.addEventListener("click", () => ui.instructionsDialog.showModal());
  ui.closeInstructions.addEventListener("click", () => ui.instructionsDialog.close());

  async function initialize() {
    if (!validateIdentity()) return;
    if (!instructionsSeen()) {
      showOnly(ui.welcome);
      ui.instructionsDialog.showModal();
      return;
    }
    await getNextTask();
  }

  initialize();
})();
