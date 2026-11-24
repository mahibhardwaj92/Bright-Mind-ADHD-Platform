let themeToggle = document.getElementById("theme-toggle");
const savedTheme = localStorage.getItem("brightMindTheme");

if (!themeToggle) {
  themeToggle = document.createElement("button");
  themeToggle.id = "theme-toggle";
  themeToggle.type = "button";
  themeToggle.style.cssText = "position:fixed;right:20px;bottom:20px;z-index:5;border:1px solid var(--line);border-radius:999px;padding:10px 13px;background:var(--card);color:var(--ink);font:700 12px var(--sans);cursor:pointer;box-shadow:0 5px 15px rgba(0,0,0,.12)";
  document.body.appendChild(themeToggle);
}

if (savedTheme === "dark") document.body.classList.add("dark");

if (themeToggle) {
  const updateThemeLabel = () => {
    const isDark = document.body.classList.contains("dark");
    themeToggle.textContent = isDark ? "☀ Light" : "☾ Dark";
    themeToggle.setAttribute("aria-label", isDark ? "Switch to light theme" : "Switch to dark theme");
  };

  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    localStorage.setItem("brightMindTheme", document.body.classList.contains("dark") ? "dark" : "light");
    updateThemeLabel();
  });

  updateThemeLabel();
}
