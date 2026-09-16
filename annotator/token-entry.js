(() => {
  "use strict";

  const config = window.ROMANBENCH_CONFIG || {};
  const params = new URLSearchParams(window.location.search);
  const tokenGate = document.getElementById("tokenGate");
  const tokenInput = document.getElementById("annotatorToken");
  const tokenButton = document.getElementById("tokenButton");
  const tokenError = document.getElementById("tokenError");
  const instructionsButton = document.getElementById("instructionsButton");

  function loadAnnotatorApp() {
    instructionsButton.classList.remove("hidden");
    const script = document.createElement("script");
    script.src = "app.js";
    script.defer = true;
    document.body.appendChild(script);
  }

  function jsonp(action, token) {
    return new Promise((resolve, reject) => {
      const callback = `__romanbench_auth_${Date.now()}_${Math.random().toString(16).slice(2)}`;
      const url = new URL(config.apiUrl);
      url.searchParams.set("action", action);
      url.searchParams.set("token", token);
      url.searchParams.set("prefix", callback);

      const script = document.createElement("script");
      const timeout = setTimeout(() => {
        cleanup();
        reject(new Error("Token verification timed out"));
      }, config.requestTimeoutMs || 15000);

      function cleanup() {
        clearTimeout(timeout);
        script.remove();
        try { delete window[callback]; } catch (_) { window[callback] = undefined; }
      }

      window[callback] = (data) => {
        cleanup();
        if (!data || !data.ok) {
          reject(new Error((data && data.error) || "Token was not accepted"));
          return;
        }
        resolve(data);
      };

      script.onerror = () => {
        cleanup();
        reject(new Error("Could not reach the annotation backend"));
      };

      script.src = url.toString();
      document.head.appendChild(script);
    });
  }

  async function verifyToken() {
    const token = tokenInput.value.trim();
    tokenError.classList.add("hidden");
    tokenError.textContent = "";

    if (!token) {
      tokenError.textContent = "Enter your annotator token.";
      tokenError.classList.remove("hidden");
      tokenInput.focus();
      return;
    }

    tokenButton.disabled = true;
    tokenButton.textContent = "Checking…";

    try {
      const identity = await jsonp("resolve", token);
      const url = new URL(window.location.href);
      url.search = "";
      url.searchParams.set("annotator", identity.annotator);
      url.searchParams.set("token", token);
      url.searchParams.set("batch", identity.batch || "default");
      window.location.replace(url.toString());
    } catch (error) {
      tokenError.textContent = error.message || String(error);
      tokenError.classList.remove("hidden");
      tokenButton.disabled = false;
      tokenButton.textContent = "Continue";
      tokenInput.select();
    }
  }

  if (params.get("demo") === "1" || params.get("token")) {
    loadAnnotatorApp();
    return;
  }

  tokenGate.classList.remove("hidden");
  tokenInput.focus();
  tokenButton.addEventListener("click", verifyToken);
  tokenInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") verifyToken();
  });
})();
