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

## 8. Sprint 0 — Descubrimiento y preparación

## 8.1. Objetivo
Cerrar insumos funcionales y reducir la ambigüedad antes de pedir implementación a Codex.

## 8.2. Entregables del sprint
- catálogo inicial de productos,
- ejemplos reales de encabezados por producto,
- definición del título por producto,
- definición del formato base,
- set de prepólizas reales de prueba,
- decisión de almacenamiento local,
- criterios exactos de trazabilidad,
- decisión de política de inserción del título.

## 8.3. Tareas

### Funcionales
- Definir 3 a 5 productos del MVP.
- Definir plantilla de encabezado por producto.
- Definir reglas mínimas de formato base.
- Definir si el título reemplaza, inserta o antecede el primer bloque.

### Técnicas
- Confirmar estándar de nombres de archivos temporales.
- Confirmar tamaño máximo permitido de `.docx`.
- Confirmar duración de refresh token.
- Confirmar si se registrará IP, hostname o ambos para trazabilidad.

### Insumos de prueba
- Preparar al menos 10 documentos de prueba distribuidos así:
  - 3 documentos simples,
  - 3 con tablas,
  - 2 con imágenes,
  - 2 con múltiples secciones y headers.

## 8.4. Riesgos que se buscan reducir
- ambigüedad del header por producto,
- inserción de título que rompa maquetación,
- expectativas incorrectas sobre preservación del Word,
- alcance inflado del MVP.

## 8.5. Criterios de aceptación
- Existe una matriz de productos con reglas mínimas.
- Existe un paquete de documentos de prueba representativo.
- Existe una definición cerrada de trazabilidad del MVP.
- Existe acuerdo explícito sobre qué sí y qué no tocará el motor DOCX.

## 8.6. Salida esperada para el sprint siguiente
Un repositorio o carpeta de trabajo con insumos funcionales listos para que Codex implemente sin adivinar reglas.

---

## 9. Sprint 1 — Bootstrap técnico del proyecto

## 9.1. Objetivo
Dejar lista la base estructural del sistema sin meter todavía la lógica de negocio compleja.

## 9.2. Alcance
- estructura modular FastAPI,
- soporte frontend vanilla,
- configuración por entorno,
- conexión base a MariaDB,
- preparación para Oracle,
- logging base,
- shell UI con sidebar colapsable.

## 9.3. Historias del sprint

### Historia 1
**Como equipo técnico, quiero una estructura modular del backend para evitar deuda técnica temprana.**

#### Criterios de aceptación
- Existe estructura `api`, `services`, `repositories`, `infrastructure`, `core`.
- Los endpoints están versionados en `/api/v1`.
- La aplicación levanta correctamente con configuración por entorno.

### Historia 2
**Como usuario, quiero ver una base visual estable para iniciar sesión y navegar al módulo principal.**

#### Criterios de aceptación
- Existe vista login.
- Existe layout con sidebar izquierdo colapsable.
- Existe vista principal vacía para módulo documental.

### Historia 3
**Como equipo, quiero una configuración portable entre desarrollo y producción.**

#### Criterios de aceptación
- La configuración se separa por entorno.
- El código no queda amarrado a MariaDB.
- La capa DB está abstraída de la lógica de negocio.

## 9.4. Tareas técnicas sugeridas
- Crear estructura base del proyecto.
- Preparar `main.py`, rutas base, templates y static.
- Preparar configuración `.env` y clases de settings.
- Preparar sesión DB y modelo base ORM.
- Incorporar logging estructurado inicial.
- Construir shell frontend.

## 9.5. Riesgos
- bootstrap demasiado simple que luego obligue a rehacer,
- frontend vanilla mal organizado desde el inicio,
- mezcla temprana entre infraestructura y dominio.

## 9.6. Definition of Done del sprint
- proyecto corre localmente,
- frontend y backend están conectados a nivel base,
- estructura queda lista para recibir módulos sin refactor mayor.

## 9.7. Prompt de Codex para Sprint 1

```text
Quiero que prepares la base de un proyecto web de despliegue local con estas restricciones obligatorias:

- Backend: FastAPI
- Frontend: vanilla HTML, CSS y JavaScript
- Base de datos desarrollo: MariaDB
- Base de datos producción: Oracle
- Seguridad: JWT con pyjwt y contraseñas con Argon2
- La app debe quedar modular, escalable y lista para crecer por dominios
- No escribas lógica de negocio todavía; solo estructura profesional del proyecto

Necesito que:
1. propongas la estructura de carpetas final,
2. expliques por qué separas api, services, repositories, infrastructure y core,
3. dejes preparado el versionado de endpoints en /api/v1,
4. dejes listo el soporte de templates y static para frontend vanilla,
5. dejes lista la base para configuración por entorno,
6. minimices acoplamiento a MariaDB para facilitar paso a Oracle,
7. implementes un shell UI con sidebar izquierdo colapsable y vistas base de login y panel principal.

Antes de implementar, enumera los archivos que crearás y el propósito de cada uno.
Luego implementa solo el bootstrap estructural y del shell.
No generes funcionalidades incompletas ni mocks engañosos.
```

---

## 10. Sprint 2 — Seguridad y gestión de sesión

## 10.1. Objetivo
Implementar autenticación segura y estable para el MVP.

## 10.2. Alcance
- login,
- access token,
- refresh token,
- rotación de refresh,
- logout,
- guardas de endpoints,
- manejo de sesión en frontend vanilla.

## 10.3. Historias del sprint

### Historia 1
**Como usuario, quiero iniciar sesión para acceder al módulo de formateo.**

#### Criterios de aceptación
- El login valida credenciales.
- El password usa Argon2.
- El sistema devuelve access y refresh token de forma segura.

### Historia 2
**Como usuario, quiero mantener mi sesión sin reloguearme constantemente.**

#### Criterios de aceptación
- El access token expira a los 30 minutos.
- El refresh token permite renovación silenciosa.
- El refresh rota y la sesión anterior no queda reutilizable indefinidamente.

### Historia 3
**Como sistema, quiero proteger endpoints para impedir accesos no autorizados.**

#### Criterios de aceptación
- Los endpoints protegidos exigen JWT válido.
- Los errores de autenticación son consistentes.
- Logout invalida la sesión vigente.

## 10.4. Tareas técnicas sugeridas
- Modelo de usuarios.
- Modelo de sesiones/refresh tokens.
- Servicio de hash y verificación.
- Servicio de emisión y validación JWT.
- Endpoint login, refresh y logout.
- Módulo JS para persistencia y refresco de token.

## 10.5. Riesgos
- seguridad implementada solo “a medias”,
- refresh token mal revocado,
- frontend que no renueva la sesión de forma consistente.

## 10.6. Definition of Done del sprint
- login funcional de punta a punta,
- refresh funcional,
- logout funcional,
- rutas protegidas operativas,
- pruebas mínimas de login y refresh.

## 10.7. Prompt de Codex para Sprint 2

```text
Quiero que implementes el módulo de autenticación para una aplicación FastAPI con frontend vanilla.

Restricciones obligatorias:
- usar pyjwt,
- usar Argon2 para hashing de contraseñas,
- access token con expiración de 30 minutos,
- refresh token con rotación,
- diseño desacoplado para MariaDB en desarrollo y Oracle en producción,
- rutas versionadas en /api/v1,
- validación y manejo de errores centralizados.

Objetivo funcional:
- login,
- refresh de token,
- logout,
- guardas para endpoints protegidos,
- integración con frontend vanilla para persistencia de sesión y renovación silenciosa.

Necesito que:
1. propongas el modelo mínimo de tablas para usuarios y sesiones,
2. implementes la capa domain/service/repository,
3. evites lógica de seguridad duplicada en rutas,
4. prepares respuestas consistentes para frontend,
5. incluyas pruebas mínimas de login y refresh,
6. integres un módulo JS claro para manejo de sesión.

Antes de escribir código, explícame las decisiones de seguridad que tomarás y los archivos que vas a modificar.
```

---

## 11. Sprint 3 — Dominio documental y catálogo de productos

## 11.1. Objetivo
Dejar lista la entrada al flujo principal: productos, carga documental y metadatos de operación.

## 11.2. Alcance
- catálogo de productos,
- reglas de formato por producto,
- endpoint de productos activos,
- carga de `.docx`,
- validación del archivo,
- almacenamiento temporal,
- creación inicial de operación documental.

## 11.3. Historias del sprint

### Historia 1
**Como usuario, quiero seleccionar un producto para que el sistema sepa qué reglas aplicar.**

#### Criterios de aceptación
- Existe endpoint para listar productos activos.
- Existe modelo de producto y de reglas de formato.
- El frontend puede cargar el catálogo.

### Historia 2
**Como usuario, quiero subir una prepóliza `.docx` válida para procesarla.**

#### Criterios de aceptación
- El sistema solo acepta `.docx`.
- El sistema valida tamaño máximo configurable.
- El sistema genera nombre interno seguro.
- El sistema no permite rutas arbitrarias.

### Historia 3
**Como sistema, quiero registrar una operación documental inicial antes de formatear.**

#### Criterios de aceptación
- Se crea un registro en estado inicial.
- Se guarda metadato del archivo original.
- Se asocia usuario, producto y número de póliza.

## 11.4. Tareas técnicas sugeridas
- Crear módulo `products`.
- Definir serialización de reglas de formato.
- Crear módulo `documents` de recepción y validación.
- Diseñar almacenamiento temporal seguro.
- Preparar endpoint para recibir archivo + producto + número de póliza.

## 11.5. Riesgos
- diseño de reglas demasiado rígido,
- validación documental superficial,
- almacenamiento temporal inseguro.

## 11.6. Definition of Done del sprint
- existe catálogo consumible por frontend,
- existe carga documental controlada,
- existe registro inicial de operación,
- el documento queda listo para pasar al motor DOCX.

## 11.7. Prompt de Codex para Sprint 3

```text
Quiero que implementes el dominio documental base del MVP y el catálogo de productos.

Objetivos:
- cada producto debe definir su título,
- cada producto debe definir su encabezado,
- cada producto debe referenciar una configuración de formato base,
- el usuario debe poder subir una prepóliza .docx junto con producto y número de póliza,
- el sistema debe validar y dejar la operación lista para pasar al motor de formateo.

Restricciones:
- aceptar solo archivos .docx,
- validar tamaño máximo configurable,
- sanitizar nombre del archivo,
- generar nombre interno seguro,
- guardar original y salida por separado,
- no permitir rutas arbitrarias definidas por el usuario,
- diseño compatible con MariaDB y Oracle,
- no usar if/else duros dispersos para resolver reglas por producto.

Necesito que:
1. propongas entidades, tablas y relaciones para productos, reglas y operaciones documentales,
2. definas cómo serializar la configuración de formato,
3. implementes services y repositories de products y documents,
4. dejes preparado el endpoint para listar productos activos,
5. implementes el endpoint de carga documental,
6. devuelvas errores claros para el frontend,
7. expliques la estrategia de almacenamiento temporal y limpieza futura.

Antes de implementar, enumera archivos y responsabilidades.
```

---

## 12. Sprint 4 — Motor DOCX MVP

## 12.1. Objetivo
Construir el núcleo de negocio del MVP: aplicar formato sin destruir la estructura del documento.

## 12.2. Alcance
- page setup,
- márgenes,
- tamaño de hoja,
- fuente base,
- párrafo base,
- interlineado,
- reemplazo de encabezado,
- inserción de título,
- exportación del nuevo `.docx`.

## 12.3. Historias del sprint

### Historia 1
**Como usuario, quiero aplicar un formato base a mi prepóliza sin alterar su contenido.**

#### Criterios de aceptación
- El contenido textual se mantiene.
- El motor modifica solo propiedades permitidas.
- El archivo resultante se genera como nuevo documento.

### Historia 2
**Como usuario, quiero que el encabezado cambie según producto y número de póliza.**

#### Criterios de aceptación
- El header se resuelve desde la configuración del producto.
- El motor soporta documentos con secciones.
- Existe una política clara para múltiples headers.

### Historia 3
**Como usuario, quiero que se inserte el título correspondiente al producto.**

#### Criterios de aceptación
- El título se inserta sin romper la estructura.
- La política de inserción queda definida y aplicada consistentemente.

### Historia 4
**Como usuario, quiero conservar tablas e imágenes del documento original.**

#### Criterios de aceptación
- Tablas no se remaquetan.
- Imágenes se preservan.
- El documento final mantiene estructura funcional equivalente.

## 12.4. Tareas técnicas sugeridas
- Diseñar el servicio de inspección DOCX.
- Diseñar el servicio de aplicación de formato.
- Diseñar el servicio de header y título.
- Diseñar política de exportación segura.
- Crear pruebas con fixtures reales.

## 12.5. Riesgos
- daño de estructura interna del DOCX,
- comportamiento inconsistente por secciones,
- inserción de título en punto incorrecto,
- librería elegida insuficiente para casos borde.

## 12.6. Definition of Done del sprint
- el motor genera un `.docx` nuevo,
- el header se reemplaza,
- el título se inserta,
- tablas e imágenes sobreviven en casos de prueba,
- se registran hallazgos o limitaciones técnicas reales.

## 12.7. Prompt de Codex para Sprint 4

```text
Quiero que implementes el motor de formateo DOCX del MVP con una premisa central:
NO debes reconstruir el documento completo ni perder tablas o imágenes.

Objetivo funcional:
- aplicar márgenes,
- tamaño de hoja,
- interlineado,
- tipo y tamaño de letra base,
- formato de párrafo,
- reemplazar encabezado según producto y número de póliza,
- insertar título según producto,
- exportar el resultado en un nuevo .docx.

Restricciones de diseño:
- el contenido y estructura deben mantenerse,
- tablas e imágenes deben preservarse,
- el motor debe intervenir lo mínimo necesario,
- la lógica debe quedar encapsulada en services claros,
- no quiero lógica mezclada en los endpoints,
- el resultado debe asociarse a la operación documental ya registrada.

Necesito que antes de implementar:
1. me expliques la estrategia técnica exacta para preservar estructura,
2. identifiques riesgos con múltiples secciones y headers,
3. propongas una política clara para inserción del título,
4. enumeres archivos y responsabilidades,
5. indiques qué librería o enfoque propones para manipular el .docx y sus límites reales.

Luego implementa el MVP del motor y agrega pruebas con documentos de ejemplo si el repositorio ya tiene fixtures.
```

---

## 13. Sprint 5 — Trazabilidad e integración del flujo principal

## 13.1. Objetivo
Cerrar el MVP funcional completo con historial y trazabilidad por usuario.

## 13.2. Alcance
- tabla de documentos procesados,
- tabla de eventos de auditoría,
- actualización de estados,
- historial del usuario,
- integración completa del flujo: login → upload → formato → exportación → descarga.

## 13.3. Historias del sprint

### Historia 1
**Como usuario, quiero descargar el documento formateado al finalizar el proceso.**

#### Criterios de aceptación
- El backend devuelve metadatos y punto de descarga.
- El original no se sobrescribe.
- El archivo generado está asociado a la operación.

### Historia 2
**Como usuario, quiero ver mi historial reciente de operaciones.**

#### Criterios de aceptación
- Existe endpoint de historial del usuario autenticado.
- Se muestra fecha, producto, archivo y estado.
- Si corresponde, se puede descargar el resultado.

### Historia 3
**Como auditor funcional, quiero trazabilidad de uso por usuario.**

#### Criterios de aceptación
- Se registra fecha inicio y fin.
- Se registra estado y error si aplica.
- Se registra archivo original y generado.
- Se diferencia trazabilidad de negocio y logging técnico.

## 13.4. Tareas técnicas sugeridas
- Diseñar tablas de auditoría y documentos procesados.
- Integrar transiciones de estado.
- Exponer historial al frontend.
- Integrar el flujo principal end-to-end.
- Probar escenarios de éxito y error.

## 13.5. Riesgos
- trazabilidad incompleta,
- flujo integrado pero con rollback pobre,
- respuestas heterogéneas entre endpoints.

## 13.6. Definition of Done del sprint
- el flujo principal está operativo,
- existe historial por usuario,
- existe auditoría básica,
- hay consistencia entre estados del proceso y archivos generados.

## 13.7. Prompt de Codex para Sprint 5

```text
Quiero que implementes la trazabilidad del MVP e integres el flujo principal completo sin romper la modularidad.

Flujo objetivo:
1. usuario autenticado,
2. selecciona producto,
3. ingresa número de póliza,
4. sube archivo .docx,
5. se aplica el formato,
6. se genera el nuevo archivo,
7. se registra trazabilidad,
8. se ofrece descarga al usuario,
9. el usuario puede ver su historial.

Por cada operación necesito registrar:
- usuario,
- producto,
- número de póliza,
- nombre del archivo original,
- nombre del archivo generado,
- fecha/hora de inicio,
- fecha/hora de fin,
- estado,
- mensaje de error si aplica.

Restricciones:
- conservar la arquitectura por módulos,
- no mover lógica a las rutas,
- respuestas consistentes para frontend,
- manejo de errores centralizado,
- no sobrescribir archivos originales,
- separar trazabilidad de negocio de logging técnico.

Necesito que primero me muestres:
1. el mapa exacto del flujo entre rutas, services y repositories,
2. el modelo de tablas propuesto,
3. los archivos a tocar,
4. los puntos de rollback si algo falla.

Luego implementa la integración completa e incluye pruebas mínimas end-to-end si el repositorio ya tiene base de testing.
```

---

## 14. Sprint 6 — Hardening y preparación para despliegue local

## 14.1. Objetivo
Dejar el MVP estable para uso interno real.

## 14.2. Alcance
- mejora del manejo de errores,
- limpieza de temporales,
- logging estructurado,
- robustez de validación documental,
- preparación para Oracle,
- revisión crítica del frontend vanilla,
- cierre de deuda técnica prioritaria.

## 14.3. Historias del sprint

### Historia 1
**Como equipo, quiero que el sistema falle de forma controlada y auditable.**

#### Criterios de aceptación
- Los errores críticos quedan registrados.
- El usuario recibe mensajes útiles y no trazas internas.
- El estado de la operación queda consistente.

### Historia 2
**Como administrador técnico, quiero que los temporales no se acumulen indefinidamente.**

#### Criterios de aceptación
- Existe política clara de limpieza.
- Originales y generados tienen reglas de retención definidas.
- No hay rutas peligrosas ni nombres inseguros.

### Historia 3
**Como equipo, quiero preparar el paso a Oracle sin rediseño mayor.**

#### Criterios de aceptación
- La capa de persistencia sigue desacoplada.
- Las diferencias entre MariaDB y Oracle están documentadas.
- Existen puntos identificados para migraciones y tuning posterior.

## 14.4. Tareas técnicas sugeridas
- revisar excepciones y códigos de respuesta,
- revisar validaciones de entrada,
- agregar correlación de logs por operación,
- revisar cleanup de archivos,
- revisar puntos específicos de compatibilidad Oracle,
- hacer QA técnico del motor documental.

## 14.5. Riesgos
- asumir que “funciona en demo” equivale a “está listo”,
- deuda de observabilidad,
- problemas de compatibilidad en el paso a producción.

## 14.6. Definition of Done del sprint
- hardening aplicado en puntos críticos,
- cleanup definido e implementado,
- logging mejorado,
- hallazgos para Oracle documentados,
- MVP listo para piloto interno.

## 14.7. Prompt de Codex para Sprint 6

```text
Quiero que revises el MVP completo y lo endurezcas para despliegue local corporativo.

Necesito que revises y mejores:
- manejo de errores,
- validaciones de archivos,
- limpieza de temporales,
- seguridad de tokens,
- logging estructurado,
- configuración por entorno,
- preparación para Oracle en producción,
- mantenibilidad del frontend vanilla.

Antes de cambiar nada, haz una revisión crítica del proyecto con formato:
1. hallazgo,
2. riesgo,
3. impacto,
4. recomendación,
5. archivos afectados.

Luego aplica solo mejoras concretas y justificadas.
No hagas refactors cosméticos innecesarios.
Prioriza estabilidad, trazabilidad y mantenibilidad.
```

---

## 15. Sprint transversal de QA técnico del motor documental
Este bloque puede ejecutarse al final del Sprint 4 o dentro del Sprint 6, según el avance real.

## 15.1. Objetivo
Auditar específicamente el motor DOCX.

## 15.2. Checklist de validación
- preservación de texto,
- preservación de tablas,
- preservación de imágenes,
- headers por sección,
- secciones múltiples,
- exportación de archivo válido,
- no sobrescritura del original,
- comportamiento frente a documentos parcialmente atípicos.

## 15.3. Prompt de Codex para auditoría técnica

```text
Quiero que audites específicamente el motor documental del proyecto.

Objetivo:
verificar que la estrategia elegida realmente preserve:
- estructura del documento,
- tablas,
- imágenes,
- encabezados,
- compatibilidad con múltiples secciones.

Necesito una revisión técnica con este formato:
1. supuestos del motor,
2. puntos frágiles,
3. casos borde,
4. pruebas faltantes,
5. refactor recomendado.

No implementes cambios todavía. Primero entrégame el diagnóstico técnico completo.
```

---

## 16. Backlog consolidado por prioridad

## 16.1. Prioridad crítica
- estructura modular,
- login y refresh,
- carga `.docx`,
- validación documental,
- catálogo de productos,
- motor DOCX,
- exportación segura,
- trazabilidad.

## 16.2. Prioridad importante
- historial del usuario,
- limpieza automática,
- observabilidad mínima,
- preparación Oracle.

## 16.3. Prioridad posterior al MVP
- administración UI de productos y reglas,
- preview del documento,
- versionado de reglas,
- comparador antes/después,
- flujo de aprobación.

---

## 17. Dependencias entre sprints

| Sprint | Depende de | No debería iniciar sin |
|---|---|---|
| Sprint 1 | Sprint 0 | Insumos mínimos y alcance cerrado |
| Sprint 2 | Sprint 1 | Estructura base operativa |
| Sprint 3 | Sprint 1 y 2 | Seguridad y base de proyecto listas |
| Sprint 4 | Sprint 3 | Productos, upload y operación documental listos |
| Sprint 5 | Sprint 4 | Motor DOCX funcionando en casos base |
| Sprint 6 | Sprint 5 | Flujo principal completo |

---

## 18. Riesgos ejecutivos del plan

### Riesgo 1
**El motor DOCX resulta más frágil de lo esperado.**

#### Mitigación
- adelantar pruebas con documentos reales desde Sprint 3,
- no esperar al final para validar headers, tablas e imágenes,
- documentar límites reales del motor.

### Riesgo 2
**Se invierte demasiado tiempo en el frontend antes de validar el núcleo documental.**

#### Mitigación
- mantener UI sobria,
- concentrar esfuerzo en flujo y motor,
- postergar embellishments visuales.

### Riesgo 3
**Se mezcla lógica de negocio con rutas o scripts frontend.**

#### Mitigación
- revisar cada PR o entrega de Codex por capas,
- exigir services claros y repositorios separados.

### Riesgo 4
**MariaDB y Oracle generan divergencias al final.**

#### Mitigación
- evitar SQL vendor-specific en MVP,
- concentrar particularidades en infraestructura y migraciones.

---

## 19. Estrategia de validación por sprint

## 19.1. Validación funcional
Al cerrar cada sprint se debe revisar:
- qué puede hacer ya un usuario real,
- qué sigue siendo mock o placeholder,
- qué riesgos persisten abiertos.

## 19.2. Validación técnica
Al cerrar cada sprint se debe revisar:
- si la modularidad se conserva,
- si los tests cubren lo crítico del sprint,
- si la deuda técnica quedó documentada.

## 19.3. Validación documental
Desde Sprint 3 en adelante se debe mantener una batería acumulativa con documentos reales para detectar regresiones.

---

## 20. Recomendación operativa para trabajar con Codex

### 20.1. Forma correcta de pedir trabajo
Cada solicitud a Codex debe:
- centrarse en un sprint o submódulo,
- fijar restricciones explícitas,
- pedir análisis antes de codificar,
- exigir lista de archivos a tocar,
- exigir criterio de aceptación.

### 20.2. Forma incorrecta de pedir trabajo
Evitar prompts como:
- “hazme todo el sistema”,
- “crea un sistema completo con buenas prácticas”,
- “implementa el backend y frontend del MVP entero”.

Ese tipo de instrucción suele producir código disperso, acoplado y difícil de mantener.

### 20.3. Patrón recomendado de interacción
Usar este patrón repetidamente:

1. análisis de diseño,
2. lista de archivos,
3. implementación acotada,
4. pruebas,
5. revisión crítica,
6. siguiente incremento.

---

## 21. Resultado esperado al cierre del roadmap
Si el plan se ejecuta bien, al cierre del Sprint 6 el equipo debería tener:

- una aplicación local autenticada,
- carga controlada de prepólizas `.docx`,
- motor MVP de formateo con preservación razonable,
- header y título por producto,
- exportación segura de Word final,
- trazabilidad básica por usuario,
- historial de operaciones,
- base técnica lista para endurecer y evolucionar.

---

## 22. Recomendación final
La mejor decisión de gestión para este proyecto es tratar el motor DOCX como un **subproducto crítico** dentro del MVP.

No conviene medir el avance solo por cantidad de pantallas listas. El avance real debe medirse por estas preguntas:

1. ¿el documento sale correcto?,
2. ¿se conservan tablas e imágenes?,
3. ¿el header y el título se aplican bien?,
4. ¿la operación queda trazable?,
5. ¿el flujo puede sostenerse sin refactor mayor?

Si esas cinco respuestas son positivas, el MVP estará bien encaminado.
