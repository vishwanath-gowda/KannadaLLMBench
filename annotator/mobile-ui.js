(() => {
  "use strict";

  const annotationCard = document.getElementById("annotationCard");
  const meaningQuestion = document.getElementById("meaningQuestion");
  const typingQuestion = document.getElementById("typingQuestion");
  const submitButton = document.getElementById("submitButton");
  const skipButton = document.getElementById("skipButton");
  const progressRow = document.querySelector(".progress-row");
  const kannadaText = document.getElementById("kannadaText");

  if (!annotationCard || !meaningQuestion || !typingQuestion || !submitButton) return;

  document.body.classList.add("tap-flow");

  // Keep Skip at the top of the card so it is always reachable on a phone.
  if (skipButton && progressRow) {
    skipButton.classList.remove("secondary", "full");
    skipButton.classList.add("skip-compact");
    skipButton.textContent = "Skip";
    progressRow.appendChild(skipButton);
  }

  // app-v3 owns state and durable submission. This layer only removes the extra
  // form-style Submit tap: Q2 answers click the existing Submit button after
  // app-v3 has recorded the selected answer.
  document.querySelectorAll(".choice").forEach((button) => {
    button.addEventListener("click", () => {
      const question = button.dataset.question;
      const value = button.dataset.value;

      if (question === "meaning" && value === "yes") {
        annotationCard.classList.add("stage-typing");
        requestAnimationFrame(() => {
          typingQuestion.scrollIntoView({ block: "nearest", behavior: "smooth" });
        });
        return;
      }

      if (question === "typing") {
        // app-v3's listener was registered first, so the answer is already in its
        // state by the time this handler runs.
        window.setTimeout(() => submitButton.click(), 0);
      }
    });
  });

  // A new task changes the Kannada text. Restore Q1 for the next item.
  if (kannadaText) {
    const observer = new MutationObserver(() => {
      annotationCard.classList.remove("stage-typing");
    });
    observer.observe(kannadaText, { childList: true, characterData: true, subtree: true });
  }
})();
