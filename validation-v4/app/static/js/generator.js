/**
 * document_inputs.js
 *
 * Purpose:
 * - Handle UI behavior for the "General Inputs" generator form:
 *   - Custom dropdown open/close + option selection
 *   - Visual feedback (border & shadow) when fields are filled
 *   - Prevent form submission if "Document Type" is not selected
 */

document.addEventListener("DOMContentLoaded", () => {
  /** @type {HTMLFormElement|null} */
  const form = document.getElementById("validationForm");
  if (!form) return;

  /** @type {NodeListOf<HTMLInputElement|HTMLTextAreaElement>} */
  const textInputs = form.querySelectorAll('input[type="text"], textarea');

  /** @type {NodeListOf<HTMLElement>} */
  const dropdowns = form.querySelectorAll(".dropdown");

  /** @type {HTMLElement|null} */
  const docTypeDropdown = form.querySelector('.dropdown[data-name="doc_type"]');

  // ---------------------------------------------------------------------------
  // Styling constants (kept inline to preserve existing visual behavior)
  // ---------------------------------------------------------------------------
  const STYLE_ACTIVE_BORDER = "#0078d4";
  const STYLE_INACTIVE_BORDER = "#ccd5e0";
  const STYLE_ACTIVE_SHADOW = "0 0 4px rgba(0, 120, 212, 0.25)";
  const STYLE_INACTIVE_SHADOW = "none";

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  /**
   * Safely query a child within an element.
   * @template {Element} T
   * @param {Element} root
   * @param {string} selector
   * @returns {T|null}
   */
  function qs(root, selector) {
    return /** @type {T|null} */ (root.querySelector(selector));
  }

  /**
   * Close all dropdowns, optionally except one.
   * @param {HTMLElement|null} except
   */
  function closeAllDropdowns(except = null) {
    dropdowns.forEach((dd) => {
      if (except && dd === except) return;
      dd.classList.remove("open");
      setExpanded(dd, false);
    });
  }

  /**
   * Set aria-expanded on the dropdown-selected element.
   * @param {HTMLElement} dropdown
   * @param {boolean} expanded
   */
  function setExpanded(dropdown, expanded) {
    const selected = qs(dropdown, ".dropdown-selected");
    if (selected) selected.setAttribute("aria-expanded", expanded ? "true" : "false");
  }

  /**
   * Apply "active" vs "inactive" styling to a text input/textarea.
   * (We keep the inline styles used in your original code to avoid CSS changes.)
   * @param {HTMLInputElement|HTMLTextAreaElement} el
   */
  function styleTextField(el) {
    const hasValue = !!el.value.trim();
    el.style.borderColor = hasValue ? STYLE_ACTIVE_BORDER : STYLE_INACTIVE_BORDER;
    el.style.boxShadow = hasValue ? STYLE_ACTIVE_SHADOW : STYLE_INACTIVE_SHADOW;
  }

  /**
   * Apply "active" vs "inactive" styling to a custom dropdown UI based on its hidden input.
   * @param {HTMLElement} dropdown
   */
  function styleDropdown(dropdown) {
    const hidden = qs(dropdown, 'input[type="hidden"]');
    const selected = qs(dropdown, ".dropdown-selected");
    if (!selected) return;

    const hasValue = !!(hidden && hidden.value);
    selected.style.borderColor = hasValue ? STYLE_ACTIVE_BORDER : STYLE_INACTIVE_BORDER;
    selected.style.boxShadow = hasValue ? STYLE_ACTIVE_SHADOW : STYLE_INACTIVE_SHADOW;
  }

  /**
   * Update visual border feedback on any supported element.
   * @param {Element} el
   */
  function updateBorder(el) {
    if (!el) return;

    // Text inputs & textarea
    if (el instanceof HTMLTextAreaElement) {
      styleTextField(el);
      return;
    }

    if (el instanceof HTMLInputElement && el.type === "text") {
      styleTextField(el);
      return;
    }

    // Dropdown container
    if (el instanceof HTMLElement && el.classList.contains("dropdown")) {
      styleDropdown(el);
    }
  }

  /**
   * Ensure dropdown selected label matches hidden value on page load.
   * If you ever prefill hidden inputs server-side, the UI will reflect it.
   * @param {HTMLElement} dropdown
   */
  function syncDropdownLabelFromHidden(dropdown) {
    const hidden = qs(dropdown, 'input[type="hidden"]');
    const selected = qs(dropdown, ".dropdown-selected");
    const options = qs(dropdown, ".dropdown-options");
    if (!hidden || !selected || !options) return;

    if (!hidden.value) return;

    const match = options.querySelector(`div[data-value="${CSS.escape(hidden.value)}"]`);
    if (match && match.textContent) {
      selected.textContent = match.textContent;
    }
  }

  /**
   * Mark a dropdown as an error (visual) and focus its selected element.
   * @param {HTMLElement} dropdown
   */
  function markDropdownError(dropdown) {
    dropdown.classList.add("error");
    const selected = qs(dropdown, ".dropdown-selected");
    selected?.focus();
  }

  // ---------------------------------------------------------------------------
  // Dropdown initialization (behavior + accessibility)
  // ---------------------------------------------------------------------------

  /**
   * Initialize a custom dropdown with click + keyboard support.
   * @param {HTMLElement} dropdown
   */
  function initDropdown(dropdown) {
    const selected = qs(dropdown, ".dropdown-selected");
    const options = qs(dropdown, ".dropdown-options");
    const hidden = qs(dropdown, 'input[type="hidden"]');

    if (!selected || !options || !hidden) return;

    // Basic accessibility roles
    selected.setAttribute("role", "button");
    selected.setAttribute("tabindex", "0");
    selected.setAttribute("aria-haspopup", "listbox");
    selected.setAttribute("aria-expanded", "false");

    options.setAttribute("role", "listbox");

    // Make each option keyboard-focusable
    const optionEls = Array.from(options.querySelectorAll("div[data-value]"));
    optionEls.forEach((opt) => {
      opt.setAttribute("role", "option");
      opt.setAttribute("tabindex", "-1");
      if (hidden.value && opt.dataset.value === hidden.value) {
        opt.setAttribute("aria-selected", "true");
      } else {
        opt.setAttribute("aria-selected", "false");
      }
    });

    function openDropdown() {
      closeAllDropdowns(dropdown);
      dropdown.classList.add("open");
      setExpanded(dropdown, true);
    }

    function closeDropdown() {
      dropdown.classList.remove("open");
      setExpanded(dropdown, false);
    }

    function toggleDropdown() {
      const isOpen = dropdown.classList.contains("open");
      if (isOpen) closeDropdown();
      else openDropdown();
    }

    /**
     * Select an option element.
     * @param {HTMLElement} opt
     */
    function selectOption(opt) {
      const value = opt.dataset.value || "";
      hidden.value = value;

      if (opt.textContent) selected.textContent = opt.textContent;

      // clear error if selection made
      if (hidden.value) dropdown.classList.remove("error");

      // aria-selected bookkeeping
      optionEls.forEach((o) => o.setAttribute("aria-selected", o === opt ? "true" : "false"));

      closeDropdown();
      updateBorder(dropdown);
    }

    // Click: toggle open/close
    selected.addEventListener("click", (e) => {
      e.preventDefault();
      toggleDropdown();
    });

    // Keyboard: Enter/Space toggles, Escape closes, ArrowDown opens
    selected.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggleDropdown();
        return;
      }
      if (e.key === "Escape") {
        e.preventDefault();
        closeDropdown();
        return;
      }
      if (e.key === "ArrowDown") {
        e.preventDefault();
        openDropdown();

        // focus first option
        const first = optionEls[0];
        first?.focus();
      }
    });

    // Click on options
    options.addEventListener("click", (e) => {
      const target = /** @type {HTMLElement|null} */ (e.target instanceof HTMLElement ? e.target : null);
      const opt = target?.closest("div[data-value]");
      if (!opt) return;
      selectOption(opt);
    });

    // Keyboard navigation within options (ArrowUp/Down, Enter selects, Escape closes)
    options.addEventListener("keydown", (e) => {
      const active = document.activeElement;
      const idx = optionEls.findIndex((o) => o === active);

      if (e.key === "Escape") {
        e.preventDefault();
        closeDropdown();
        selected.focus();
        return;
      }

      if (e.key === "Enter") {
        e.preventDefault();
        if (active instanceof HTMLElement && active.dataset.value !== undefined) {
          selectOption(active);
        }
        return;
      }

      if (e.key === "ArrowDown") {
        e.preventDefault();
        const next = optionEls[Math.min(idx + 1, optionEls.length - 1)] || optionEls[0];
        next?.focus();
        return;
      }

      if (e.key === "ArrowUp") {
        e.preventDefault();
        const prev = optionEls[Math.max(idx - 1, 0)] || optionEls[optionEls.length - 1];
        prev?.focus();
      }
    });

    // Initial sync
    syncDropdownLabelFromHidden(dropdown);
    updateBorder(dropdown);
  }

  // Init dropdowns
  dropdowns.forEach((dropdown) => initDropdown(dropdown));

  // Close dropdowns on outside click
  document.addEventListener("click", (e) => {
    const target = /** @type {Node} */ (e.target);
    dropdowns.forEach((dropdown) => {
      if (!dropdown.contains(target)) {
        dropdown.classList.remove("open");
        setExpanded(dropdown, false);
      }
    });
  });

  // Close dropdowns on global Escape
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAllDropdowns(null);
  });

  // ---------------------------------------------------------------------------
  // Live visual feedback on text fields
  // ---------------------------------------------------------------------------
  textInputs.forEach((input) => {
    input.addEventListener("input", () => updateBorder(input));
    // Apply initial style on load (useful if browser autofills)
    updateBorder(input);
  });

  // ---------------------------------------------------------------------------
  // Block submit if doc_type not selected
  // ---------------------------------------------------------------------------
  form.addEventListener("submit", (e) => {
    if (!docTypeDropdown) return;

    const hidden = qs(docTypeDropdown, 'input[type="hidden"][name="doc_type"]');
    const hasValue = !!(hidden && hidden.value);

    if (!hasValue) {
      e.preventDefault();
      markDropdownError(docTypeDropdown);
    }
  });
});