const form = document.querySelector("#loan-form");
const result = document.querySelector("#result");
const submitButton = form.querySelector(".submit-btn");
const originalButton = submitButton.innerHTML;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.hidden = true;
  submitButton.disabled = true;
  submitButton.innerHTML = '<span>◌</span> Checking your details…';
  const payload = Object.fromEntries(new FormData(form).entries());

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok || !data.success) throw new Error(data.error || "Prediction could not be completed.");

    const approved = data.prediction.toLowerCase().includes("approv") ||
      ["1", "yes", "y", "true"].includes(data.prediction.toLowerCase());
    result.className = "result" + (approved ? "" : " rejected");
    const probability = data.probability_supported && data.probability !== null
      ? `<p>Model confidence for this predicted class: <strong>${data.probability}%</strong></p>`
      : `<p>The model returned a prediction but does not provide probability scores.</p>`;
    result.innerHTML = `
      <span class="result-label">MODEL PREDICTION</span>
      <h3>${approved ? "✓" : "↗"} ${escapeHtml(data.prediction)}</h3>
      ${probability}
      <p class="result-warning">This is a machine-learning estimate, not a lender's final decision.</p>`;
    result.hidden = false;
    result.scrollIntoView({behavior: "smooth", block: "nearest"});
  } catch (error) {
    result.className = "result rejected";
    result.innerHTML = `<span class="result-label">UNABLE TO PREDICT</span><h3>Something needs attention</h3><p>${escapeHtml(error.message)}</p>`;
    result.hidden = false;
  } finally {
    submitButton.disabled = false;
    submitButton.innerHTML = originalButton;
  }
});

form.addEventListener("reset", () => {
  result.hidden = true;
  result.innerHTML = "";
  result.className = "result";
});

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}
