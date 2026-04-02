/**
 * chatbot.js
 *
 * Purpose:
 * - Provide client-side UX for the chatbot page:
 *   - Auto-resize textarea + character counter
 *   - "Enter to send" behavior (Shift+Enter for new line)
 *   - Immediately show the user's message bubble (optimistic UI)
 *   - Show a loading bubble while the server responds
 *   - Rotate friendly loading messages
 *   - Source proof modal: click a source chip -> open modal with excerpt
 */

document.addEventListener("DOMContentLoaded", () => {
  // ---------------------------------------------------------------------------
  // DOM references
  // ---------------------------------------------------------------------------
  const chatArea = document.getElementById("chatArea");
  const textarea = document.getElementById("questionInput");
  const sendBtn = document.getElementById("sendBtn");
  const chatForm = document.getElementById("chatForm");
  const charCounter = document.getElementById("charCounter");

  const proofModal = document.getElementById("proofModal");
  const proofText = document.getElementById("proofText");
  const modalCloseBtn = proofModal?.querySelector(".modal__close");

  if (!textarea || !sendBtn || !chatForm) return;

  // ---------------------------------------------------------------------------
  // Constants
  // ---------------------------------------------------------------------------
  const MAX_LENGTH = Number(textarea.getAttribute("maxlength")) || 2000;

  const cfgElement = document.getElementById("chatbot-config");
    if (!cfgElement) {
      console.error("Chatbot config element not found");
      return;
    }
    const CFG = JSON.parse(cfgElement.textContent);

  const LOADING_MESSAGES = CFG.loadingMessages;
  const TERMINAL_COUNT = CFG.loadingTerminalCount;
  const MAX_TIME_MS = CFG.loadingMaxTimeSec * 1000;

  // Number of messages that rotate
  const ROTATING_COUNT = Math.max(LOADING_MESSAGES.length - TERMINAL_COUNT, 1);

  // Interval = total time / rotating messages
  const LOADING_MESSAGE_INTERVAL_MS = Math.floor(
    MAX_TIME_MS / ROTATING_COUNT
  );

  // ---------------------------------------------------------------------------
  // State (kept small and explicit)
  // ---------------------------------------------------------------------------
  const state = {
    hasSubmitted: false,
    intervalId: /** @type {number|null} */ (null),
    loadingTextEl: /** @type {HTMLElement|null} */ (null),
  };

  // ---------------------------------------------------------------------------
  // Helpers: scrolling + empty state
  // ---------------------------------------------------------------------------
  function scrollToBottom() {
    if (!chatArea) return;
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function removeEmptyState() {
    if (!chatArea) return;
    const empty = chatArea.querySelector(".chat-thread__empty");
    empty?.remove();
  }

  // ---------------------------------------------------------------------------
  // Helpers: loading interval
  // ---------------------------------------------------------------------------
  function clearLoadingInterval() {
    if (state.intervalId !== null) {
      clearInterval(state.intervalId);
      state.intervalId = null;
    }
  }

  function startLoadingInterval() {
    if (!state.loadingTextEl) return;

    clearLoadingInterval();

    let idx = 0;
    state.loadingTextEl.textContent = LOADING_MESSAGES[idx];

    state.intervalId = window.setInterval(() => {
      idx++;

      // Stop rotation at last message
      if (idx >= LOADING_MESSAGES.length) {
        clearLoadingInterval();
        return;
      }

      state.loadingTextEl.textContent = LOADING_MESSAGES[idx];
    }, LOADING_MESSAGE_INTERVAL_MS);
  }


  // ---------------------------------------------------------------------------
  // Helpers: UI elements (safe DOM building)
  // ---------------------------------------------------------------------------
  function setButtonLoading() {
    sendBtn.classList.add("btn--loading");
    sendBtn.disabled = true;
  }

  /**
   * Insert a user bubble into the chat area.
   * (Optimistic UI: user sees their message immediately.)
   * @param {string} message
   */
  function insertUserBubble(message) {
    if (!chatArea) return;

    const text = (message || "").trim();
    if (!text) return;

    removeEmptyState();

    // Prevent duplicates if double-triggered
    const existing = chatArea.querySelector(".chat-bubble--user.chat-bubble--pending");
    if (existing) return;

    const bubble = document.createElement("article");
    bubble.className = "chat-bubble chat-bubble--user chat-bubble--pending";

    const header = document.createElement("header");
    header.className = "chat-bubble__meta";

    const author = document.createElement("span");
    author.className = "chat-bubble__author";
    author.textContent = "You";

    header.appendChild(author);

    const body = document.createElement("p");
    body.className = "chat-bubble__body";
    body.textContent = text;

    bubble.appendChild(header);
    bubble.appendChild(body);

    chatArea.appendChild(bubble);
    scrollToBottom();
  }

  /**
   * Insert a loading bubble for the bot response.
   * This bubble will rotate loading messages until page refresh.
   */
  function insertLoadingBubble() {
    if (!chatArea) return;

    removeEmptyState();

    // Prevent multiple loading bubbles
    const existing = chatArea.querySelector(".chat-bubble--loading");
    if (existing) return;

    const bubble = document.createElement("article");
    bubble.className = "chat-bubble chat-bubble--bot chat-bubble--loading";

    const header = document.createElement("header");
    header.className = "chat-bubble__meta";

    const author = document.createElement("span");
    author.className = "chat-bubble__author";
    author.textContent = "Bot";

    const role = document.createElement("span");
    role.className = "chat-bubble__role";
    role.textContent = "GAMP 5 Expert";

    header.appendChild(author);
    header.appendChild(role);

    const bodyWrap = document.createElement("div");
    bodyWrap.className = "chat-bubble__body";

    const p = document.createElement("p");
    p.className = "loading-text";
    bodyWrap.appendChild(p);

    bubble.appendChild(header);
    bubble.appendChild(bodyWrap);

    chatArea.appendChild(bubble);
    scrollToBottom();

    state.loadingTextEl = p;
    startLoadingInterval();
  }

  // ---------------------------------------------------------------------------
  // Helpers: textarea behavior
  // ---------------------------------------------------------------------------
  function autoResize() {
    textarea.style.height = "auto";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }

  function updateCounterAndButton() {
    const length = textarea.value.length;

    if (charCounter) {
      charCounter.textContent = `${length} / ${MAX_LENGTH}`;
      charCounter.classList.toggle("chat-input__counter--warning", length >= MAX_LENGTH);
    }

    if (!sendBtn.classList.contains("btn--loading")) {
      sendBtn.disabled = textarea.value.trim().length === 0;
    }
  }

  // ---------------------------------------------------------------------------
  // Submission behavior
  // ---------------------------------------------------------------------------
  function submitChat() {
    if (state.hasSubmitted) return;

    const question = textarea.value.trim();
    if (!question) return;

    state.hasSubmitted = true;

    insertUserBubble(question);

    textarea.readOnly = true;
    setButtonLoading();
    insertLoadingBubble();

    // Let the server handle response by submitting the form
    chatForm.submit();
  }

  // ---------------------------------------------------------------------------
  // Initial UI state
  // ---------------------------------------------------------------------------
  scrollToBottom();
  autoResize();
  updateCounterAndButton();

  // ---------------------------------------------------------------------------
  // Event bindings: input + keyboard
  // ---------------------------------------------------------------------------
  textarea.addEventListener("input", () => {
    autoResize();
    updateCounterAndButton();
  });

  textarea.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitChat();
    }
  });

  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    submitChat();
  });

  // Clean up intervals on navigation / tab hide
  window.addEventListener("pagehide", clearLoadingInterval);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) clearLoadingInterval();
  });

  // ---------------------------------------------------------------------------
  // Source proof modal handling
  // ---------------------------------------------------------------------------
  function openModalWithText(text) {
    if (!proofModal || !proofText) return;

    proofText.textContent = text || "";
    proofModal.classList.remove("modal--hidden");
    proofModal.classList.add("modal--visible");
  }

  function closeModal() {
    if (!proofModal) return;

    proofModal.classList.remove("modal--visible");
    proofModal.classList.add("modal--hidden");
  }

  if (chatArea && proofModal) {
    chatArea.addEventListener("click", (event) => {
      const target = /** @type {HTMLElement|null} */ (event.target instanceof HTMLElement ? event.target : null);
      if (!target) return;

      if (target.classList.contains("source-link")) {
        // dataset values are strings; guard for undefined.
        const proof = target.dataset?.proof || "";
        openModalWithText(proof);
      }
    });
  }

  modalCloseBtn?.addEventListener("click", closeModal);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeModal();
  });
});
