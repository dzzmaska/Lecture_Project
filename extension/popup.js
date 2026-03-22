const fileInput = document.getElementById("audioFile");
const fileLabel = document.getElementById("fileLabel");
const btn = document.getElementById("summarizeBtn");
const output = document.getElementById("outputText");
const loading = document.getElementById("loading");

let selectedFile = null;

// When user selects file
fileInput.addEventListener("change", () => {
  selectedFile = fileInput.files[0];
  if (selectedFile) {
    fileLabel.innerText = selectedFile.name;
  }
});

btn.addEventListener("click", async () => {
  if (!selectedFile) {
    output.innerText = "Please upload an MP3 file.";
    return;
  }

  loading.classList.remove("hidden");
  output.innerText = "";

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch("http://127.0.0.1:8000/summarize", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    output.innerText = data.summary;

  } catch (err) {
    output.innerText = "Error processing audio.";
  }

  loading.classList.add("hidden");
});