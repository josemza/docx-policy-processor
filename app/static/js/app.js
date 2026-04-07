import { initDashboardPage } from "./pages/dashboard.js";
import { initFormatRulesPage } from "./pages/format-rules.js";
import { initLoginPage } from "./pages/login.js";

const SHELL_PREFERENCE_KEY = "formateador.shell.collapsed";

function initShell() {
    const shell = document.querySelector("[data-shell]");
    const sidebarToggle = document.querySelector("[data-sidebar-toggle]");

    if (!shell || !sidebarToggle) {
        return;
    }

    const applyCollapsedState = (isCollapsed) => {
        shell.classList.toggle("is-collapsed", isCollapsed);
        sidebarToggle.setAttribute("aria-expanded", String(!isCollapsed));
    };

    applyCollapsedState(window.localStorage.getItem(SHELL_PREFERENCE_KEY) === "true");

    sidebarToggle.addEventListener("click", () => {
        const nextCollapsed = !shell.classList.contains("is-collapsed");
        applyCollapsedState(nextCollapsed);
        window.localStorage.setItem(SHELL_PREFERENCE_KEY, String(nextCollapsed));
    });
}

async function bootstrapPage() {
    const view = document.body.dataset.view;

    const pageInitializers = {
        login: initLoginPage,
        dashboard: initDashboardPage,
        format_rules: initFormatRulesPage,
    };

    const initPage = pageInitializers[view];
    if (initPage) {
        await initPage();
    }
}

initShell();
bootstrapPage();
