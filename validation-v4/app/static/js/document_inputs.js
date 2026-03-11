/**
 * document_inputs.js
 *
 * Purpose:
 * - Handle the "Specific Inputs" page:
 *   - Click on a card -> open modal
 *   - Edit table rows/cells (textarea, static @...@, toggle #...#)
 *   - Optional wizard for grouped tables (Next/Previous)
 *   - Dynamic tables: add/delete rows + max row enforcement
 *   - Persist user-edited data into window.sectionData
 *   - On Generate: serialize window.sectionData into hidden input "table_data"
 *   - Show loading indicator and rotate loading messages (adaptive pacing)
 *
 * Compatibility:
 * - Does NOT change the JSON shape of window.sectionData.
 * - Does NOT change form submission mechanism.
 * - Keeps the same modal IDs and button IDs.
 * - Removes only debug code and improves robustness / maintainability.
 */

document.addEventListener("DOMContentLoaded", () => {
  // ---------------------------------------------------------------------------
  // Safe JSON parsing
  // ---------------------------------------------------------------------------
  /**
   * @param {string} raw
   * @param {any} fallback
   * @returns {any}
   */
  function safeJsonParse(raw, fallback) {
    try {
      return JSON.parse(raw);
    } catch {
      return fallback;
    }
  }

  /** @type {HTMLElement|null} */
  const tableDataScript = document.getElementById("table-data");
  /** @type {HTMLElement|null} */
  const tableMetaScript = document.getElementById("table-meta");

  // Keep these names stable conceptually; internal variable names can differ.
  const tablesBySection = safeJsonParse(tableDataScript?.textContent || "{}", {});
  const metaBySection = safeJsonParse(tableMetaScript?.textContent || "{}", {});

  // Preserve original global contract
  window.sectionData = window.sectionData || {};

  // ---------------------------------------------------------------------------
  // DOM references
  // ---------------------------------------------------------------------------
  /** @type {HTMLElement|null} */
  const modal = document.getElementById("tableModal");
  /** @type {HTMLElement|null} */
  const modalTitle = document.getElementById("modalTitle");
  /** @type {HTMLElement|null} */
  const modalBody = document.getElementById("modalBody");
  /** @type {HTMLInputElement|null} */
  const tableDataInput = document.getElementById("tableDataInput");
  /** @type {HTMLFormElement|null} */
  const generateForm = document.getElementById("generateForm");
  /** @type {HTMLElement|null} */
  const loadingEl = document.getElementById("loadingIndicator");

  if (!modal || !modalTitle || !modalBody || !tableDataInput || !generateForm) {
    // Page not matching expected DOM structure → do nothing safely.
    return;
  }

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  const state = {
    currentSection: /** @type {string|null} */ (null),

    // wizard-only state (grouped tables)
    wizardGroups: /** @type {Array<[string, any]>} */ ([]),
    wizardIndex: 0,

    // current section meta flags
    isDynamic: false,
    isGrouped: false,
  };

  // ---------------------------------------------------------------------------
  // Loading messages (adaptive pacing)
  // ---------------------------------------------------------------------------
  const uiCfg = JSON.parse(
    document.getElementById("generator-ui-config")?.textContent || "{}"
  );

  const LOADING_MESSAGES = uiCfg.loadingMessages || [];
  const TERMINAL_COUNT = uiCfg.loadingTerminalCount || 0;
  const MAX_TIME_MS = (uiCfg.loadingMaxTimeSec || 60) * 1000;

  const ROTATING_COUNT = Math.max(LOADING_MESSAGES.length - TERMINAL_COUNT, 1);
  const ESTIMATED_DURATION_MS = MAX_TIME_MS;


  let loadingTimeout = null;

  /**
   * Start adaptive rotating messages.
   * This is safe even if the generation takes longer than expected.
   *
   * @param {{
   *  messages: string[],
   *  estimatedDurationMs: number,
   *  fadeMs?: number,
   *  minIntervalMs?: number,
   *  maxSlowdown?: number
   * }} cfg
   */
  function startLoadingMessagesAdaptive(cfg) {
    const textEl = document.getElementById("loadingText");
    if (!textEl) return;

    const messages = cfg.messages;
    if (!Array.isArray(messages) || messages.length === 0) return;

    const estimatedDurationMs = cfg.estimatedDurationMs;
    const fadeMs = cfg.fadeMs ?? 500;
    const minIntervalMs = cfg.minIntervalMs ?? 2000;
    const maxSlowdown = cfg.maxSlowdown ?? 1.6;

    if (loadingTimeout) {
      clearTimeout(loadingTimeout);
      loadingTimeout = null;
    }

    let index = 0;
    const maxIndex = messages.length - 1;

    const baseInterval = Math.max(
      estimatedDurationMs / ROTATING_COUNT,
      minIntervalMs
    );

    const scheduleNext = () => {
      if (index >= maxIndex) return;

      const progressRatio = index / ROTATING_COUNT;
      const slowdownFactor = 1 + progressRatio * (maxSlowdown - 1);
      const interval = baseInterval * slowdownFactor;

      textEl.style.opacity = "0";

      window.setTimeout(() => {
        index++;
        textEl.textContent = messages[index];
        textEl.style.opacity = "1";
        loadingTimeout = window.setTimeout(scheduleNext, interval);
      }, fadeMs);
    };

    // message initial
    textEl.textContent = messages[0];
    loadingTimeout = window.setTimeout(scheduleNext, baseInterval);
  }

  // avoid timer leak if user leaves page
  window.addEventListener("pagehide", () => {
    if (loadingTimeout) clearTimeout(loadingTimeout);
    loadingTimeout = null;
  });

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------
  /**
   * @param {any} v
   * @returns {boolean}
   */
  function isEmptyValue(v) {
    return v === null || v === undefined || (typeof v === "string" && v.trim() === "");
  }

  /**
   * Minimal HTML escape for safe innerHTML insertion
   * @param {any} str
   * @returns {string}
   */
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  /**
   * Convert snake_case keys to pretty UI label
   * @param {any} key
   * @returns {string}
   */
  function prettyLabel(key) {
    if (key === null || key === undefined) return "";
    return String(key)
      .replace(/[_\-]+/g, " ")
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  }

  function openModal() {
    modal.classList.remove("hidden");
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  function autoResizeTextareas() {
    modal.querySelectorAll("textarea").forEach((t) => {
      t.style.height = "39px";
      t.style.height = Math.max(t.scrollHeight + 2, 39) + "px";
    });
  }

  function markFilledInputs() {
    modal.querySelectorAll("textarea").forEach((t) => {
      t.classList.toggle("input-filled", t.value.trim() !== "");
    });
  }

  /**
   * Determines if a section has any content, then toggles the "filled" class on the card.
   * Keeps same behavior as original.
   * @param {string} section
   */
  function updateCardStyles(section) {
    const card = document.querySelector(`.card[data-section="${CSS.escape(section)}"]`);
    if (!card) return;

    const data = window.sectionData[section];
    let filled = false;

    if (Array.isArray(data)) {
      filled = data.some((r) => Object.values(r).some((v) => !isEmptyValue(v)));
    } else if (data && typeof data === "object") {
      // grouped object: { groupKey: [rows], ... }
      filled = Object.values(data).some((rows) =>
        Array.isArray(rows) &&
        rows.some((r) => Object.values(r).some((v) => !isEmptyValue(v)))
      );
    }

    card.classList.toggle("filled", filled);
  }

  /**
   * Update Add Row button state according to max_rows.
   * @param {HTMLButtonElement|null} addRowBtn
   * @param {HTMLTableSectionElement|null} tbody
   * @param {number|null} maxRows
   */
  function updateAddRowButtonState(addRowBtn, tbody, maxRows) {
    if (!addRowBtn || maxRows === null || !tbody) return;

    const count = tbody.querySelectorAll("tr").length;

    if (count >= maxRows) {
      addRowBtn.disabled = true;
      addRowBtn.classList.add("btn-disabled");
      addRowBtn.textContent = "Max rows reached";
    } else {
      addRowBtn.disabled = false;
      addRowBtn.classList.remove("btn-disabled");
      addRowBtn.textContent = "➕ Add Row";
    }
  }

  /**
   * Get section meta
   * @param {string} section
   * @returns {{dynamic?: boolean, grouped?: boolean, max_rows?: number|null, order?: string[]}}
   */
  function getSectionMeta(section) {
    const meta = metaBySection?.[section] || {};
    return meta;
  }

  /**
   * Get the raw data for a section (prefer user's edits over default tables)
   * @param {string} section
   * @returns {any}
   */
  function getSectionDataForModal(section) {
    // If user already edited, use that; otherwise default TABLES
    return window.sectionData?.[section] ?? tablesBySection?.[section];
  }

  // ---------------------------------------------------------------------------
  // Modal Builders
  // ---------------------------------------------------------------------------
  /**
   * Build modal content based on the current section.
   * Sets wizard state if grouped.
   * @param {any} data
   * @param {boolean} isDynamic
   * @param {boolean} isGrouped
   * @returns {string}
   */
  function buildModalContent(data, isDynamic, isGrouped) {
    if (!data) return "<p>No data available.</p>";

    if (!isGrouped) {
      return buildTable(data, isDynamic) + buildFooter(isDynamic, false);
    }

    // Grouped: data must be object {groupKey: rows[]}
    state.wizardGroups = Object.entries(data);
    state.wizardIndex = 0;

    return renderWizardStep(isDynamic);
  }

  /**
   * Render current wizard step for grouped table.
   * @param {boolean} isDynamic
   * @returns {string}
   */
  function renderWizardStep(isDynamic) {
    const entry = state.wizardGroups[state.wizardIndex];
    if (!entry) return "<p>No data available.</p>";

    const [groupKey, rows] = entry;

    let html = `
      <h3 class="modal-subtitle">${escapeHtml(prettyLabel(groupKey))}</h3>
      ${buildTable(rows, isDynamic)}
    `;

    html += buildFooter(isDynamic, true);
    return html;
  }

  /**
   * Build a table HTML.
   * Uses meta.order if present; else uses first row keys.
   * @param {any} rows
   * @param {boolean} isDynamic
   * @returns {string}
   */
  function buildTable(rows, isDynamic) {
    if (!Array.isArray(rows) || rows.length === 0) {
      return "<p>No data available.</p>";
    }

    const meta = getSectionMeta(state.currentSection || "");
    const headers = Array.isArray(meta.order) && meta.order.length > 0
      ? meta.order
      : Object.keys(rows[0] || {});

    const thead = `
      <thead>
        <tr>
          ${headers.map((h) => `<th>${escapeHtml(prettyLabel(h))}</th>`).join("")}
          ${isDynamic ? `<th style="width:40px;"></th>` : ""}
        </tr>
      </thead>
    `;

    const tbody = rows
      .map((r, i) => {
        const cols = headers
          .map((k) => `<td data-col-key="${escapeHtml(k)}">${renderCell(r?.[k], k)}</td>`)
          .join("");

        const del = isDynamic ? `<td><button class="delete-row-btn" type="button" aria-label="Delete row">🗑️</button></td>` : "";
        return `<tr data-row="${i}">${cols}${del}</tr>`;
      })
      .join("");

    return `
      <div class="modal-table-container">
        <table class="modal-table">
          ${thead}
          <tbody class="modalTableBody">${tbody}</tbody>
        </table>
      </div>
    `;
  }

  /**
   * Build modal footer (buttons).
   * Keeps original button IDs for compatibility with existing CSS/behavior.
   * @param {boolean} isDynamic
   * @param {boolean} isWizard
   * @returns {string}
   */
  function buildFooter(isDynamic, isWizard) {
    const isFirst = state.wizardIndex === 0;
    const isLast = state.wizardIndex === state.wizardGroups.length - 1;

    return `
      <div class="modal-footer">
        <div class="modal-footer-left">
          ${isDynamic ? `<button id="addRowBtn" class="btn-secondary" type="button">➕ Add Row</button>` : ""}
        </div>
        <div class="modal-footer-right">
          ${isWizard && !isFirst ? `<button id="prevBtn" class="btn-secondary" type="button">← Previous</button>` : ""}
          ${isWizard && !isLast ? `<button id="nextBtn" class="btn-primary" type="button">Next →</button>` : ""}
          ${(!isWizard || isLast) ? `<button id="saveBtn" class="btn-primary" type="button">Save</button>` : ""}
          <button id="cancelBtn" class="btn-secondary" type="button">Cancel</button>
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------------------
  // Cell rendering (@...@, #...#, [...] and text chunks)
  // ---------------------------------------------------------------------------
  /**
   * Render a table cell given a value and column key.
   * Rules:
   * - @...@ => static text (non-editable)
   * - #...# => toggle span, supports "<A>/<B>" format
   * - [...] => textarea with placeholder
   * - other text => textarea with initial content
   *
   * @param {any} value
   * @param {string} colKey
   * @returns {string}
   */
  function renderCell(value, colKey) {
    if (!value || typeof value !== "string") {
      return `<textarea data-key="${escapeHtml(colKey)}"></textarea>`;
    }

    const fragments = [];
    const pattern = /(@[^@]+@)|(#.+?#)|(\[[^\]]*])|([^\n@#\[\]]+)/g;
    let m;

    while ((m = pattern.exec(value)) !== null) {
      const at = m[1];
      const hash = m[2];
      const square = m[3];
      const other = m[4];

      if (at) {
        fragments.push(
          `<div class="static-cell" data-key="${escapeHtml(colKey)}">${escapeHtml(at.slice(1, -1).trim())}</div>`
        );
        continue;
      }

      if (hash) {
        const inside = hash.slice(1, -1);
        const mm = inside.match(/^<([^>]*)>\/<([^>]*)>$/);
        const A = (mm ? mm[1] : inside).trim();
        const B = (mm ? mm[2] : "").trim();

        fragments.push(
          `<span class="toggle-span"
                data-key="${escapeHtml(colKey)}"
                data-toggle-a="${escapeHtml(A)}"
                data-toggle-b="${escapeHtml(B)}">${escapeHtml(A)}</span>`
        );
        continue;
      }

      if (square) {
        fragments.push(
          `<textarea data-key="${escapeHtml(colKey)}"
                    placeholder="${escapeHtml(square.slice(1, -1))}"></textarea>`
        );
        continue;
      }

      if (other && other.trim()) {
        fragments.push(
          `<textarea data-key="${escapeHtml(colKey)}">${escapeHtml(other.trim())}</textarea>`
        );
      }
    }

    return fragments.join("") || `<textarea data-key="${escapeHtml(colKey)}"></textarea>`;
  }

  // ---------------------------------------------------------------------------
  // Data extraction + save logic
  // ---------------------------------------------------------------------------
  /**
   * Extract rows from tbody into an array of objects.
   * Keeps exact same behavior as original:
   * - If textarea exists: use its value
   * - else if toggle-span exists: use its text
   * - else if static-cell exists: use its text
   * - else empty string
   *
   * @param {HTMLTableSectionElement|null} tbody
   * @returns {Array<Record<string, string>>}
   */
  function extractRows(tbody) {
    const rows = [];
    if (!tbody) return rows;

    tbody.querySelectorAll("tr").forEach((tr) => {
      /** @type {Record<string, string>} */
      const row = {};

      tr.querySelectorAll("td[data-col-key]").forEach((td) => {
        const key = td.getAttribute("data-col-key") || "";
        if (!key) return;

        const textarea = td.querySelector("textarea");
        const toggle = td.querySelector(".toggle-span");
        const fixed = td.querySelector(".static-cell");

        row[key] =
          textarea?.value?.trim() ||
          toggle?.textContent?.trim() ||
          fixed?.textContent?.trim() ||
          "";
      });

      rows.push(row);
    });

    return rows;
  }

  function saveNonGrouped() {
    const tbody = modal.querySelector(".modalTableBody");
    if (!state.currentSection) return;
    window.sectionData[state.currentSection] = extractRows(tbody);
  }

  function saveWizardStep() {
    if (!state.currentSection) return;

    const entry = state.wizardGroups[state.wizardIndex];
    if (!entry) return;

    const [groupKey] = entry;
    const tbody = modal.querySelector(".modalTableBody");

    if (!window.sectionData[state.currentSection]) {
      window.sectionData[state.currentSection] = {};
    }

    window.sectionData[state.currentSection][groupKey] = extractRows(tbody);
  }

  // ---------------------------------------------------------------------------
  // UI refresh after rendering modal content
  // ---------------------------------------------------------------------------
  function refreshModalUi() {
    requestAnimationFrame(() => {
      autoResizeTextareas();
      markFilledInputs();

      const addRowBtn = /** @type {HTMLButtonElement|null} */ (document.getElementById("addRowBtn"));
      const tbody = /** @type {HTMLTableSectionElement|null} */ (modal.querySelector(".modalTableBody"));
      const maxRows = (metaBySection?.[state.currentSection || ""]?.max_rows ?? null);

      updateAddRowButtonState(addRowBtn, tbody, typeof maxRows === "number" ? maxRows : null);
    });
  }

  // ---------------------------------------------------------------------------
  // Open modal from card click (single handler)
  // ---------------------------------------------------------------------------
  document.querySelectorAll(".card").forEach((card) => {
    card.addEventListener("click", () => {
      const section = card.getAttribute("data-section");
      if (!section) return;

      state.currentSection = section;

      const meta = getSectionMeta(section);
      state.isDynamic = meta.dynamic === true;
      state.isGrouped = meta.grouped === true;

      const data = getSectionDataForModal(section);

      modalTitle.textContent = prettyLabel(section);
      modalBody.innerHTML = buildModalContent(data, state.isDynamic, state.isGrouped);

      openModal();
      refreshModalUi();
    });
  });

  // ---------------------------------------------------------------------------
  // Modal event delegation (IMPORTANT: registered ONCE)
  // ---------------------------------------------------------------------------
  // INPUT: textarea typing -> resize + filled class
  // KEYDOWN: Tab injects placeholder into empty table cells
  modal.addEventListener("keydown", (e) => {
    const target = e.target;
    if (!(target instanceof HTMLTextAreaElement)) return;
    if (e.key !== "Tab") return;

    // Only inject if empty and placeholder exists
    const current = target.value.trim();
    const ph = (target.getAttribute("placeholder") || "").trim();
    if (!current && ph) {
      // Put placeholder as requested
      target.value = `${ph}`;

      // Update UI feedback immediately
      target.classList.add("input-filled");
      autoResizeTextareas();
    }
  });

  // CLICK: buttons + toggles + delete row
  modal.addEventListener("click", (e) => {
    const target = /** @type {HTMLElement|null} */ (e.target instanceof HTMLElement ? e.target : null);
    if (!target) return;

    // Toggle-span click
    const toggle = target.closest(".toggle-span");
    if (toggle) {
      const A = toggle.getAttribute("data-toggle-a") || "";
      const B = toggle.getAttribute("data-toggle-b") || "";
      const current = (toggle.textContent || "").trim();

      toggle.textContent = current === A ? B : A;
      return;
    }

    // Cancel
    if (target.id === "cancelBtn") {
      closeModal();
      return;
    }

    // Save
    if (target.id === "saveBtn") {
      if (!state.currentSection) return;

      if (state.isGrouped) saveWizardStep();
      else saveNonGrouped();

      closeModal();
      updateCardStyles(state.currentSection);
      return;
    }

    // Next (wizard)
    if (target.id === "nextBtn") {
      if (!state.isGrouped) return;

      saveWizardStep();

      state.wizardIndex = Math.min(state.wizardIndex + 1, state.wizardGroups.length - 1);
      modalBody.innerHTML = renderWizardStep(state.isDynamic);
      refreshModalUi();
      return;
    }

    // Previous (wizard)
    if (target.id === "prevBtn") {
      if (!state.isGrouped) return;

      saveWizardStep();

      state.wizardIndex = Math.max(state.wizardIndex - 1, 0);
      modalBody.innerHTML = renderWizardStep(state.isDynamic);
      refreshModalUi();
      return;
    }

    // Delete row
    if (target.classList.contains("delete-row-btn")) {
      const tr = target.closest("tr");
      const tbody = target.closest("tbody");
      if (tr) tr.remove();

      const addRowBtn = /** @type {HTMLButtonElement|null} */ (document.getElementById("addRowBtn"));
      const maxRows = (metaBySection?.[state.currentSection || ""]?.max_rows ?? null);
      updateAddRowButtonState(addRowBtn, /** @type {HTMLTableSectionElement|null} */ (tbody), typeof maxRows === "number" ? maxRows : null);
      return;
    }

    // Add row
    if (target.id === "addRowBtn") {
      if (!state.isDynamic || !state.currentSection) return;

      const tbody = /** @type {HTMLTableSectionElement|null} */ (modal.querySelector(".modalTableBody"));
      if (!tbody) return;

      const maxRows = (metaBySection?.[state.currentSection]?.max_rows ?? null);
      const max = typeof maxRows === "number" ? maxRows : null;

      if (max !== null && tbody.children.length >= max) {
        updateAddRowButtonState(/** @type {HTMLButtonElement|null} */ (target), tbody, max);
        return;
      }

      const meta = getSectionMeta(state.currentSection);
      const headers = Array.isArray(meta.order) ? meta.order : [];

      const tr = document.createElement("tr");
      tr.innerHTML =
        headers
          .map(
            (k) => `<td data-col-key="${escapeHtml(k)}"><textarea data-key="${escapeHtml(k)}"></textarea></td>`
          )
          .join("") +
        `<td><button class="delete-row-btn" type="button" aria-label="Delete row">🗑️</button></td>`;

      tbody.appendChild(tr);
      refreshModalUi();

      updateAddRowButtonState(
        /** @type {HTMLButtonElement|null} */ (document.getElementById("addRowBtn")),
        tbody,
        max
      );

      return;
    }
  });

  // ESC key closes modal (UX)
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });

  // ---------------------------------------------------------------------------
  // Submit: serialize sectionData + show loading
  // ---------------------------------------------------------------------------
  generateForm.addEventListener("submit", () => {
    // Keep exactly same output: JSON string
    tableDataInput.value = JSON.stringify(window.sectionData);

    if (loadingEl) loadingEl.style.display = "flex";

    const actionButtons = document.querySelector(".action-buttons");
    if (actionButtons) actionButtons.style.display = "none";

    startLoadingMessagesAdaptive({
      messages: LOADING_MESSAGES,
      estimatedDurationMs: ESTIMATED_DURATION_MS,
      fadeMs: 200,
      minIntervalMs: 1800,
      maxSlowdown: 1.6,
    });
  });
});