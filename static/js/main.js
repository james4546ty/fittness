(function() {
  // Theme toggle using localStorage + data-bs-theme attribute
  function setTheme(theme) {
    const html = document.documentElement;
    html.setAttribute("data-bs-theme", theme);
    localStorage.setItem("theme", theme);
  }
  function getTheme() {
    return localStorage.getItem("theme") || document.documentElement.getAttribute("data-bs-theme") || "light";
  }

  document.addEventListener("DOMContentLoaded", function() {
    const current = getTheme();
    setTheme(current);

    const btn = document.getElementById("themeToggle");
    if (btn) {
      btn.addEventListener("click", function() {
        const next = (getTheme() === "light") ? "dark" : "light";
        setTheme(next);
      });
    }

    // Landing navbar transparency -> solid on scroll
    const nav = document.querySelector(".navbar-transparent");
    if (nav) {
      const onScroll = () => {
        if (window.scrollY > 40) {
          nav.classList.add("scrolled");
        } else {
          nav.classList.remove("scrolled");
        }
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
  });
})();