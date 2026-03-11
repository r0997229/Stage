document.addEventListener("DOMContentLoaded", () => {
  const dropdowns = document.querySelectorAll(".dropdown");
  const form = document.getElementById("templateIngestForm");
  const submitBtn = document.getElementById("ti-submit");
  const spinner = document.getElementById("ti-spinner");

  function closeAll(except = null) {
    dropdowns.forEach((dd) => {
      if (dd !== except) dd.classList.remove("open");
    });
  }

  dropdowns.forEach((dropdown) => {
    const selected = dropdown.querySelector(".dropdown-selected");
    const options = dropdown.querySelector(".dropdown-options");
    const hidden = dropdown.querySelector('input[type="hidden"]');
    if (!selected || !options || !hidden) return;

    function toggleOpen() {
      const open = dropdown.classList.toggle("open");
      if (open) closeAll(dropdown);
    }

    selected.addEventListener("click", toggleOpen);

    options.addEventListener("click", (e) => {
      const opt = e.target.closest("div[data-value]");
      if (!opt) return;
      hidden.value = opt.dataset.value;
      selected.textContent = opt.textContent;
      dropdown.classList.remove("open");
      dropdown.classList.remove("error");
    });
  });

  document.addEventListener("click", (e) => {
    dropdowns.forEach((dd) => {
      if (!dd.contains(e.target)) dd.classList.remove("open");
    });
  });

  if (form) {
    form.addEventListener("submit", () => {
      // Let server validate; show busy UI
      if (submitBtn && spinner) {
        submitBtn.disabled = true;
        spinner.classList.remove("ti-hidden");
        spinner.setAttribute("aria-hidden", "false");
      }
    });
  }
});
