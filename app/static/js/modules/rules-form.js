function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

export function createRulesFormController({ form, listContainer, deleteButton, submitButton, editorState }) {
    let selectedRuleId = null;

    function setEditorState(text, variant = "pending") {
        if (!editorState) {
            return;
        }

        editorState.textContent = text;
        editorState.className = `badge badge--${variant}`;
    }

    function reset() {
        if (!form) {
            return;
        }

        selectedRuleId = null;
        form.reset();
        form.elements.rule_id.value = "";
        form.elements.paper_size.value = "A4";
        form.elements.margin_top_cm.value = "2.5";
        form.elements.margin_bottom_cm.value = "2.5";
        form.elements.margin_left_cm.value = "2.0";
        form.elements.margin_right_cm.value = "2.0";
        form.elements.general_font_family.value = "Arial";
        form.elements.general_font_size_pt.value = "10";
        form.elements.general_line_spacing.value = "1.15";
        form.elements.general_color_hex.value = "#000000";
        form.elements.general_uppercase.checked = false;
        form.elements.title_font_family.value = "Arial";
        form.elements.title_font_size_pt.value = "14";
        form.elements.title_alignment.value = "center";
        form.elements.title_uppercase.checked = true;
        form.elements.title_bold.checked = true;
        form.elements.rule_active.checked = true;

        if (deleteButton) {
            deleteButton.disabled = true;
        }

        if (submitButton) {
            submitButton.textContent = "Guardar regla";
        }

        setEditorState("Nueva regla", "pending");
    }

    function load(rule) {
        if (!form) {
            return;
        }

        selectedRuleId = rule.id;
        const config = rule.configuration;
        form.elements.rule_id.value = rule.id;
        form.elements.paper_size.value = config.page_setup.paper_size;
        form.elements.margin_top_cm.value = config.page_setup.margins.top_cm;
        form.elements.margin_bottom_cm.value = config.page_setup.margins.bottom_cm;
        form.elements.margin_left_cm.value = config.page_setup.margins.left_cm;
        form.elements.margin_right_cm.value = config.page_setup.margins.right_cm;
        form.elements.general_font_family.value = config.general_text.font_family;
        form.elements.general_font_size_pt.value = config.general_text.font_size_pt;
        form.elements.general_line_spacing.value = config.general_text.line_spacing;
        form.elements.general_color_hex.value = `#${config.general_text.color_hex}`;
        form.elements.general_uppercase.checked = Boolean(config.general_text.uppercase);
        form.elements.title_font_family.value = config.title_text.font_family;
        form.elements.title_font_size_pt.value = config.title_text.font_size_pt;
        form.elements.title_alignment.value = config.title_text.alignment;
        form.elements.title_uppercase.checked = Boolean(config.title_text.uppercase);
        form.elements.title_bold.checked = Boolean(config.title_text.bold);
        form.elements.rule_active.checked = Boolean(rule.active);

        if (deleteButton) {
            deleteButton.disabled = false;
        }

        if (submitButton) {
            submitButton.textContent = "Actualizar regla";
        }

        setEditorState(`Versión ${rule.version}`, rule.active ? "active" : "pending");
    }

    function buildPayload(productId) {
        const current = form.elements;
        return {
            product_id: productId,
            active: current.rule_active.checked,
            configuration: {
                page_setup: {
                    paper_size: current.paper_size.value,
                    margins: {
                        top_cm: Number(current.margin_top_cm.value),
                        bottom_cm: Number(current.margin_bottom_cm.value),
                        left_cm: Number(current.margin_left_cm.value),
                        right_cm: Number(current.margin_right_cm.value),
                    },
                },
                general_text: {
                    font_family: current.general_font_family.value,
                    font_size_pt: Number(current.general_font_size_pt.value),
                    line_spacing: Number(current.general_line_spacing.value),
                    uppercase: current.general_uppercase.checked,
                    color_hex: current.general_color_hex.value,
                },
                title_text: {
                    font_family: current.title_font_family.value,
                    font_size_pt: Number(current.title_font_size_pt.value),
                    uppercase: current.title_uppercase.checked,
                    alignment: current.title_alignment.value,
                    bold: current.title_bold.checked,
                },
            },
        };
    }

    function renderList(rules, onSelect, context = {}) {
        if (!listContainer) {
            return;
        }

        if (!rules.length) {
            listContainer.innerHTML = `
                <div class="empty-state empty-state--compact">
                    <strong>Sin reglas visibles</strong>
                    <span class="empty-state__text">No hay reglas registradas para este producto.</span>
                </div>
            `;
            return;
        }

        const titleTemplate = context.product?.title_template || "Título no disponible";
        const headerTemplate = context.product?.header_template || "Encabezado no disponible";

        listContainer.innerHTML = rules.map((rule) => `
            <button class="rule-card list-card ${selectedRuleId === rule.id ? "is-selected" : ""}" type="button" data-rule-item data-rule-id="${escapeHtml(rule.id)}">
                <div class="rule-card__top">
                    <div>
                        <span class="rule-card__title list-card__title">Versión ${escapeHtml(rule.version)}</span>
                        <p class="rule-card__description">${escapeHtml(titleTemplate)}</p>
                    </div>
                    <div class="rule-card__badge-row">
                        <span class="badge ${rule.active ? "badge--active" : "badge--pending"}">${rule.active ? "Activa" : "Inactiva"}</span>
                    </div>
                </div>
                <div class="rule-card__meta-grid">
                    <div class="rule-card__meta-item">
                        <span>Encabezado</span>
                        <strong>${escapeHtml(headerTemplate)}</strong>
                    </div>
                    <div class="rule-card__meta-item">
                        <span>Fuente</span>
                        <strong>${escapeHtml(rule.configuration.general_text.font_family)} / ${escapeHtml(rule.configuration.general_text.font_size_pt)} pt</strong>
                    </div>
                    <div class="rule-card__meta-item">
                        <span>Color</span>
                        <strong>#${escapeHtml(rule.configuration.general_text.color_hex)}</strong>
                    </div>
                    <div class="rule-card__meta-item">
                        <span>Interlineado</span>
                        <strong>${escapeHtml(rule.configuration.general_text.line_spacing)}</strong>
                    </div>
                </div>
            </button>
        `).join("");

        listContainer.querySelectorAll("[data-rule-item]").forEach((button) => {
            button.addEventListener("click", () => onSelect(button.dataset.ruleId));
        });
    }

    return {
        reset,
        load,
        buildPayload,
        renderList,
        getSelectedRuleId() {
            return selectedRuleId;
        },
    };
}
