document.querySelectorAll(".nav-link").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((btn) => {
      btn.classList.remove("active");
      btn.removeAttribute("aria-current");
    });
    button.classList.add("active");
    button.setAttribute("aria-current", "page");
  });
});

/**
 * Palette: Client-side search and filtering for vault items.
 * Improves UX by providing instant feedback as users type.
 */
const searchInput = document.getElementById("vault-search");
const vaultCards = document.querySelectorAll(".vault-card");

if (searchInput) {
  searchInput.addEventListener("input", (e) => {
    const term = e.target.value.toLowerCase();

    vaultCards.forEach(card => {
      const title = card.querySelector(".card-title").textContent.toLowerCase();
      const tags = Array.from(card.querySelectorAll(".tag")).map(t => t.textContent.toLowerCase());
      const matches = title.includes(term) || tags.some(tag => tag.includes(term));

      card.style.display = matches ? "block" : "none";
    });
  });
}

const filterButtons = document.querySelectorAll(".filters .btn");
if (filterButtons.length > 0) {
  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const filter = btn.getAttribute("data-filter");

      // Update UI state
      filterButtons.forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-pressed", "false");
      });
      btn.classList.add("active");
      btn.setAttribute("aria-pressed", "true");

      // Filter items
      vaultCards.forEach(card => {
        if (filter === "all") {
          card.style.display = "block";
        } else {
          const meta = card.querySelector(".card-meta").textContent.toLowerCase();
          // Palette: Use includes() instead of startsWith() for more robust matching against the meta text.
          card.style.display = meta.includes(filter) ? "block" : "none";
        }
      });
    });
  });
}
