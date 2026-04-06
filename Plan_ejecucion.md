# Plan de ejecución por sprints — MVP Formateador Web de Prepólizas Word

## 1. Propósito del documento
Este documento aterriza el blueprint funcional y técnico del MVP a un **plan ejecutable por sprints**, pensado para trabajar con **Codex en VS Code** como agente de implementación.

El objetivo no es solo definir qué construir, sino **en qué orden**, **con qué criterios de aceptación**, **con qué riesgos controlados** y **con qué prompts concretos** para acelerar el desarrollo sin perder modularidad.

---

## 2. Supuestos de ejecución

### 2.1. Supuestos base
Se asume lo siguiente para este plan:

- El producto será de **despliegue local corporativo**.
- El stack es obligatorio:
  - **Backend:** FastAPI
  - **Frontend:** HTML, CSS y JavaScript vanilla
  - **DB desarrollo:** MariaDB
  - **DB producción:** Oracle
  - **Seguridad:** `pyjwt` + `argon2`
- El formato de entrada y salida del MVP será **solo `.docx`**.
- El objetivo del MVP es **estabilidad documental**, no edición visual avanzada.
- Se trabajará con **Codex** como agente de implementación asistida, por lo que cada sprint debe terminar con módulos cerrados y verificables.

### 2.2. Cadencia propuesta
Se propone trabajar con:

- **Sprint 0** de definición y preparación.
- **6 sprints de construcción**.
- **Duración sugerida por sprint:** 1 semana.

Esta cadencia funciona bien para un MVP con alta dependencia técnica del motor DOCX, porque permite validar temprano los riesgos más peligrosos sin esperar iteraciones largas.

### 2.3. Enfoque de priorización
La prioridad del proyecto debe seguir este orden:

1. Base técnica sólida.
2. Seguridad y sesión.
3. Flujo documental controlado.
4. Motor de formateo DOCX.
5. Trazabilidad.
6. Integración end-to-end.
7. Endurecimiento para despliegue local.

---

## 3. Objetivo del MVP
Desarrollar un aplicativo web que permita:

1. iniciar sesión,
2. cargar una prepóliza en formato Word (`.docx`),
3. aplicar un formato predefinido,
4. reemplazar encabezado según producto y número de póliza,
5. insertar título según producto,
6. mantener estructura, tablas e imágenes,
7. exportar la póliza final en Word,
8. registrar trazabilidad básica por usuario.

---

## 4. Estrategia de ejecución

## 4.1. Principio rector
El proyecto debe ejecutarse alrededor de esta regla:

> **El corazón del producto es el motor de manipulación DOCX con preservación estructural.**

Por eso los sprints no deben centrarse primero en “pantallas bonitas”, sino en dejar lista la arquitectura, la seguridad y la ruta de procesamiento documental.

## 4.2. Estrategia de implementación con Codex
Para trabajar bien con un agente de IA, cada sprint debe dividirse en piezas pequeñas con estas reglas:

- pedir primero análisis de impacto,
- pedir siempre lista de archivos a crear o modificar,
- exigir separación por capas,
- pedir pruebas mínimas por módulo,
- evitar prompts genéricos del tipo “hazme el sistema completo”.

## 4.3. Criterio de cierre por sprint
Cada sprint debe cerrar con:

- código integrado en una rama funcional,
- pruebas ejecutables del alcance del sprint,
- validación manual mínima,
- deuda técnica documentada,
- prompt de continuación para el siguiente sprint.

---

## 5. Vista general del roadmap

| Sprint | Objetivo principal | Resultado esperado |
|---|---|---|
| Sprint 0 | Alineamiento funcional y técnico | Insumos, reglas y arquitectura objetivo cerrada |
| Sprint 1 | Bootstrap del proyecto | Base FastAPI + frontend vanilla + configuración por entorno |
| Sprint 2 | Seguridad y sesión | Login, JWT, refresh token, guardas y frontend de sesión |
| Sprint 3 | Dominio documental y catálogo | Carga `.docx`, validación, productos y metadatos |
| Sprint 4 | Motor DOCX MVP | Formateo base + header + título + exportación segura |
| Sprint 5 | Trazabilidad e integración | Historial, auditoría y flujo principal completo |
| Sprint 6 | Hardening MVP | Limpieza, errores, observabilidad y preparación Oracle |

---

## 6. Definition of Ready (DoR)
Una historia o tarea entra a sprint solo si:

- tiene objetivo funcional claro,
- tiene criterios de aceptación verificables,
- identifica archivos o módulos impactados,
- define si requiere prueba unitaria, integración o validación manual,
- no depende de una decisión funcional aún abierta.

---

## 7. Definition of Done (DoD)
Una tarea se considera terminada solo si:

- está implementada en la capa correcta,
- no deja lógica crítica en rutas o JS inline,
- incluye validaciones mínimas,
- incluye manejo de errores razonable,
- tiene prueba o evidencia funcional,
- deja documentación breve de uso o limitaciones,
- no rompe la arquitectura acordada.

---