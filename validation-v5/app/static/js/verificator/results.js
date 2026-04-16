// app/static/js/verificator/results.js

// ─── Status ───────────────────────────────────────────────────────

const STATUS_COLORS = {
    unseen:      '#b0b8c1',
    viewed:      '#0078d4',
    in_progress: '#f59400',
    validated:   '#1e7d5a',
    to_remove:   '#d93025'
};

let currentId  = null;
let currentLi  = null;
let originalDesc = null;

function getStatus(id) {
    return localStorage.getItem('status_' + id) || 'unseen';
}

function saveStatus(id, status) {
    localStorage.setItem('status_' + id, status);
}

function applyDot(id) {
    const status = getStatus(id);
    document.querySelectorAll(`.status-dot[data-id="${id}"]`).forEach(dot => {
        dot.style.background = STATUS_COLORS[status];
    });
}

function initDots() {
    document.querySelectorAll('.status-dot').forEach(dot => {
        applyDot(dot.dataset.id);
    });
}

// ─── Meta tellers updaten ─────────────────────────────────────────

function updateMetaCounts() {
    const sectionCount    = document.querySelectorAll('.result-card').length;
    const suggestionCount = document.querySelectorAll('.suggestion-item').length;

    const metaSections    = document.getElementById('metaSectionCount');
    const metaSuggestions = document.getElementById('metaSuggestionCount');

    if (metaSections)    metaSections.textContent    = sectionCount;
    if (metaSuggestions) metaSuggestions.textContent = suggestionCount;
}

// ─── Description ─────────────────────────────────────────────────

function getDescription(id, fallback) {
    return localStorage.getItem('desc_' + id) ?? fallback;
}

function saveDescription(id, text) {
    localStorage.setItem('desc_' + id, text);
}

// ─── Custom suggesties ────────────────────────────────────────────

function getCustomSuggestions(section) {
    const raw = localStorage.getItem('custom_' + section);
    return raw ? JSON.parse(raw) : [];
}

function saveCustomSuggestions(section, list) {
    localStorage.setItem('custom_' + section, JSON.stringify(list));
}

// ─── Custom secties ───────────────────────────────────────────────

function getCustomSections() {
    const raw = localStorage.getItem('custom_sections');
    return raw ? JSON.parse(raw) : [];
}

function saveCustomSections(list) {
    localStorage.setItem('custom_sections', JSON.stringify(list));
}

// ─── Suggestion item aanmaken ─────────────────────────────────────

function createSuggestionItem(id, title, description, source, isCustom) {
    const li = document.createElement('li');
    li.className      = 'suggestion-item';
    li.dataset.id     = id;
    li.dataset.title  = title;
    li.dataset.description = description;
    li.dataset.source = source || '';
    li.dataset.custom = isCustom ? 'true' : 'false';

    const dot = document.createElement('span');
    dot.className    = 'status-dot';
    dot.dataset.id   = id;

    const titleSpan = document.createElement('span');
    titleSpan.className   = 'suggestion-title';
    titleSpan.textContent = title;

    li.append(dot, titleSpan);

    if (isCustom) {
        const badge = document.createElement('span');
        badge.className   = 'badge-custom';
        badge.textContent = 'Custom';
        li.appendChild(badge);
    }

    li.addEventListener('click', () => openDrawer(li));
    applyDot(id);
    return li;
}

// ─── Card body aanmaken (voor nieuwe secties) ─────────────────────

function createCardBody() {
    const body = document.createElement('div');
    body.className = 'card-body';

    const list = document.createElement('ul');
    list.className = 'suggestions-list';

    const form = document.createElement('div');
    form.className = 'add-suggestion-form';
    form.style.display = 'none';
    form.innerHTML = `
        <input type="text" class="add-title-input" placeholder="Title…">
        <textarea class="add-desc-input" placeholder="Description…" rows="3"></textarea>
        <div class="add-form-actions">
            <button class="btn-add-confirm">Add</button>
            <button class="btn-add-cancel">Cancel</button>
        </div>
    `;

    const addBtn = document.createElement('button');
    addBtn.className   = 'btn-add-suggestion';
    addBtn.textContent = '＋ Add suggestion';

    body.append(list, form, addBtn);
    bindCardBodyEvents(body);
    return body;
}

// ─── Card aanmaken (nieuwe sectie) ───────────────────────────────

function createCard(section, isCustom) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.dataset.section       = section;
    card.dataset.customSection = isCustom ? 'true' : 'false';

    const header = document.createElement('div');
    header.className = 'result-card-header';
    header.innerHTML = `
        <h4>${section}</h4>
        <div class="header-right">
            <span class="badge-count">0</span>
            <span class="toggle-icon">▾</span>
            <button class="btn-delete-section" title="Delete section">🗑</button>
        </div>
    `;

    if (isCustom) {
        const badge = document.createElement('span');
        badge.className   = 'badge-custom-section';
        badge.textContent = 'Custom';
        header.querySelector('h4').insertAdjacentElement('afterend', badge);
    }

    const body = createCardBody();

    card.append(header, body);
    bindCardHeaderEvents(header);
    bindDeleteSectionEvent(header.querySelector('.btn-delete-section'), card, section, isCustom);

    return card;
}

// ─── Events binden aan card header ───────────────────────────────

function bindCardHeaderEvents(header) {
    header.addEventListener('click', (e) => {
        if (e.target.closest('.btn-delete-section')) return;
        toggleCard(header);
    });
}

// ─── Events binden aan card body ─────────────────────────────────

function bindCardBodyEvents(body) {
    const addBtn  = body.querySelector('.btn-add-suggestion');
    const form    = body.querySelector('.add-suggestion-form');
    const confirm = body.querySelector('.btn-add-confirm');
    const cancel  = body.querySelector('.btn-add-cancel');

    addBtn?.addEventListener('click', () => {
        form.style.display = 'flex';
        addBtn.style.display = 'none';
        form.querySelector('.add-title-input').focus();
    });

    cancel?.addEventListener('click', () => {
        form.style.display = 'none';
        addBtn.style.display = '';
        form.querySelector('.add-title-input').value = '';
        form.querySelector('.add-desc-input').value  = '';
    });

    confirm?.addEventListener('click', () => {
        const parentCard = body.closest('.result-card');
        const section    = parentCard?.dataset.section;
        const title      = form.querySelector('.add-title-input').value.trim();
        const desc       = form.querySelector('.add-desc-input').value.trim();

        if (!title) {
            form.querySelector('.add-title-input').focus();
            return;
        }

        const customs = getCustomSuggestions(section);
        const id      = section.replace(/\s+/g, '_') + '_custom_' + Date.now();
        customs.push({ id, title, description: desc });
        saveCustomSuggestions(section, customs);

        const list = body.querySelector('.suggestions-list');
        const li   = createSuggestionItem(id, title, desc, '', true);
        list.appendChild(li);

        updateBadgeCount(parentCard);
        updateMetaCounts(); // ← meta teller updaten

        form.style.display   = 'none';
        addBtn.style.display = '';
        form.querySelector('.add-title-input').value = '';
        form.querySelector('.add-desc-input').value  = '';
    });
}

// ─── Badge count updaten ──────────────────────────────────────────

function updateBadgeCount(card) {
    const badge = card.querySelector('.badge-count');
    if (!badge) return;
    const count = card.querySelectorAll('.suggestion-item').length;
    badge.textContent = count;
}

// ─── Sectie verwijderen ───────────────────────────────────────────

function bindDeleteSectionEvent(btn, card, section, isCustom) {
    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (!confirm(`Delete section "${section}"?`)) return;

        if (isCustom) {
            const customs = getCustomSections().filter(s => s !== section);
            saveCustomSections(customs);
            localStorage.removeItem('custom_' + section);
        }

        card.remove();
        updateMetaCounts(); // ← meta teller updaten
    });
}

// ─── Drawer ───────────────────────────────────────────────────────

function openDrawer(li) {
    currentId    = li.dataset.id;
    currentLi    = li;
    originalDesc = getDescription(currentId, li.dataset.description);

    const isCustom    = li.dataset.custom === 'true';
    const titleEl     = document.getElementById('drawerTitle');
    const titleInput  = document.getElementById('drawerTitleInput');
    const saveBtn     = document.getElementById('btnSaveDescription');

    // Titel: bewerkbaar voor custom, read-only voor origineel
    if (isCustom) {
        titleEl.style.display    = 'none';
        titleInput.style.display = '';
        titleInput.value         = li.dataset.title;
    } else {
        titleEl.style.display    = '';
        titleInput.style.display = 'none';
        titleEl.textContent      = li.dataset.title;
    }

    document.getElementById('drawerDescription').value = originalDesc;

    const source   = li.dataset.source;
    const sourceEl = document.getElementById('drawerSource');
    sourceEl.style.display = source ? '' : 'none';
    if (source) sourceEl.textContent = '"' + source + '"';

    // Save knop standaard uitgeschakeld
    saveBtn.disabled = true;

    if (getStatus(currentId) === 'unseen') {
        saveStatus(currentId, 'viewed');
        applyDot(currentId);
    }

    document.getElementById('drawer').classList.add('open');
    document.getElementById('drawerOverlay').classList.add('open');
}

function closeDrawer() {
    document.getElementById('drawer').classList.remove('open');
    document.getElementById('drawerOverlay').classList.remove('open');
    currentId    = null;
    currentLi    = null;
    originalDesc = null;
}

// ─── Suggestie verwijderen ────────────────────────────────────────

function deleteSuggestion() {
    if (!currentLi) return;

    const isCustom  = currentLi.dataset.custom === 'true';
    const id        = currentLi.dataset.id;
    const card      = currentLi.closest('.result-card');
    const section   = card?.dataset.section;

    if (isCustom && section) {
        const customs = getCustomSuggestions(section).filter(s => s.id !== id);
        saveCustomSuggestions(section, customs);
    }

    localStorage.removeItem('status_' + id);
    localStorage.removeItem('desc_'   + id);

    currentLi.remove();
    updateBadgeCount(card);
    updateMetaCounts(); // ← meta teller updaten
    closeDrawer();
}

// ─── Toggle kaart ─────────────────────────────────────────────────

function toggleCard(header) {
    header.closest('.result-card').classList.toggle('collapsed');
}

// ─── Custom secties laden ─────────────────────────────────────────

function loadCustomSections() {
    const grid = document.getElementById('resultsGrid');
    getCustomSections().forEach(section => {
        const card = createCard(section, true);
        grid.appendChild(card);

        getCustomSuggestions(section).forEach(s => {
            const li = createSuggestionItem(s.id, s.title, s.description, '', true);
            card.querySelector('.suggestions-list').appendChild(li);
        });

        updateBadgeCount(card);
    });
    updateMetaCounts(); // ← na laden custom secties tellers bijwerken
}

// ─── Custom suggesties laden (bestaande secties) ──────────────────

function loadCustomSuggestions() {
    document.querySelectorAll('.result-card[data-section]').forEach(card => {
        const section = card.dataset.section;
        const list    = card.querySelector('.suggestions-list');
        if (!list) return;

        getCustomSuggestions(section).forEach(s => {
            const li = createSuggestionItem(s.id, s.title, s.description, '', true);
            list.appendChild(li);
        });

        updateBadgeCount(card);
    });
    updateMetaCounts(); // ← na laden custom suggesties tellers bijwerken
}

// ─── Add section modal ────────────────────────────────────────────

function openModal() {
    document.getElementById('addSectionModal').classList.add('open');
    document.getElementById('modalOverlay').classList.add('open');
    document.getElementById('sectionNameInput').focus();
}

function closeModal() {
    document.getElementById('addSectionModal').classList.remove('open');
    document.getElementById('modalOverlay').classList.remove('open');
    document.getElementById('sectionNameInput').value = '';
}

function confirmAddSection() {
    const name = document.getElementById('sectionNameInput').value.trim();
    if (!name) {
        document.getElementById('sectionNameInput').focus();
        return;
    }

    const customs = getCustomSections();
    customs.push(name);
    saveCustomSections(customs);

    const card = createCard(name, true);
    document.getElementById('resultsGrid').appendChild(card);

    updateMetaCounts(); // ← meta teller updaten
    closeModal();
}

// ─── PDF export ───────────────────────────────────────────────────

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function loadHtml2Pdf() {
    return new Promise(resolve => {
        if (window.html2pdf) { resolve(); return; }
        const s = document.createElement("script");
        s.src = "https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js";
        s.onload = resolve;
        document.head.appendChild(s);
    });
}

const confirmBtn = document.getElementById("confirmBtn");

confirmBtn?.addEventListener("click", async () => {
    confirmBtn.disabled = true;
    confirmBtn.textContent = "Generating PDF…";

    let overlay = document.getElementById("pdfOverlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "pdfOverlay";
        overlay.style.cssText = `
            position:fixed;inset:0;background:rgba(255,255,255,0.85);
            display:flex;flex-direction:column;align-items:center;
            justify-content:center;gap:14px;z-index:9999;font-family:Arial,sans-serif;
        `;
        overlay.innerHTML = `
            <div style="width:36px;height:36px;border:3px solid #ccc;border-top-color:#0078d4;border-radius:50%;animation:spin 0.8s linear infinite;"></div>
            <span style="font-size:11pt;color:#555;">Generating PDF…</span>
            <style>@keyframes spin{to{transform:rotate(360deg);}}</style>
        `;
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = "flex";
    }

    await loadHtml2Pdf();

    const sections = [];
    document.querySelectorAll(".result-card").forEach(card => {
        const section = card.querySelector(".result-card-header h4")?.textContent.trim();
        if (!section) return;
        const items = [...card.querySelectorAll(".suggestion-item")]
            .map(el => el.querySelector('.suggestion-title')?.textContent.trim())
            .filter(Boolean);
        if (items.length > 0) sections.push({ section, items });
    });

    const totalCount = sections.reduce((sum, s) => sum + s.items.length, 0);
    const dateStr    = new Date().toLocaleDateString("en-GB", { day:"2-digit", month:"long", year:"numeric" });

    const wrapper = document.createElement("div");
    wrapper.style.cssText = "position:relative;width:210mm;margin:0;padding:0;";
    wrapper.innerHTML = `
        <div class="pdf-root">
            <div style="border-bottom:3px solid #005a9e;padding-bottom:18pt;margin-bottom:28pt;">
                <p style="font-size:8pt;letter-spacing:.18em;text-transform:uppercase;color:#0078d4;margin-bottom:10pt;">Pharma IT Validation · GAMP 5 Second Edition</p>
                <h1 style="font-size:26pt;font-weight:700;color:#1a1a2e;line-height:1.15;margin-bottom:6pt;">Compliance Review Report</h1>
                <p style="font-style:italic;font-size:11pt;color:#4a4a6a;margin-bottom:18pt;">Confirmed improvement suggestions after document analysis</p>
                <div style="display:flex;gap:28pt;">
                    <div style="display:flex;flex-direction:column;"><span style="font-size:7.5pt;color:#4a4a6a;">Date</span><span style="font-size:13pt;color:#4a4a6a;">${dateStr}</span></div>
                    <div style="display:flex;flex-direction:column;"><span style="font-size:7.5pt;color:#4a4a6a;">Sections</span><span style="font-size:13pt;">${sections.length}</span></div>
                    <div style="display:flex;flex-direction:column;"><span style="font-size:7.5pt;color:#4a4a6a;">Suggestions</span><span style="font-size:13pt;">${totalCount}</span></div>
                </div>
            </div>
            ${sections.map((s, i) => `
                <div style="margin-bottom:22pt;break-inside:avoid;">
                    <div style="display:flex;align-items:baseline;gap:10pt;border-bottom:1px solid #d0d8e8;padding-bottom:6pt;margin-bottom:10pt;">
                        <span style="font-size:9pt;font-weight:600;color:#0078d4;opacity:0.55;min-width:20pt;">${String(i+1).padStart(2,'0')}</span>
                        <h2 style="font-size:13pt;font-weight:600;color:#1a1a2e;flex:1;">${escapeHtml(s.section)}</h2>
                        <span style="font-size:8pt;color:#4a4a6a;font-style:italic;">${s.items.length} item${s.items.length!==1?'s':''}</span>
                    </div>
                    <ol style="list-style:none;padding-left:30pt;">
                        ${s.items.map(item => `
                            <li style="position:relative;padding:7pt 10pt 7pt 20pt;font-size:10pt;color:#1a1a2e;border-left:2.5px solid #0078d4;background:#f4f6fb;margin-bottom:5pt;border-radius:0 4pt 4pt 0;">
                                ${escapeHtml(item)}
                            </li>
                        `).join("")}
                    </ol>
                </div>
            `).join("")}
        </div>
    `;
    document.body.appendChild(wrapper);
    await new Promise(r => setTimeout(r, 500));

    await html2pdf()
        .set({
            margin: [12,14,12,14],
            filename: "GAMP5_Compliance_Report.pdf",
            image: { type:"jpeg", quality:0.97 },
            html2canvas: { scale:2, useCORS:true, letterRendering:true, scrollY:0 },
            jsPDF: { unit:"mm", format:"a4", orientation:"portrait" },
            pagebreak: { mode:["avoid-all","css"] }
        })
        .from(wrapper.querySelector(".pdf-root"))
        .save();

    document.body.removeChild(wrapper);
    overlay.style.display = "none";
    confirmBtn.disabled   = false;
    confirmBtn.textContent = "Confirm & Export";
});

// ─── DOMContentLoaded ─────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    initDots();
    loadCustomSuggestions();
    loadCustomSections();

    // Suggesties openen (originele)
    document.querySelectorAll('.suggestion-item').forEach(li => {
        li.addEventListener('click', () => openDrawer(li));
    });

    // Delete section knoppen (originele secties)
    document.querySelectorAll('.btn-delete-section').forEach(btn => {
        const card    = btn.closest('.result-card');
        const section = card?.dataset.section;
        const isCustom = card?.dataset.customSection === 'true';
        bindDeleteSectionEvent(btn, card, section, isCustom);
    });

    // Card headers toggle (originele secties)
    document.querySelectorAll('.result-card-header').forEach(header => {
        bindCardHeaderEvents(header);
    });

    // Card body events (originele secties)
    document.querySelectorAll('.card-body').forEach(body => {
        bindCardBodyEvents(body);
    });

    // Drawer sluiten
    document.getElementById('drawerClose').addEventListener('click', closeDrawer);
    document.getElementById('drawerOverlay').addEventListener('click', closeDrawer);

    // Status knoppen
    document.querySelectorAll('.status-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (!currentId) return;
            saveStatus(currentId, btn.dataset.status);
            applyDot(currentId);
        });
    });

    document.getElementById('drawerDescription').addEventListener('input', () => {
        document.getElementById('btnSaveDescription').disabled = false;
    });
    document.getElementById('drawerTitleInput').addEventListener('input', () => {
        document.getElementById('btnSaveDescription').disabled = false;
    });

    document.getElementById('btnSaveDescription').addEventListener('click', () => {
        if (!currentId || !currentLi) return;

        const desc    = document.getElementById('drawerDescription').value;
        const isCustom = currentLi.dataset.custom === 'true';

        saveDescription(currentId, desc);

        if (isCustom) {
            const newTitle = document.getElementById('drawerTitleInput').value.trim();
            if (newTitle) {
                currentLi.dataset.title = newTitle;
                currentLi.querySelector('.suggestion-title').textContent = newTitle;

                const card    = currentLi.closest('.result-card');
                const section = card?.dataset.section;
                const customs = getCustomSuggestions(section);
                const item    = customs.find(s => s.id === currentId);
                if (item) {
                    item.title = newTitle;
                    saveCustomSuggestions(section, customs);
                }
            }
        }

        closeDrawer();
    });


    document.getElementById('btnCancelDescription').addEventListener('click', closeDrawer);

    // Add section
    document.getElementById('btnAddSection').addEventListener('click', openModal);
    document.getElementById('modalClose').addEventListener('click', closeModal);
    document.getElementById('modalCancel').addEventListener('click', closeModal);
    document.getElementById('modalOverlay').addEventListener('click', closeModal);
    document.getElementById('modalConfirm').addEventListener('click', confirmAddSection);

    // Enter in modal input
    document.getElementById('sectionNameInput').addEventListener('keydown', e => {
        if (e.key === 'Enter') confirmAddSection();
    });
});