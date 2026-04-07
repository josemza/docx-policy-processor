import { authorizedRequest } from "../core/http.js";
import { appConfig, operationStore, sessionStore } from "../core/store.js";
import { ensureSession, logoutCurrentSession, populateSessionUser } from "../core/session.js";
import {
    renderProcessingResult,
    renderRecentOperations,
    renderTraceabilityPanel,
} from "../modules/operation-summary.js";
import { renderProductSummary } from "../modules/product-summary.js";

const RECENT_OPERATIONS_KEY = "formateador.recentOperations";

function readRecentOperations() {
    const raw = window.localStorage.getItem(RECENT_OPERATIONS_KEY);
    if (!raw) {
        return [];
    }

    try {
        return JSON.parse(raw);
    } catch {
        return [];
    }
}

function writeRecentOperations(operations) {
    window.localStorage.setItem(RECENT_OPERATIONS_KEY, JSON.stringify(operations.slice(0, 5)));
}

function formatFileSize(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) {
        return "0 KB";
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function getNowIso() {
    return new Date().toISOString();
}

function attachFrontendMeta(operation, overrides = {}) {
    if (!operation) {
        return null;
    }

    const baseMeta = operation._frontend_meta || {};
    return {
        ...operation,
        _frontend_meta: {
            ...baseMeta,
            ...overrides,
        },
    };
}

function hydrateStoredOperation(operation) {
    if (!operation) {
        return null;
    }

    const baseTimestamp = operation.created_at || operation.updated_at || getNowIso();
    return attachFrontendMeta(operation, {
        registered_at: operation._frontend_meta?.registered_at || baseTimestamp,
        last_transition_at: operation._frontend_meta?.last_transition_at || operation.updated_at || baseTimestamp,
        processed_at: operation._frontend_meta?.processed_at || (operation.status === "COMPLETED" || operation.status === "ERROR" ? operation.updated_at || baseTimestamp : null),
        processing_started_at: operation._frontend_meta?.processing_started_at || (operation.status === "PROCESSING" ? operation.updated_at || baseTimestamp : null),
        product_label: operation._frontend_meta?.product_label || null,
    });
}

function setButtonLoading(button, isLoading, idleLabel, loadingLabel) {
    if (!button) {
        return;
    }

    button.classList.toggle("is-loading", isLoading);
    button.disabled = isLoading || button.disabled;
    button.textContent = isLoading ? loadingLabel : idleLabel;
}

export async function initDashboardPage() {
    const session = await ensureSession();
    if (!session) {
        return;
    }

    const sessionUserLabel = document.querySelector("[data-session-user]");
    const logoutButtons = Array.from(document.querySelectorAll("[data-logout-button]"));
    const documentForm = document.querySelector("[data-document-form]");
    const productSelect = document.querySelector("[data-product-select]");
    const productsStatus = document.querySelector("[data-products-status]");
    const productSummary = document.querySelector("[data-product-summary]");
    const documentFeedback = document.querySelector("[data-document-feedback]");
    const processButton = document.querySelector("[data-process-button]");
    const registerButton = document.querySelector("[data-register-button]");
    const clearButton = document.querySelector("[data-clear-document-button]");
    const resetResultButton = document.querySelector("[data-reset-result-button]");
    const downloadButton = document.querySelector("[data-download-button]");
    const resultPanel = document.querySelector("[data-result-panel]");
    const resultBadge = document.querySelector("[data-result-badge]");
    const validationBadge = document.querySelector("[data-validation-badge]");
    const validationFeedback = document.querySelector("[data-validation-feedback]");
    const fileMeta = document.querySelector("[data-file-meta]");
    const stepper = document.querySelector("[data-workflow-stepper]");
    const recentOperations = document.querySelector("[data-recent-operations]");
    const historyStatusBadge = document.querySelector("[data-history-status-badge]");
    const operationCreatedAt = document.querySelector("[data-operation-created-at]");
    const operationUpdatedAt = document.querySelector("[data-operation-updated-at]");
    const operationId = document.querySelector("[data-operation-id]");
    const operationStatus = document.querySelector("[data-operation-status]");
    const operationStatusBadge = document.querySelector("[data-operation-status-badge]");
    const operationProduct = document.querySelector("[data-operation-product]");
    const operationPolicy = document.querySelector("[data-operation-policy]");
    const operationOrigin = document.querySelector("[data-operation-origin]");
    const operationOutput = document.querySelector("[data-operation-output]");
    const operationDuration = document.querySelector("[data-operation-duration]");
    const operationObservation = document.querySelector("[data-operation-observation]");

    const traceabilityElements = {
        sessionUser: sessionUserLabel,
        createdAt: operationCreatedAt,
        updatedAt: operationUpdatedAt,
        id: operationId,
        status: operationStatus,
        statusBadge: operationStatusBadge,
        product: operationProduct,
        policy: operationPolicy,
        origin: operationOrigin,
        output: operationOutput,
        duration: operationDuration,
        observation: operationObservation,
    };

    let activeProducts = [];
    let currentOperation = hydrateStoredOperation(operationStore.read());
    let sessionUserText = "Sesión activa";
    let activeFile = null;
    let lastOperationTimestamp = currentOperation?._frontend_meta?.last_transition_at || null;
    let recentItems = readRecentOperations();

    const getSelectedProduct = () => activeProducts.find((item) => item.id === productSelect?.value) || null;
    const getSelectedProductLabel = () => getSelectedProduct()?.name || currentOperation?._frontend_meta?.product_label || null;
    const policyNumberInput = documentForm?.elements.policy_number || null;
    const fileInput = documentForm?.elements.file || null;

    function setFeedback(message, variant = "info") {
        if (!documentFeedback) {
            return;
        }

        documentFeedback.textContent = message || "";
        documentFeedback.className = `form-feedback alert alert--${variant}`;
    }

    function setProductsStatus(text, variant = "neutral") {
        if (!productsStatus) {
            return;
        }

        productsStatus.textContent = text;
        productsStatus.className = `status-pill badge status-pill--${variant === "neutral" ? "neutral" : variant}`;
    }

    function setHistoryStatus(text, variant = "neutral") {
        if (!historyStatusBadge) {
            return;
        }

        historyStatusBadge.textContent = text;
        historyStatusBadge.className = `status-pill badge status-pill--${variant === "neutral" ? "neutral" : variant}`;
    }

    function buildTraceabilityContext({ loading = false } = {}) {
        return {
            loading,
            selectedProduct: getSelectedProduct(),
            policyNumber: currentOperation?.policy_number || policyNumberInput?.value.trim() || "",
            activeFileName: activeFile?.name || currentOperation?.original_filename || "",
            fallbackTimestamp: lastOperationTimestamp,
        };
    }

    function syncOperationProductLabel() {
        if (!currentOperation) {
            return;
        }

        const productLabel = getSelectedProductLabel();
        if (!productLabel) {
            return;
        }

        currentOperation = attachFrontendMeta(currentOperation, {
            product_label: productLabel,
        });
    }

    function renderFileMeta(file) {
        if (!fileMeta) {
            return;
        }

        if (!file && currentOperation?.original_filename) {
            fileMeta.innerHTML = `
                <div class="document-meta__list">
                    <div class="document-meta__row">
                        <span class="document-meta__label">Archivo registrado</span>
                        <span class="document-meta__value">${currentOperation.original_filename}</span>
                    </div>
                    <div class="document-meta__row">
                        <span class="document-meta__label">Estado</span>
                        <span class="document-meta__value">Registro vigente en esta sesión</span>
                    </div>
                    <div class="document-meta__row">
                        <span class="document-meta__label">Compatibilidad</span>
                        <span class="document-meta__value">DOCX registrado</span>
                    </div>
                </div>
            `;
            return;
        }

        if (!file) {
            fileMeta.innerHTML = `
                <div class="document-meta__empty empty-state empty-state--compact">
                    <strong>Sin archivo cargado</strong>
                    <span class="empty-state__text">Selecciona una prepóliza para validar nombre, extensión y tamaño antes de continuar.</span>
                </div>
            `;
            return;
        }

        const extension = file.name.includes(".") ? file.name.split(".").pop().toLowerCase() : "sin extensión";
        const isDocx = extension === "docx";
        fileMeta.innerHTML = `
            <div class="document-meta__list">
                <div class="document-meta__row">
                    <span class="document-meta__label">Archivo</span>
                    <span class="document-meta__value">${file.name}</span>
                </div>
                <div class="document-meta__row">
                    <span class="document-meta__label">Tamaño</span>
                    <span class="document-meta__value">${formatFileSize(file.size)}</span>
                </div>
                <div class="document-meta__row">
                    <span class="document-meta__label">Compatibilidad</span>
                    <span class="document-meta__value">${isDocx ? "DOCX válido" : "Formato no compatible"}</span>
                </div>
            </div>
        `;
    }

    function pushRecentOperation(operation) {
        if (!operation) {
            return;
        }

        const normalized = {
            id: operation.id,
            status: operation.status,
            policy_number: operation.policy_number,
            original_filename: operation.original_filename,
            output_path: operation.output_path || "",
            error_message: operation.error_message || "",
            product_label: operation._frontend_meta?.product_label || getSelectedProductLabel() || "Operación documental",
            created_at: operation.created_at || operation._frontend_meta?.registered_at || null,
            updated_at: operation.updated_at || operation._frontend_meta?.processed_at || operation._frontend_meta?.last_transition_at || null,
            timestamp: operation._frontend_meta?.last_transition_at || operation._frontend_meta?.registered_at || null,
        };

        recentItems = [normalized, ...recentItems.filter((item) => item.id !== operation.id)].slice(0, 5);
        writeRecentOperations(recentItems);
        renderRecentOperations(recentOperations, recentItems);
        setHistoryStatus(`${recentItems.length} registro(s)`, recentItems.length ? "info" : "neutral");
    }

    function invalidateRegisteredOperation(message = "Los datos cambiaron. Guarda un nuevo registro para continuar.") {
        if (!currentOperation) {
            return;
        }

        currentOperation = null;
        lastOperationTimestamp = null;
        operationStore.clear();
        setFeedback(message, "warning");
    }

    function updateStepper() {
        if (!stepper) {
            return;
        }

        const hasUploadedFile = Boolean(activeFile || currentOperation?.original_filename);
        const selectedProduct = Boolean(productSelect?.value || currentOperation?.product_id);
        const hasPolicy = Boolean(policyNumberInput?.value.trim() || currentOperation?.policy_number);
        const hasValidation = Boolean(currentOperation?.id) || (selectedProduct && hasPolicy && hasUploadedFile);
        const hasRegisteredOperation = Boolean(currentOperation?.id);
        const isProcessing = currentOperation?.status === "PROCESSING";
        const isCompleted = currentOperation?.status === "COMPLETED";

        const stepStates = {
            upload: hasUploadedFile,
            product: selectedProduct,
            validation: hasValidation,
            processing: hasRegisteredOperation,
            download: isCompleted,
        };

        stepper.querySelectorAll("[data-step]").forEach((stepElement) => {
            const stepName = stepElement.dataset.step;
            stepElement.classList.remove("is-current", "is-complete", "is-disabled");

            if (stepName === "download") {
                if (stepStates.download) {
                    stepElement.classList.add("is-current", "is-complete");
                } else {
                    stepElement.classList.add("is-disabled");
                }
                return;
            }

            if (stepName === "processing") {
                if (isCompleted) {
                    stepElement.classList.add("is-complete");
                } else if (isProcessing || hasRegisteredOperation) {
                    stepElement.classList.add("is-current");
                } else if (!stepStates.validation) {
                    stepElement.classList.add("is-disabled");
                }
                return;
            }

            if (stepStates[stepName]) {
                stepElement.classList.add("is-complete");
            } else if (
                (stepName === "upload") ||
                (stepName === "product" && hasUploadedFile) ||
                (stepName === "validation" && selectedProduct && hasPolicy)
            ) {
                stepElement.classList.add("is-current");
            } else {
                stepElement.classList.add("is-disabled");
            }
        });
    }

    function updateValidationState() {
        const selectedProduct = Boolean(productSelect?.value);
        const hasPolicy = Boolean(policyNumberInput?.value.trim());
        const hasFile = Boolean(activeFile);
        const isDocx = activeFile ? activeFile.name.toLowerCase().endsWith(".docx") : false;
        const readyToRegister = selectedProduct && hasPolicy && hasFile && isDocx;
        const readyToProcess = Boolean(currentOperation?.id) && !["PROCESSING", "COMPLETED"].includes(currentOperation?.status);

        if (validationBadge) {
            if (readyToProcess) {
                validationBadge.textContent = "Registro listo";
                validationBadge.className = "status-pill badge status-pill--success badge--success";
            } else if (currentOperation?.status === "COMPLETED") {
                validationBadge.textContent = "Procesado";
                validationBadge.className = "status-pill badge status-pill--success badge--success";
            } else if (readyToRegister) {
                validationBadge.textContent = "Validación correcta";
                validationBadge.className = "status-pill badge status-pill--info badge--active";
            } else if (hasFile && !isDocx) {
                validationBadge.textContent = "Archivo inválido";
                validationBadge.className = "status-pill badge status-pill--danger badge--error";
            } else {
                validationBadge.textContent = "Faltan datos";
                validationBadge.className = "status-pill badge status-pill--neutral badge--pending";
            }
        }

        if (validationFeedback) {
            validationFeedback.className = "helper-feedback alert alert--info";
            if (readyToProcess) {
                validationFeedback.textContent = "La operación ya fue registrada. Ejecuta el procesamiento documental cuando estés listo.";
            } else if (currentOperation?.status === "COMPLETED") {
                validationFeedback.textContent = "El documento ya fue procesado. Si necesitas otra ejecución, limpia el formulario o registra una nueva operación.";
            } else if (readyToRegister) {
                validationFeedback.textContent = "La información mínima está completa. Guarda el registro para habilitar el procesamiento.";
            } else if (hasFile && !isDocx) {
                validationFeedback.className = "helper-feedback alert alert--error";
                validationFeedback.textContent = "El archivo seleccionado no corresponde a un DOCX válido para este flujo.";
            } else if (!selectedProduct) {
                validationFeedback.className = "helper-feedback alert alert--warning";
                validationFeedback.textContent = "Selecciona un producto para cargar la configuración aplicable.";
            } else {
                validationFeedback.textContent = "Completa producto, número de póliza y archivo para habilitar el procesamiento.";
            }
        }

        if (registerButton && !registerButton.classList.contains("is-loading")) {
            registerButton.disabled = !readyToRegister;
        }

        if (processButton && !processButton.classList.contains("is-loading")) {
            processButton.disabled = !readyToProcess;
        }

        updateStepper();
    }

    function refreshOperationalPanels() {
        syncOperationProductLabel();
        renderProductSummary(productSummary, getSelectedProduct());
        renderProcessingResult(resultPanel, resultBadge, downloadButton, currentOperation);
        renderTraceabilityPanel(traceabilityElements, sessionUserText, currentOperation, buildTraceabilityContext());
        renderRecentOperations(recentOperations, recentItems);
        setHistoryStatus(recentItems.length ? `${recentItems.length} registro(s)` : "Sin registros", recentItems.length ? "info" : "neutral");
        updateValidationState();
    }

    async function loadProducts() {
        if (!productSelect || !productsStatus) {
            return;
        }

        setProductsStatus("Cargando catálogo...");
        const result = await authorizedRequest(appConfig.productsBaseUrl, "", { method: "GET" });
        if (!result.payload.success) {
            setProductsStatus("Catálogo no disponible", "danger");
            setFeedback(result.payload.message || "No fue posible cargar el catálogo de productos.", "error");
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

        setProductsStatus(`${activeProducts.length} producto(s) activos`, "success");

        const productId = currentOperation?.product_id;
        if (productId) {
            productSelect.value = productId;
            syncOperationProductLabel();
        }
    }

    function resetWorkflow({ keepHistory = true } = {}) {
        if (documentForm) {
            documentForm.reset();
        }
        currentOperation = null;
        activeFile = null;
        lastOperationTimestamp = null;
        operationStore.clear();
        renderFileMeta(null);
        if (!keepHistory) {
            recentItems = [];
            writeRecentOperations(recentItems);
        }
        setFeedback("", "info");
        refreshOperationalPanels();
    }

    async function handleDocumentUpload(event) {
        event.preventDefault();
        if (!documentForm) {
            return;
        }

        const formData = new FormData(documentForm);
        setFeedback("Guardando registro documental...", "info");
        setButtonLoading(registerButton, true, "Guardar registro", "Guardando...");

        const result = await authorizedRequest(appConfig.documentsBaseUrl, "/upload", {
            method: "POST",
            body: formData,
        });

        setButtonLoading(registerButton, false, "Guardar registro", "Guardando...");

        if (!result.payload.success) {
            setFeedback(result.payload.message || "No fue posible registrar el documento.", "error");
            refreshOperationalPanels();
            return;
        }

        const now = getNowIso();
        currentOperation = attachFrontendMeta(result.payload.data, {
            registered_at: now,
            last_transition_at: now,
            product_label: getSelectedProductLabel(),
        });
        lastOperationTimestamp = now;
        operationStore.write(currentOperation);
        pushRecentOperation(currentOperation);
        setFeedback(result.payload.message || "Registro documental guardado.", "success");
        renderFileMeta(activeFile);
        refreshOperationalPanels();
    }

    async function handleProcessOperation() {
        if (!currentOperation) {
            return;
        }

        const processingStartedAt = getNowIso();
        setFeedback("Aplicando formato y generando documento...", "warning");
        setButtonLoading(processButton, true, "Aplicar formato y generar Word", "Procesando...");
        currentOperation = attachFrontendMeta(
            { ...currentOperation, status: "PROCESSING" },
            {
                registered_at: currentOperation._frontend_meta?.registered_at || processingStartedAt,
                processing_started_at: currentOperation._frontend_meta?.processing_started_at || processingStartedAt,
                last_transition_at: processingStartedAt,
                product_label: currentOperation._frontend_meta?.product_label || getSelectedProductLabel(),
            },
        );
        lastOperationTimestamp = processingStartedAt;
        operationStore.write(currentOperation);
        refreshOperationalPanels();

        const result = await authorizedRequest(appConfig.documentsBaseUrl, `/${currentOperation.id}/process`, {
            method: "POST",
        });

        setButtonLoading(processButton, false, "Aplicar formato y generar Word", "Procesando...");

        if (!result.payload.success) {
            const failedAt = getNowIso();
            currentOperation = attachFrontendMeta(
                {
                    ...currentOperation,
                    status: "ERROR",
                    error_message: result.payload.message || "No fue posible procesar el documento.",
                },
                {
                    processed_at: failedAt,
                    last_transition_at: failedAt,
                    product_label: currentOperation._frontend_meta?.product_label || getSelectedProductLabel(),
                },
            );
            lastOperationTimestamp = failedAt;
            setFeedback(currentOperation.error_message, "error");
            operationStore.write(currentOperation);
            pushRecentOperation(currentOperation);
            refreshOperationalPanels();
            return;
        }

        const completedAt = getNowIso();
        currentOperation = attachFrontendMeta(result.payload.data, {
            registered_at: currentOperation._frontend_meta?.registered_at || completedAt,
            processing_started_at: currentOperation._frontend_meta?.processing_started_at || completedAt,
            processed_at: completedAt,
            last_transition_at: completedAt,
            product_label: currentOperation._frontend_meta?.product_label || getSelectedProductLabel(),
        });
        lastOperationTimestamp = completedAt;
        operationStore.write(currentOperation);
        pushRecentOperation(currentOperation);
        setFeedback(result.payload.message || "Documento procesado correctamente.", "success");
        refreshOperationalPanels();
    }

    logoutButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            await logoutCurrentSession();
            window.location.assign("/login");
        });
    });

    if (productSelect) {
        productSelect.addEventListener("change", () => {
            invalidateRegisteredOperation();
            refreshOperationalPanels();
        });
    }

    if (policyNumberInput) {
        policyNumberInput.addEventListener("input", () => {
            invalidateRegisteredOperation();
            refreshOperationalPanels();
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", () => {
            activeFile = fileInput.files?.[0] || null;
            invalidateRegisteredOperation();
            renderFileMeta(activeFile);
            refreshOperationalPanels();
        });
    }

    if (documentForm) {
        documentForm.addEventListener("submit", handleDocumentUpload);
    }

    if (processButton) {
        processButton.addEventListener("click", handleProcessOperation);
    }

    if (clearButton) {
        clearButton.addEventListener("click", () => {
            resetWorkflow();
        });
    }

    if (resetResultButton) {
        resetResultButton.addEventListener("click", () => {
            resetWorkflow();
        });
    }

    if (downloadButton) {
        downloadButton.addEventListener("click", () => {
            if (!currentOperation?.output_path) {
                return;
            }
            setFeedback("La salida ya fue generada. La descarga web estará disponible cuando el backend exponga ese endpoint.", "info");
        });
    }

    renderRecentOperations(recentOperations, recentItems, { loading: true });
    setHistoryStatus("Cargando historial");
    renderTraceabilityPanel(traceabilityElements, sessionUserText, currentOperation, buildTraceabilityContext({ loading: true }));
    await populateSessionUser(sessionUserLabel);
    sessionUserText = sessionUserLabel?.textContent || `Sesión activa: ${sessionStore.read()?.user?.username || "usuario"}`;
    await loadProducts();
    if (currentOperation?.product_id && productSelect) {
        productSelect.value = currentOperation.product_id;
        syncOperationProductLabel();
    }
    renderFileMeta(activeFile);
    refreshOperationalPanels();
}
