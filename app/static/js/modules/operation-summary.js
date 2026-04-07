function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function formatDateTime(value) {
    if (!value) {
        return "Sin registro";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return escapeHtml(value);
    }

    return new Intl.DateTimeFormat("es-PE", {
        dateStyle: "short",
        timeStyle: "short",
    }).format(date);
}

function formatDuration(startValue, endValue) {
    if (!startValue) {
        return "Sin cálculo disponible";
    }

    const start = new Date(startValue);
    const end = endValue ? new Date(endValue) : new Date();
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
        return "Sin cálculo disponible";
    }

    const diffMs = Math.max(0, end.getTime() - start.getTime());
    const totalSeconds = Math.round(diffMs / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    if (minutes <= 0) {
        return `${seconds}s`;
    }

    return `${minutes}m ${seconds}s`;
}

function resolveFrontendMeta(operation) {
    return operation?._frontend_meta || {};
}

function resolveOperationDates(operation) {
    const meta = resolveFrontendMeta(operation);
    return {
        createdAt: operation?.created_at || meta.registered_at || null,
        updatedAt: operation?.updated_at || meta.processed_at || meta.last_transition_at || meta.registered_at || null,
        processingStartedAt: meta.processing_started_at || null,
        processedAt: meta.processed_at || null,
    };
}

function getStatusPresentation(status) {
    const normalized = String(status || "").toUpperCase();

    if (normalized === "PROCESSING") {
        return {
            label: "Procesamiento en curso",
            badgeClass: "status-pill--warning badge--processing",
            detail: "Motor DOCX ejecutándose",
        };
    }

    if (normalized === "COMPLETED") {
        return {
            label: "Procesado exitosamente",
            badgeClass: "status-pill--success badge--success",
            detail: "Salida disponible en almacenamiento interno",
        };
    }

    if (normalized === "ERROR") {
        return {
            label: "Procesado con error",
            badgeClass: "status-pill--danger badge--error",
            detail: "La ejecución requiere revisión o reintento",
        };
    }

    if (normalized === "RECEIVED") {
        return {
            label: "Documento registrado",
            badgeClass: "status-pill--info badge--active",
            detail: "Listo para pasar al motor de formateo",
        };
    }

    return {
        label: "Pendiente",
        badgeClass: "status-pill--neutral badge--pending",
        detail: "Sin actividad documental",
    };
}

function getObservationText(operation, uiState, context = {}) {
    if (operation?.error_message) {
        return operation.error_message;
    }

    if (uiState.key === "success") {
        return operation?.output_path
            ? "La salida fue generada correctamente y queda lista para exponerse cuando exista el endpoint de descarga."
            : "La operación finalizó correctamente. La descarga web se habilitará cuando el backend exponga ese endpoint.";
    }

    if (uiState.key === "processing") {
        return "El documento se encuentra en ejecución. Evita lanzar una nueva operación hasta que este estado cambie.";
    }

    if (uiState.key === "ready") {
        return "La información mínima ya fue registrada. El siguiente paso es aplicar formato y generar el Word final.";
    }

    if (context.selectedProduct || context.policyNumber || context.activeFileName) {
        return "Hay un borrador en preparación. Guarda el registro para dejar trazabilidad formal de la operación.";
    }

    return "Cuando exista una operación activa, aquí verás su contexto, estado y observaciones operativas.";
}

function getHistoryDetail(operation) {
    const statusInfo = getStatusPresentation(operation?.status);
    if (operation?.error_message) {
        return operation.error_message;
    }
    if (operation?.status === "COMPLETED") {
        return operation.output_path ? "Salida generada" : statusInfo.detail;
    }
    return statusInfo.detail;
}

export function getOperationUiState(operation) {
    if (!operation) {
        return {
            key: "pending",
            label: "Pendiente",
            badgeClass: "status-pill--neutral badge--pending",
            panelClass: "result-panel__state--pending",
            summary: "Aún no se ha registrado ninguna operación en esta sesión.",
        };
    }

    if (operation.status === "PROCESSING") {
        return {
            key: "processing",
            label: "Procesando",
            badgeClass: "status-pill--warning badge--processing",
            panelClass: "result-panel__state--processing",
            summary: "Aplicando formato y generando documento sobre la prepóliza registrada.",
        };
    }

    if (operation.status === "COMPLETED") {
        return {
            key: "success",
            label: "Éxito",
            badgeClass: "status-pill--success badge--success",
            panelClass: "result-panel__state--success",
            summary: "El documento quedó procesado y la salida fue generada en el almacenamiento interno.",
        };
    }

    if (operation.status === "ERROR") {
        return {
            key: "error",
            label: "Error",
            badgeClass: "status-pill--danger badge--error",
            panelClass: "result-panel__state--error",
            summary: "La operación falló durante el procesamiento y requiere revisión o reintento.",
        };
    }

    return {
        key: "ready",
        label: "Listo para procesar",
        badgeClass: "status-pill--info badge--active",
        panelClass: "result-panel__state--ready",
        summary: "La operación quedó registrada y está lista para ejecutar el formateo DOCX.",
    };
}

export function renderProcessingResult(container, badge, downloadButton, operation) {
    if (!container || !badge) {
        return;
    }

    const uiState = getOperationUiState(operation);
    badge.textContent = uiState.label;
    badge.className = `status-pill badge ${uiState.badgeClass}`;

    if (!operation) {
        container.innerHTML = `
            <div class="result-panel__state ${uiState.panelClass} empty-state empty-state--compact">
                <strong>Sin procesamiento activo</strong>
                <p class="empty-state__text">${uiState.summary}</p>
            </div>
        `;
        if (downloadButton) {
            downloadButton.disabled = true;
        }
        return;
    }

    const hasDownload = Boolean(operation.output_path && operation.status === "COMPLETED");
    const dates = resolveOperationDates(operation);
    if (downloadButton) {
        downloadButton.disabled = !hasDownload;
    }

    container.innerHTML = `
        <div class="result-panel__state ${uiState.panelClass}">
            <strong>${uiState.label}</strong>
            <p>${uiState.summary}</p>
        </div>
        <dl class="summary-list result-panel__list">
            <div><dt>ID operación</dt><dd>${escapeHtml(operation.id)}</dd></div>
            <div><dt>Estado backend</dt><dd>${escapeHtml(operation.status)}</dd></div>
            <div><dt>Póliza</dt><dd>${escapeHtml(operation.policy_number)}</dd></div>
            <div><dt>Archivo origen</dt><dd>${escapeHtml(operation.original_filename)}</dd></div>
            <div><dt>Salida generada</dt><dd>${escapeHtml(operation.output_path || "Pendiente")}</dd></div>
            <div><dt>Registrado</dt><dd>${formatDateTime(dates.createdAt)}</dd></div>
            <div><dt>Última actualización</dt><dd>${formatDateTime(dates.updatedAt)}</dd></div>
            <div><dt>Observación</dt><dd>${escapeHtml(operation.error_message || uiState.summary)}</dd></div>
        </dl>
    `;
}

export function renderTraceabilityPanel(panelElements, sessionLabelText, operation, context = {}) {
    if (!panelElements) {
        return;
    }

    const selectedProduct = context.selectedProduct || null;
    const dates = resolveOperationDates(operation);
    const statusInfo = getStatusPresentation(operation?.status);
    const observationText = getObservationText(operation, getOperationUiState(operation), context);
    const hasDraftContext = Boolean(selectedProduct || context.policyNumber || context.activeFileName);

    if (panelElements.sessionUser && sessionLabelText) {
        panelElements.sessionUser.textContent = sessionLabelText;
    }

    if (context.loading) {
        if (panelElements.statusBadge) {
            panelElements.statusBadge.textContent = "Cargando contexto";
            panelElements.statusBadge.className = "status-pill badge status-pill--neutral badge--pending";
        }
        if (panelElements.createdAt) {
            panelElements.createdAt.textContent = "Preparando trazabilidad...";
        }
        if (panelElements.updatedAt) {
            panelElements.updatedAt.textContent = "Preparando trazabilidad...";
        }
        if (panelElements.id) {
            panelElements.id.textContent = "Sin registrar";
        }
        if (panelElements.status) {
            panelElements.status.textContent = "Cargando";
        }
        if (panelElements.product) {
            panelElements.product.textContent = selectedProduct?.name || "Sin producto";
        }
        if (panelElements.policy) {
            panelElements.policy.textContent = context.policyNumber || "Sin póliza";
        }
        if (panelElements.origin) {
            panelElements.origin.textContent = context.activeFileName || "Sin archivo";
        }
        if (panelElements.output) {
            panelElements.output.textContent = "Pendiente";
        }
        if (panelElements.duration) {
            panelElements.duration.textContent = "Sin cálculo disponible";
        }
        if (panelElements.observation) {
            panelElements.observation.textContent = "Cargando contexto operativo de la sesión...";
            panelElements.observation.className = "alert alert--info traceability-note";
        }
        return;
    }

    const productLabel = operation?._frontend_meta?.product_label || selectedProduct?.name || "Sin producto seleccionado";
    const policyLabel = operation?.policy_number || context.policyNumber || "Sin número de póliza";
    const originLabel = operation?.original_filename || context.activeFileName || "Sin archivo cargado";
    const outputLabel = operation?.output_path || "Pendiente";
    const statusLabel = operation ? statusInfo.label : hasDraftContext ? "Borrador en preparación" : "Sin iniciar";
    const statusBadgeClass = operation
        ? statusInfo.badgeClass
        : hasDraftContext
            ? "status-pill--info badge--active"
            : "status-pill--neutral badge--pending";
    const createdAtLabel = operation ? formatDateTime(dates.createdAt || context.fallbackTimestamp) : "Sin registrar";
    const updatedAtLabel = operation
        ? formatDateTime(dates.updatedAt || context.fallbackTimestamp)
        : hasDraftContext
            ? "Pendiente de registro"
            : "Sin cambios";
    const durationLabel = operation
        ? (operation.status === "RECEIVED"
            ? "Pendiente de procesamiento"
            : operation.status === "PROCESSING"
                ? `En curso · ${formatDuration(dates.processingStartedAt || dates.createdAt, null)}`
                : formatDuration(dates.processingStartedAt || dates.createdAt, dates.processedAt || dates.updatedAt))
        : "Disponible cuando exista una ejecución";

    if (panelElements.statusBadge) {
        panelElements.statusBadge.textContent = statusLabel;
        panelElements.statusBadge.className = `status-pill badge ${statusBadgeClass}`;
    }
    if (panelElements.createdAt) {
        panelElements.createdAt.textContent = createdAtLabel;
    }
    if (panelElements.updatedAt) {
        panelElements.updatedAt.textContent = updatedAtLabel;
    }
    if (panelElements.id) {
        panelElements.id.textContent = operation?.id || "Pendiente";
    }
    if (panelElements.status) {
        panelElements.status.textContent = statusLabel;
    }
    if (panelElements.product) {
        panelElements.product.textContent = productLabel;
    }
    if (panelElements.policy) {
        panelElements.policy.textContent = policyLabel;
    }
    if (panelElements.origin) {
        panelElements.origin.textContent = originLabel;
    }
    if (panelElements.output) {
        panelElements.output.textContent = outputLabel;
    }
    if (panelElements.duration) {
        panelElements.duration.textContent = durationLabel;
    }
    if (panelElements.observation) {
        const isError = operation?.status === "ERROR";
        const isSuccess = operation?.status === "COMPLETED";
        panelElements.observation.textContent = observationText;
        panelElements.observation.className = `alert ${isError ? "alert--error" : isSuccess ? "alert--success" : "alert--info"} traceability-note`;
    }
}

export function renderRecentOperations(container, operations, options = {}) {
    if (!container) {
        return;
    }

    if (options.loading) {
        container.innerHTML = `
            <div class="empty-state empty-state--compact">
                <strong>Cargando historial reciente</strong>
                <span class="empty-state__text">Preparando el resumen de operaciones visibles en esta sesión.</span>
            </div>
        `;
        return;
    }

    if (!operations.length) {
        container.innerHTML = `
            <div class="empty-state empty-state--compact">
                <strong>Sin operaciones recientes</strong>
                <span class="empty-state__text">Los registros documentales recientes aparecerán aquí para dar contexto operativo inmediato.</span>
            </div>
            <p class="traceability-footnote">La vista histórica completa quedará preparada para una fase posterior sin interrumpir el flujo principal.</p>
        `;
        return;
    }

    container.innerHTML = `
        <div class="history-table-wrapper">
            <table class="data-table data-table--compact history-table">
                <thead>
                    <tr>
                        <th>Fecha / hora</th>
                        <th>Producto</th>
                        <th>Póliza</th>
                        <th>Estado</th>
                        <th>Detalle</th>
                    </tr>
                </thead>
                <tbody>
                    ${operations.map((operation) => {
                        const statusInfo = getStatusPresentation(operation.status);
                        const detail = getHistoryDetail(operation);
                        const timestamp = operation.updated_at || operation.created_at || operation.timestamp;
                        return `
                            <tr>
                                <td>${escapeHtml(formatDateTime(timestamp))}</td>
                                <td>
                                    <div class="history-table__primary">${escapeHtml(operation.product_label || "Operación documental")}</div>
                                    <div class="history-table__secondary">${escapeHtml(operation.original_filename || "Sin archivo origen")}</div>
                                </td>
                                <td>${escapeHtml(operation.policy_number || "Sin póliza")}</td>
                                <td><span class="status-pill badge ${statusInfo.badgeClass}">${escapeHtml(statusInfo.label)}</span></td>
                                <td>${escapeHtml(detail)}</td>
                            </tr>
                        `;
                    }).join("")}
                </tbody>
            </table>
        </div>
        <p class="traceability-footnote">Resumen reciente de la sesión actual. La trazabilidad histórica completa se integrará cuando exista la vista dedicada.</p>
    `;
}


