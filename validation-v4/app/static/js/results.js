// app\static\js\results.js

const activeCountEl    = document.getElementById("activeCount");
const dismissedCountEl = document.getElementById("dismissedCount");
const confirmCountEl   = document.getElementById("confirmCount");
const confirmBtn       = document.getElementById("confirmBtn");

let totalActive    = parseInt(activeCountEl?.textContent || "0");
let totalDismissed = 0;

// ── Helper function to escape HTML ───────────────────────────────
function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// ── Click to dismiss / restore suggestions ───────────────────────
document.querySelectorAll(".suggestion-item").forEach(item => {
    item.addEventListener("click", () => {
        const isDismissed = item.classList.toggle("dismissed");

        totalActive    += isDismissed ? -1 : 1;
        totalDismissed += isDismissed ?  1 : -1;

        // Update badge on card
        const card = item.closest(".result-card");
        const badge = card?.querySelector(".badge-count");
        if (badge) {
            const activeCount = card.querySelectorAll(".suggestion-item:not(.dismissed)").length;
            badge.textContent = activeCount;
            badge.style.background = activeCount === 0 ? "#aaa" : "";
        }

        // Update meta counters
        activeCountEl.textContent    = totalActive;
        dismissedCountEl.textContent = totalDismissed;
        confirmCountEl.textContent   = totalActive;
    });
});

// ── Load html2pdf.js from CDN if needed ─────────────────────────
function loadHtml2Pdf() {
    return new Promise(resolve => {
        if (window.html2pdf) { resolve(); return; }
        const s = document.createElement("script");
        s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js";
        s.onload = resolve;
        document.head.appendChild(s);
    });
}

// ── Confirm & Export PDF ────────────────────────────────────────
confirmBtn?.addEventListener("click", async () => {
    if (!confirmBtn) return;

    confirmBtn.disabled = true;
    confirmBtn.textContent = "Generating PDF…";

    // Show overlay
    let overlay = document.getElementById("pdfOverlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "pdfOverlay";
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            background: rgba(255,255,255,0.85);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 14px;
            z-index: 9999;
            font-family: Arial, sans-serif;
        `;
        overlay.innerHTML = `
            <div style="width:36px; height:36px; border:3px solid #ccc; border-top-color:#0078d4; border-radius:50%; animation:spin 0.8s linear infinite;"></div>
            <span style="font-size:11pt; color:#555;">Generating PDF…</span>
            <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = "flex";
    }

    // Load html2pdf
    await loadHtml2Pdf();

    // Collect active suggestions per section
    const sections = [];
    document.querySelectorAll(".result-card").forEach(card => {
        const section = card.querySelector(".result-card-header h4")?.textContent.trim();
        if (!section) return;

        const items = [...card.querySelectorAll(".suggestion-item:not(.dismissed)")]
            .map(el => el.textContent.trim());

        if (items.length > 0) sections.push({ section, items });
    });

    const totalCount = sections.reduce((sum, s) => sum + s.items.length, 0);
    const dateStr = new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "long", year: "numeric" });

    // Create offscreen wrapper for PDF
    const wrapper = document.createElement("div");
    wrapper.style.cssText = "position: relative; width:210mm; margin:0; padding:0;";
    wrapper.innerHTML = `
        <div class="pdf-root">
            <!-- Cover -->
            <div class="cover" style="border-bottom:3px solid #005a9e; padding-bottom:18pt; margin-bottom:28pt;">
                <p class="cover-eyebrow" style="font-size:8pt; letter-spacing:.18em; text-transform:uppercase; color:#0078d4; margin-bottom:10pt;">Pharma IT Validation · GAMP 5 Second Edition</p>
                <h1 class="cover-title" style="font-family:'Playfair Display', serif; font-size:26pt; font-weight:700; color:#1a1a2e; line-height:1.15; margin-bottom:6pt;">Compliance Review Report</h1>
                <p class="cover-sub" style="font-style:italic; font-size:11pt; color:#4a4a6a; margin-bottom:18pt;">Confirmed improvement suggestions after document analysis</p>
                <div class="cover-meta" style="display:flex; gap:28pt;">
                    <div class="meta-cell" style="display:flex; flex-direction:column;">
                        <span class="meta-label" style="font-size:7.5pt; color:#4a4a6a;">Date</span>
                        <span class="meta-value" style="font-size:13pt; color:#4a4a6a;">${dateStr}</span>
                    </div>
                    <div class="meta-cell" style="display:flex; flex-direction:column;">
                        <span class="meta-label" style="font-size:7.5pt; color:#4a4a6a;">Sections</span>
                        <span class="meta-value">${sections.length}</span>
                    </div>
                    <div class="meta-cell" style="display:flex; flex-direction:column;">
                        <span class="meta-label" style="font-size:7.5pt; color:#4a4a6a;">Suggestions</span>
                        <span class="meta-value">${totalCount}</span>
                    </div>
                </div>
            </div>

            <!-- Sections -->
            ${sections.map((s,i) => `
                <div class="section-block" style="margin-bottom:22pt; break-inside:avoid;">
                    <div class="section-header" style="display:flex; align-items:baseline; gap:10pt; border-bottom:1px solid #d0d8e8; padding-bottom:6pt; margin-bottom:10pt;">
                        <span class="section-index" style="font-family:'Playfair Display', serif; font-size:9pt; font-weight:600; color:#0078d4; opacity:0.55; min-width:20pt;">${String(i+1).padStart(2,'0')}</span>
                        <h2 class="section-title" style="font-family:'Playfair Display', serif; font-size:13pt; font-weight:600; color:#1a1a2e; flex:1;">${escapeHtml(s.section)}</h2>
                        <span class="section-count" style="font-size:8pt; color:#4a4a6a; font-style:italic; flex-shrink:0;">${s.items.length} item${s.items.length!==1?'s':''}</span>
                    </div>
                    <ol class="suggestion-list" style="list-style:none; padding-left:30pt; counter-reset:list-item;">
                        ${s.items.map(item => `<li style="position:relative; padding:7pt 10pt 7pt 20pt; font-size:10pt; color:#1a1a2e; border-left:2.5px solid #0078d4; background:#f4f6fb; margin-bottom:5pt; border-radius:0 4pt 4pt 0;">${escapeHtml(item)}</li>`).join("")}
                    </ol>
                </div>
            `).join("")}
        </div>
    `;
    document.body.appendChild(wrapper);

    // Small delay to ensure fonts/layout are ready
    await new Promise(r => setTimeout(r, 500));

    await html2pdf()
        .set({
            margin: [12,14,12,14],
            filename: "GAMP5_Compliance_Report.pdf",
            image: { type: "jpeg", quality: 0.97 },
            html2canvas: { scale:2, useCORS:true, letterRendering:true, scrollY:0 },
            jsPDF: { unit:"mm", format:"a4", orientation:"portrait" },
            pagebreak: { mode:["avoid-all","css"] }
        })
        .from(wrapper.querySelector(".pdf-root"))
        .save();

    // Cleanup
    document.body.removeChild(wrapper);
    overlay.style.display = "none";
    confirmBtn.disabled = false;
    confirmBtn.textContent = "Confirm & Export";
});