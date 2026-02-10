document.querySelectorAll(".nav-link").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");
  });
});
