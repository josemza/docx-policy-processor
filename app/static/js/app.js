const shell = document.querySelector("[data-shell]");
const sidebarToggle = document.querySelector("[data-sidebar-toggle]");

if (shell && sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
        shell.classList.toggle("is-collapsed");
    });
}
