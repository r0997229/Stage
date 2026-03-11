/**
 * toast.js
 *
 * Purpose:
 * - Display short user notifications ("toasts") in the bottom/top corner (CSS decides).
 *
 * Design goals:
 * - Safe by default (no innerHTML injection).
 * - Works even if the container is missing (self-creates).
 * - Limits the number of visible toasts to keep UI clean.
 *
 * Public API:
 * - showToast(message, type = "error", timeout = 3500)
 */

/** @type {number} */
const DEFAULT_TIMEOUT_MS = 3500;
/** @type {number} */
const MAX_TOASTS = 4;
/** @type {number} */
const ANIMATION_OUT_MS = 250;

/**
 * Get or create the toast container.
 * @returns {HTMLElement}
 */
function getToastContainer() {
  let container = document.getElementById("toastContainer");

  // Failsafe: create container if it doesn't exist.
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  return container;
}

/**
 * Remove old toasts if we exceed MAX_TOASTS.
 * @param {HTMLElement} container
 */
function enforceToastLimit(container) {
  while (container.children.length > MAX_TOASTS) {
    container.firstChild?.remove();
  }
}

/**
 * Create a toast element (DOM only).
 * @param {string} message
 * @param {string} type
 * @returns {{toast: HTMLElement, closeBtn: HTMLButtonElement}}
 */
function createToastElement(message, type) {
  const toast = document.createElement("div");
  toast.className = `toast toast--${type}`;
  toast.setAttribute("role", "alert");

  // Safe text insertion (no innerHTML).
  const messageSpan = document.createElement("span");
  messageSpan.textContent = message;

  const closeBtn = document.createElement("button");
  closeBtn.className = "toast-close";
  closeBtn.setAttribute("aria-label", "Close");
  closeBtn.type = "button";
  closeBtn.textContent = "×";

  toast.appendChild(messageSpan);
  toast.appendChild(closeBtn);

  return { toast, closeBtn };
}

/**
 * Animate toast out and remove it.
 * @param {HTMLElement} toast
 */
function removeToastAnimated(toast) {
  toast.style.animation = "toast-out 0.25s forwards ease-in";
  window.setTimeout(() => toast.remove(), ANIMATION_OUT_MS);
}

/**
 * Display a toast message.
 *
 * @param {string} message - Text content shown to the user.
 * @param {"error"|"success"|"info"|"warning"|string} [type="error"] - Used as a CSS modifier: toast--<type>.
 * @param {number} [timeout=3500] - Auto close delay in milliseconds. Set <= 0 to disable auto close.
 */
export function showToast(message, type = "error", timeout = DEFAULT_TIMEOUT_MS) {
  const container = getToastContainer();

  // Normalize parameters (robustness)
  const safeMessage = typeof message === "string" ? message : String(message ?? "");
  const safeType = typeof type === "string" && type.trim() ? type.trim() : "error";
  const safeTimeout = Number.isFinite(timeout) ? timeout : DEFAULT_TIMEOUT_MS;

  const { toast, closeBtn } = createToastElement(safeMessage, safeType);
  container.appendChild(toast);
  enforceToastLimit(container);

  let removed = false;
  let timerId = null;

  const removeOnce = () => {
    if (removed) return;
    removed = true;

    if (timerId) {
      clearTimeout(timerId);
      timerId = null;
    }

    removeToastAnimated(toast);
  };

  closeBtn.addEventListener("click", removeOnce);

  // Auto close (if timeout > 0)
  if (safeTimeout > 0) {
    timerId = window.setTimeout(removeOnce, safeTimeout);
  }
}
