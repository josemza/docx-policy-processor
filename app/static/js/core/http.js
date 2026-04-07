import { ensureSession, renewSessionSilently } from "./session.js";
import { sessionStore } from "./store.js";

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

export async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const payload = await parseResponse(response);
    return {
        ok: response.ok,
        status: response.status,
        payload,
    };
}

export function requestApi(baseUrl, path, options = {}) {
    return requestJson(`${baseUrl}${path}`, options);
}

export async function authorizedRequest(baseUrl, path, options = {}) {
    let session = await ensureSession();
    if (!session) {
        return {
            ok: false,
            status: 401,
            payload: { success: false, message: "Sesión no disponible." },
        };
    }

    const headers = new Headers(options.headers || {});
    headers.set("Authorization", `Bearer ${session.tokens.access_token}`);

    let response = await fetch(`${baseUrl}${path}`, { ...options, headers });
    let payload = await parseResponse(response);

    if (response.status !== 401) {
        return { ok: response.ok, status: response.status, payload };
    }

    const refreshed = await renewSessionSilently();
    if (!refreshed) {
        window.location.assign("/login");
        return { ok: false, status: 401, payload };
    }

    session = sessionStore.read();
    const retryHeaders = new Headers(options.headers || {});
    retryHeaders.set("Authorization", `Bearer ${session.tokens.access_token}`);

    response = await fetch(`${baseUrl}${path}`, { ...options, headers: retryHeaders });
    payload = await parseResponse(response);

    return { ok: response.ok, status: response.status, payload };
}
