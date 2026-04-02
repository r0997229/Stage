// app/static/js/verificator/verificator.js

const zone         = document.getElementById("uploadZone");
const fileInput    = document.getElementById("document");
const fileError    = document.getElementById("fileError");
const form         = document.getElementById("verificatorForm");
const submitBtn    = document.getElementById("submitBtn");
const trashBtn     = document.getElementById("trashBtn");
const fileChip     = document.getElementById("fileChip");
const fileChipName = document.getElementById("fileChipName");
const fileChipMeta = document.getElementById("fileChipMeta");
const fileChipIcon = document.getElementById("fileChipIcon");

// Vlag: is het bestandsvenster momenteel open?
let dialogOpen = false;

const ICONS = {
    pdf: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="9" y1="13" x2="15" y2="13"/>
            <line x1="9" y1="17" x2="12" y2="17"/>
          </svg>`,
    docx: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
             <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
             <polyline points="14 2 14 8 20 8"/>
             <line x1="9" y1="13" x2="15" y2="13"/>
             <line x1="9" y1="17" x2="15" y2="17"/>
             <line x1="9" y1="9" x2="11" y2="9"/>
           </svg>`,
};

function formatSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

function showChip(file) {
    const ext = file.name.split(".").pop().toLowerCase();

    // Valideer bestandstype
    if (ext !== "pdf" && ext !== "docx") {
        fileInput.value         = "";
        fileError.textContent   = "Only PDF or DOCX files are allowed.";
        fileError.style.display = "block";
        zone.classList.add("error");
        return; // stop hier, geen chip tonen
    }

    const type = ext === "pdf" ? "PDF" : "DOCX";

    fileChipName.textContent = file.name;
    fileChipMeta.textContent = `${type} · ${formatSize(file.size)}`;
    fileChipIcon.innerHTML   = ICONS[ext] || ICONS.pdf;
    fileChipIcon.style.background = ext === "pdf" ? "#e6f1fb" : "#eaf3de";
    fileChipIcon.querySelector("svg").style.stroke = ext === "pdf" ? "#0c447c" : "#27500a";

    zone.style.display      = "none";
    fileChip.classList.add("visible");

    zone.classList.remove("error");
    fileError.textContent   = "Please select a PDF or DOCX file.";
    fileError.style.display = "none";
    submitBtn.disabled      = false;
}

function showZone() {
    fileChip.classList.remove("visible");
    zone.style.display = "";

    fileInput.value    = "";
    submitBtn.disabled = true;
}

// Klik op zone → open file dialog (geblokkeerd als dialog al open is)
zone.addEventListener("click", () => {
    if (dialogOpen) return;
    dialogOpen = true;
    fileInput.click();
});

// Venster gesloten zonder keuze (Annuleren knop)
fileInput.addEventListener("cancel", () => {
    dialogOpen = false;
});

// Bestand gekozen via klik
fileInput.addEventListener("change", () => {
    dialogOpen = false;
    if (fileInput.files[0]) showChip(fileInput.files[0]);
});

// Vuilnisbak: reset naar upload zone
trashBtn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    showZone();
});

// Drag-and-drop — geblokkeerd als dialog open is
zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    if (dialogOpen) return;
    zone.classList.add("dragover");
});

zone.addEventListener("dragleave", () => {
    zone.classList.remove("dragover");
});

zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("dragover");
    if (dialogOpen) return;
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        fileInput.dispatchEvent(new Event("change"));
    }
});

// Validatie bij submit
form.addEventListener("submit", (e) => {
    if (!fileInput.files[0]) {
        e.preventDefault();
        zone.classList.add("error");
        fileError.textContent   = "Please select a PDF or DOCX file.";
        fileError.style.display = "block";
        return;
    }
    submitBtn.disabled    = true;
    submitBtn.textContent = "Analysing…";
});