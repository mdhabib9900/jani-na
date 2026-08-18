const generateBtn = document.getElementById("generateBtn");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const emptyState = document.getElementById("emptyState");
const downloadLink = document.getElementById("download");

function setStatus(text, error = false) {
  statusEl.textContent = text;
  statusEl.style.color = error ? "#ff7b72" : "#9ecbff";
}

generateBtn.addEventListener("click", async () => {
  const payload = {
    prompt: document.getElementById("prompt").value,
    negative_prompt: document.getElementById("negativePrompt").value,
    model: document.getElementById("model").value,
    size: document.getElementById("size").value,
    output_format: document.getElementById("outputFormat").value,
    seed: document.getElementById("seed").value,
  };

  setStatus("Generating image with Pollinations.ai...");
  generateBtn.disabled = true;

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Generation failed");
    }

    const mime = data.mime_type || "image/jpeg";
    const src = data.image_data
      ? `data:${mime};base64,${data.image_data}`
      : data.image_url;
    resultEl.src = src;
    resultEl.classList.remove("hidden");
    emptyState.classList.add("hidden");

    downloadLink.href = data.image_url || src;
    downloadLink.download = data.filename;
    downloadLink.classList.remove("hidden");

    setStatus(data.message);
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    generateBtn.disabled = false;
  }
});
