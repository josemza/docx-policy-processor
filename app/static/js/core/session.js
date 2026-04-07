import { operationStore, sessionStore, appConfig } from "./store.js";

async function parseResponse(response) {
    const text = await response.text();

    if (!text) {
        return { success: response.ok, data: null, message: "" };
    }

    try {
        return JSON.parse(text);
    } catch {
        return {
            success: false,
            message: text,
        };
    }
}

async function requestAuth(path, options = {}) {
    const response = await fetch(`${appConfig.authBaseUrl}${path}`, options);
    const payload = await parseResponse(response);
    return {
        ok: response.ok,
        status: response.status,
        payload,
    };
}

export const authApi = {
    login(username, password) {
        return requestAuth("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });
    },
    refresh(refreshToken) {
        return requestAuth("/refresh", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
    },
    logout(refreshToken) {
        return requestAuth("/logout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
    },
    me(accessToken) {
        return requestAuth("/me", {
            headers: { Authorization: `Bearer ${accessToken}` },
        });
    },
};

export function persistSession(authPayload) {
    const now = Date.now();
    sessionStore.write({
        user: authPayload.user,
        tokens: authPayload.tokens,
        accessExpiresAt: now + authPayload.tokens.expires_in * 1000,
    });
}

export async function renewSessionSilently() {
    const currentSession = sessionStore.read();
    if (!currentSession?.tokens?.refresh_token) {
        return null;
    }

    const result = await authApi.refresh(currentSession.tokens.refresh_token);
    if (!result.payload.success) {
        clearClientSession();
        return null;
    }

    persistSession(result.payload.data);
    return result.payload.data;
}

export async function ensureSession({ redirectToLogin = true } = {}) {
    const currentSession = sessionStore.read();
    if (!currentSession) {
        if (redirectToLogin && window.location.pathname.startsWith("/app")) {
            window.location.assign("/login");
        }
        return null;
    }

    const shouldRefresh = Date.now() >= currentSession.accessExpiresAt - 60000;
    if (!shouldRefresh) {
        return currentSession;
    }

    const refreshed = await renewSessionSilently();
    if (!refreshed) {
        if (redirectToLogin && window.location.pathname.startsWith("/app")) {
            window.location.assign("/login");
        }
        return null;
    }

    return sessionStore.read();
}

export async function logoutCurrentSession() {
    const currentSession = sessionStore.read();
    if (currentSession?.tokens?.refresh_token) {
        await authApi.logout(currentSession.tokens.refresh_token);
    }

    clearClientSession();
}

export function clearClientSession() {
    sessionStore.clear();
    operationStore.clear();
}

export async function populateSessionUser(labelElement) {
    if (!labelElement) {
        return;
    }

    const session = await ensureSession();
    if (!session) {
        return;
    }

    const meResult = await authApi.me(session.tokens.access_token);
    if (meResult.payload.success) {
        labelElement.textContent = `Sesión activa: ${meResult.payload.data.user.username}`;
        return;
    }

    const refreshed = await renewSessionSilently();
    if (!refreshed) {
        window.location.assign("/login");
        return;
    }

    labelElement.textContent = `Sesión activa: ${refreshed.user.username}`;
}
