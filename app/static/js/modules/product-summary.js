function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

export function renderProductSummary(container, product) {
    if (!container) {
        return;
    }

    if (!product) {
        container.innerHTML = `
            <div class="empty-state empty-state--compact">
                <strong>Sin producto seleccionado</strong>
                <span class="empty-state__text">Selecciona un producto para ver el título esperado, el encabezado aplicable y el resumen de formato.</span>
            </div>
        `;
        return;
    }

    const rule = product.active_format_rule || {};
    const config = rule.configuration || {};
    container.innerHTML = `
        <dl class="summary-list">
            <div><dt>Producto</dt><dd>${escapeHtml(product.name)}</dd></div>
            <div><dt>Código</dt><dd>${escapeHtml(product.code)}</dd></div>
            <div><dt>Título esperado</dt><dd>${escapeHtml(product.title_template)}</dd></div>
            <div><dt>Encabezado aplicable</dt><dd>${escapeHtml(product.header_template)}</dd></div>
            <div><dt>Versión de regla</dt><dd>${escapeHtml(rule.version || "No definida")}</dd></div>
            <div><dt>Fuente general</dt><dd>${escapeHtml(config.general_text?.font_family || "No definida")}</dd></div>
            <div><dt>Tamaño general</dt><dd>${escapeHtml(config.general_text?.font_size_pt || "-")}</dd></div>
            <div><dt>Color texto</dt><dd>#${escapeHtml(config.general_text?.color_hex || "000000")}</dd></div>
        </dl>
    `;
}
