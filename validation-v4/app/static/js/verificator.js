// app\static\js\verificator.js

const zone      = document.getElementById("uploadZone");
const fileInput = document.getElementById("document");
const fileLabel = document.getElementById("uploadFilename");
const fileError = document.getElementById("fileError");
const form      = document.getElementById("verificatorForm");
const submitBtn = document.getElementById("submitBtn");

// Show selected filename
fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file) {
        fileLabel.textContent = file.name;
        fileLabel.classList.add("visible");
        zone.classList.remove("error");
        fileError.style.display = "none";
    } else {
        fileLabel.classList.remove("visible");
    }
});

// Drag-and-drop visual feedback
zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("dragover");
});

zone.addEventListener("dragleave", () => {
    zone.classList.remove("dragover");
});

zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        fileInput.dispatchEvent(new Event("change"));
    }
});

// Validation on submit
form.addEventListener("submit", (e) => {
    const file = fileInput.files[0];
    if (!file) {
        e.preventDefault();
        zone.classList.add("error");
        fileError.style.display = "block";
        return;
    }

    // Loading state
    submitBtn.disabled = true;
    submitBtn.textContent = "Analysing…";
});