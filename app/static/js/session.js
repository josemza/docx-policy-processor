const SESSION_STORAGE_KEY = "formateador.session";

const sessionApi = {
    authBaseUrl: window.APP_SESSION?.authBaseUrl || "/api/v1/auth",

    read() {
        const raw = window.localStorage.getItem(SESSION_STORAGE_KEY);
        return raw ? JSON.parse(raw) : null;
    },

    write(value) {
        window.localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(value));
    },

    clear() {
        window.localStorage.removeItem(SESSION_STORAGE_KEY);
    },

    async request(path, options = {}) {
        const response = await fetch(`${this.authBaseUrl}${path}`, options);
        return response.json();
    },

    async login(username, password) {
        return this.request("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });
    },

    async refresh(refreshToken) {
        return this.request("/refresh", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
    },

    async logout(refreshToken) {
        return this.request("/logout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
    },

    async me(accessToken) {
        return this.request("/me", {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
    },
};

function persistSession(authPayload) {
    const now = Date.now();
    sessionApi.write({
        user: authPayload.user,
        tokens: authPayload.tokens,
        accessExpiresAt: now + authPayload.tokens.expires_in * 1000,
    });
}

async function renewSessionSilently() {
    const currentSession = sessionApi.read();
    if (!currentSession?.tokens?.refresh_token) {
        return null;
    }

    const result = await sessionApi.refresh(currentSession.tokens.refresh_token);
    if (!result.success) {
        sessionApi.clear();
        return null;
    }

    persistSession(result.data);
    return result.data;
}

async function ensureSession() {
    const currentSession = sessionApi.read();
    if (!currentSession) {
        if (window.location.pathname.startsWith("/app")) {
            window.location.assign("/login");
        }
        return null;
    }

    const shouldRefresh = Date.now() >= currentSession.accessExpiresAt - 60000;
    if (shouldRefresh) {
        const refreshed = await renewSessionSilently();
        if (!refreshed && window.location.pathname.startsWith("/app")) {
            window.location.assign("/login");
        }
        return refreshed;
    }

    return currentSession;
}

const loginForm = document.querySelector("[data-login-form]");
const loginFeedback = document.querySelector("[data-login-feedback]");
const sessionUserLabel = document.querySelector("[data-session-user]");
const logoutButton = document.querySelector("[data-logout-button]");

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(loginForm);
        const username = String(formData.get("username") || "");
        const password = String(formData.get("password") || "");

        if (loginFeedback) {
            loginFeedback.textContent = "Validando credenciales...";
        }

        const result = await sessionApi.login(username, password);
        if (!result.success) {
            if (loginFeedback) {
                loginFeedback.textContent = result.message;
            }
            return;
        }

        persistSession(result.data);
        window.location.assign("/app");
    });
}

if (logoutButton) {
    logoutButton.addEventListener("click", async () => {
        const currentSession = sessionApi.read();
        if (currentSession?.tokens?.refresh_token) {
            await sessionApi.logout(currentSession.tokens.refresh_token);
        }
        sessionApi.clear();
        window.location.assign("/login");
    });
}

ensureSession().then(async (session) => {
    if (!session || !sessionUserLabel) {
        return;
    }

    const result = await sessionApi.me(session.tokens.access_token);
    if (!result.success) {
        const refreshed = await renewSessionSilently();
        if (!refreshed) {
            window.location.assign("/login");
            return;
        }
        sessionUserLabel.textContent = `Sesión activa: ${refreshed.user.username}`;
        return;
    }

    sessionUserLabel.textContent = `Sesión activa: ${result.data.user.username}`;
});
