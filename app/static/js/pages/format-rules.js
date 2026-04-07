import { authorizedRequest } from "../core/http.js";
import { appConfig, operationStore } from "../core/store.js";
import { ensureSession, logoutCurrentSession, populateSessionUser } from "../core/session.js";
import { renderProductSummary } from "../modules/product-summary.js";
import { createRulesFormController } from "../modules/rules-form.js";

export async function initFormatRulesPage() {
    const session = await ensureSession();
    if (!session) {
        return;
    }

    const sessionUserLabel = document.querySelector("[data-session-user]");
    const logoutButtons = Array.from(document.querySelectorAll("[data-logout-button]"));
    const productSelect = document.querySelector("[data-product-select]");
    const productsStatus = document.querySelector("[data-products-status]");
    const rulesStatus = document.querySelector("[data-rules-status]");
    const productSummary = document.querySelector("[data-product-summary]");
    const rulesList = document.querySelector("[data-rules-list]");
    const ruleForm = document.querySelector("[data-rule-form]");
    const ruleFeedback = document.querySelector("[data-rule-feedback]");
    const ruleDeleteButton = document.querySelector("[data-rule-delete-button]");
    const ruleResetButton = document.querySelector("[data-rule-reset-button]");
    const ruleSubmitButton = document.querySelector("[data-rule-submit-button]");
    const editorState = document.querySelector("[data-rule-editor-state]");
    const summaryProducts = document.querySelector("[data-rules-summary-products]");
    const summaryActive = document.querySelector("[data-rules-summary-active]");
    const summaryVersion = document.querySelector("[data-rules-summary-version]");
    const selectionContext = document.querySelector("[data-rules-selection-context]");
    const currentProductLabel = document.querySelector("[data-current-product-label]");
    const currentRuleLabel = document.querySelector("[data-current-rule-label]");

    let activeProducts = [];
    let currentRules = [];

    const formController = createRulesFormController({
        form: ruleForm,
        listContainer: rulesList,
        deleteButton: ruleDeleteButton,
        submitButton: ruleSubmitButton,
        editorState,
    });

    const getSelectedProduct = () => activeProducts.find((item) => item.id === productSelect?.value) || null;

    function setFeedback(message, variant = "info") {
        if (!ruleFeedback) {
            return;
        }

        ruleFeedback.textContent = message || "";
        ruleFeedback.className = `form-feedback alert alert--${variant}`;
    }

    function setStatusBadge(element, text, variant = "neutral") {
        if (!element) {
            return;
        }

        const normalized = variant === "neutral" ? "neutral" : variant;
        element.textContent = text;
        element.className = `status-pill badge status-pill--${normalized}`;
    }

    function setButtonLoading(button, isLoading) {
        if (!button) {
            return;
        }
        button.classList.toggle("is-loading", isLoading);
    }

    function updateSummaryCards() {
        if (summaryProducts) {
            summaryProducts.textContent = String(activeProducts.length);
        }

        if (summaryActive) {
            const activeCount = currentRules.filter((rule) => rule.active).length;
            summaryActive.textContent = String(activeCount);
        }

        const selectedRuleId = formController.getSelectedRuleId();
        const selectedRule = currentRules.find((rule) => rule.id === selectedRuleId) || null;
        const selectedProduct = getSelectedProduct();

        if (summaryVersion) {
            summaryVersion.textContent = selectedRule ? `v${selectedRule.version}` : "--";
        }

        if (selectionContext) {
            if (!selectedProduct) {
                selectionContext.textContent = "Selecciona un producto para revisar reglas vigentes, versiones anteriores y configuración base.";
            } else if (!currentRules.length) {
                selectionContext.textContent = `El producto ${selectedProduct.name} no tiene reglas cargadas todavía. Puedes crear una versión inicial.`;
            } else if (selectedRule) {
                selectionContext.textContent = `Editando la versión ${selectedRule.version} del producto ${selectedProduct.name}. ${selectedRule.active ? "Actualmente está activa." : "Actualmente está inactiva."}`;
            } else {
                selectionContext.textContent = `El producto ${selectedProduct.name} tiene ${currentRules.length} regla(s) visible(s). Selecciona una versión o crea una nueva.`;
            }
        }

        if (currentProductLabel) {
            currentProductLabel.textContent = selectedProduct ? `${selectedProduct.name} (${selectedProduct.code})` : "Sin producto seleccionado";
        }

        if (currentRuleLabel) {
            currentRuleLabel.textContent = selectedRule ? `Versión ${selectedRule.version}` : "Nueva regla";
        }
    }

    function bindRulesList() {
        const selectedProduct = getSelectedProduct();
        if (!productSelect?.value || !selectedProduct) {
            if (rulesList) {
                rulesList.innerHTML = `
                    <div class="empty-state empty-state--compact">
                        <strong>Sin reglas visibles</strong>
                        <span class="empty-state__text">Selecciona un producto para cargar sus reglas.</span>
                    </div>
                `;
            }
            updateSummaryCards();
            return;
        }

        if (!currentRules.length) {
            formController.renderList([], () => {}, { product: selectedProduct });
            updateSummaryCards();
            return;
        }

        formController.renderList(currentRules, (ruleId) => {
            const rule = currentRules.find((item) => item.id === ruleId);
            if (!rule) {
                return;
            }

            formController.load(rule);
            bindRulesList();
        }, { product: selectedProduct });
        updateSummaryCards();
    }

    async function loadProducts() {
        if (!productSelect || !productsStatus) {
            return;
        }

        setStatusBadge(productsStatus, "Cargando catálogo...");
        const result = await authorizedRequest(appConfig.productsBaseUrl, "", { method: "GET" });
        if (!result.payload.success) {
            setStatusBadge(productsStatus, "Catálogo no disponible", "danger");
            setFeedback(result.payload.message || "No fue posible cargar el catálogo.", "error");
            return;
        }

        activeProducts = result.payload.data;
        productSelect.innerHTML = '<option value="">Selecciona un producto</option>';
        activeProducts.forEach((product) => {
            const option = document.createElement("option");
            option.value = product.id;
            option.textContent = `${product.name} (${product.code})`;
            productSelect.appendChild(option);
        });

        const currentOperation = operationStore.read();
        if (currentOperation?.product_id) {
            productSelect.value = currentOperation.product_id;
        }

        setStatusBadge(productsStatus, `${activeProducts.length} producto(s) activos`, "success");
        updateSummaryCards();
    }

    async function loadFormatRules(productId) {
        if (!rulesStatus) {
            return;
        }

        if (!productId) {
            currentRules = [];
            setStatusBadge(rulesStatus, "Sin producto");
            formController.reset();
            bindRulesList();
            return;
        }

        setStatusBadge(rulesStatus, "Cargando reglas...", "info");
        const result = await authorizedRequest(
            appConfig.formatRulesBaseUrl,
            `?product_id=${encodeURIComponent(productId)}`,
            { method: "GET" },
        );

        if (!result.payload.success) {
            currentRules = [];
            setStatusBadge(rulesStatus, "Error", "danger");
            setFeedback(result.payload.message || "No fue posible cargar las reglas.", "error");
            bindRulesList();
            return;
        }

        currentRules = result.payload.data;
        setStatusBadge(rulesStatus, `${currentRules.length} regla(s)`, currentRules.length ? "success" : "neutral");

        const activeRule = currentRules.find((item) => item.active) || currentRules[0] || null;
        if (activeRule) {
            formController.load(activeRule);
        } else {
            formController.reset();
        }

        bindRulesList();
    }

    async function refreshProductsAndRules(productId) {
        await loadProducts();
        if (!productId || !productSelect) {
            return;
        }

        productSelect.value = productId;
        renderProductSummary(productSummary, getSelectedProduct());
        await loadFormatRules(productId);
    }

    async function handleRuleSubmit(event) {
        event.preventDefault();
        if (!ruleForm || !ruleFeedback || !productSelect?.value) {
            return;
        }

        const payload = formController.buildPayload(productSelect.value);
        const ruleId = ruleForm.elements.rule_id.value;
        const method = ruleId ? "PUT" : "POST";
        const path = ruleId ? `/${ruleId}` : "";
        setFeedback(ruleId ? "Actualizando regla..." : "Creando regla...", "info");
        setButtonLoading(ruleSubmitButton, true);

        const result = await authorizedRequest(appConfig.formatRulesBaseUrl, path, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(ruleId ? { active: payload.active, configuration: payload.configuration } : payload),
        });

        setButtonLoading(ruleSubmitButton, false);
        if (!result.payload.success) {
            setFeedback(result.payload.message || "No fue posible guardar la regla.", "error");
            return;
        }

        setFeedback(result.payload.message, "success");
        await refreshProductsAndRules(productSelect.value);
    }

    async function handleRuleDelete() {
        const selectedRuleId = formController.getSelectedRuleId();
        if (!selectedRuleId || !ruleFeedback || !productSelect?.value) {
            return;
        }

        setFeedback("Desactivando regla...", "warning");
        setButtonLoading(ruleDeleteButton, true);
        const result = await authorizedRequest(appConfig.formatRulesBaseUrl, `/${selectedRuleId}`, {
            method: "DELETE",
        });
        setButtonLoading(ruleDeleteButton, false);

        if (!result.payload.success) {
            setFeedback(result.payload.message || "No fue posible desactivar la regla.", "error");
            return;
        }

        setFeedback(result.payload.message, "success");
        formController.reset();
        await refreshProductsAndRules(productSelect.value);
    }

    logoutButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            await logoutCurrentSession();
            window.location.assign("/login");
        });
    });

    if (productSelect) {
        productSelect.addEventListener("change", async (event) => {
            const productId = event.target.value;
            renderProductSummary(productSummary, getSelectedProduct());
            formController.reset();
            bindRulesList();
            await loadFormatRules(productId);
        });
    }

    if (ruleForm) {
        ruleForm.addEventListener("submit", handleRuleSubmit);
    }

    if (ruleDeleteButton) {
        ruleDeleteButton.addEventListener("click", handleRuleDelete);
    }

    if (ruleResetButton) {
        ruleResetButton.addEventListener("click", () => {
            formController.reset();
            bindRulesList();
            setFeedback("Formulario listo para crear una nueva regla.", "info");
        });
    }

    await populateSessionUser(sessionUserLabel);
    formController.reset();
    await loadProducts();
    renderProductSummary(productSummary, getSelectedProduct());
    bindRulesList();
    if (productSelect?.value) {
        await loadFormatRules(productSelect.value);
    }
}
