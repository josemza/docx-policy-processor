const DEFAULT_CONFIG = {
    authBaseUrl: "/api/v1/auth",
    productsBaseUrl: "/api/v1/products",
    documentsBaseUrl: "/api/v1/documents",
    formatRulesBaseUrl: "/api/v1/format-rules",
};

export const appConfig = Object.freeze({
    ...DEFAULT_CONFIG,
    ...(window.APP_SESSION || {}),
});

function safeParse(value) {
    if (!value) {
        return null;
    }

    try {
        return JSON.parse(value);
    } catch {
        return null;
    }
}

export function createJsonStore(key) {
    return {
        read() {
            return safeParse(window.localStorage.getItem(key));
        },
        write(value) {
            window.localStorage.setItem(key, JSON.stringify(value));
        },
        clear() {
            window.localStorage.removeItem(key);
        },
    };
}

export const sessionStore = createJsonStore("formateador.session");
export const operationStore = createJsonStore("formateador.currentOperation");
