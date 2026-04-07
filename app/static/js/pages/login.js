import { authApi, clearClientSession, persistSession } from "../core/session.js";

function setButtonLoading(button, isLoading, idleLabel, loadingLabel) {
    if (!button) {
        return;
    }

    button.classList.toggle("is-loading", isLoading);
    button.disabled = isLoading;
    button.textContent = isLoading ? loadingLabel : idleLabel;
}

export function initLoginPage() {
    const loginForm = document.querySelector("[data-login-form]");
    const loginFeedback = document.querySelector("[data-login-feedback]");
    const submitButton = document.querySelector("[data-login-submit-button]");

    if (!loginForm) {
        return;
    }

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData(loginForm);
        const username = String(formData.get("username") || "");
        const password = String(formData.get("password") || "");

        if (loginFeedback) {
            loginFeedback.textContent = "Validando acceso corporativo...";
            loginFeedback.className = "form-feedback alert alert--info";
        }

        setButtonLoading(submitButton, true, "Acceder", "Validando...");
        const result = await authApi.login(username, password);
        setButtonLoading(submitButton, false, "Acceder", "Validando...");

        if (!result.payload.success) {
            if (loginFeedback) {
                loginFeedback.textContent = result.payload.message || "No fue posible iniciar sesión.";
                loginFeedback.className = "form-feedback alert alert--error";
            }
            return;
        }

        clearClientSession();
        persistSession(result.payload.data);
        window.location.assign("/app");
    });
}
