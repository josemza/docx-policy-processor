# Blueprint MVP — Formateador Web de Prepólizas Word

## 1. Objetivo del producto
Desarrollar un aplicativo web de despliegue local que permita:

1. autenticar usuarios,
2. cargar una prepóliza en formato Word (`.docx`),
3. aplicar un formato predefinido sin alterar la estructura funcional del documento,
4. reemplazar el encabezado según producto y número de póliza,
5. insertar el título según producto,
6. exportar la póliza final nuevamente en formato Word,
7. registrar trazabilidad básica por usuario.

El foco del MVP debe ser **fiabilidad sobre sofisticación**: preservar contenido, tablas e imágenes con el menor nivel posible de intervención estructural sobre el documento.

---

## 2. Alcance del MVP

### Incluye
- Login con JWT.
- Renovación de token cada 30 minutos.
- Frontend vanilla (`HTML`, `CSS`, `JavaScript`) con panel lateral izquierdo colapsable.
- Carga de archivo Word (`.docx`).
- Parametrización mínima del formateo por producto.
- Aplicación de formato base:
  - márgenes,
  - tamaño de hoja,
  - interlineado,
  - tipo y tamaño de letra,
  - formato de texto y párrafo.
- Reemplazo de encabezado según producto y número de póliza.
- Inserción de título según producto.
- Exportación de Word formateado.
- Registro de trazabilidad por usuario.

### No incluye en el MVP
- Edición visual avanzada del documento en navegador.
- Versionado complejo del documento.
- Flujo colaborativo multiusuario sobre el mismo archivo.
- Firma digital.
- Plantillas WYSIWYG completas.
- Soporte para `.doc` legado.

---

## 3. Principios de diseño del producto

### 3.1. Preservación documental
La regla principal es:

> **No reconstruir el documento si no es estrictamente necesario.**

Para cumplir con el requerimiento de mantener contenido, estructura, imágenes y tablas, la estrategia correcta es **modificar el DOCX de forma mínima y controlada**. El motor debe actuar sobre estilos, secciones, encabezados y bloques específicos, evitando reescribir el documento completo.

### 3.2. Separación clara de responsabilidades
El sistema debe dividirse en capas:
- presentación,
- API,
- autenticación,
- procesamiento documental,
- persistencia,
- trazabilidad/auditoría.

### 3.3. Parametrización por producto
Los formatos no deben quedar “quemados” en lógica rígida. Deben vivir en una capa de configuración para poder incorporar más productos sin rediseñar el motor.

### 3.4. Escalabilidad local-realista
Aunque el despliegue sea local, la arquitectura debe permitir:
- crecer en número de productos,
- crecer en reglas de formateo,
- crecer en usuarios,
- migrar de MariaDB a Oracle sin reescribir el dominio.

---

## 4. Arquitectura propuesta

## 4.1. Vista general

```text
[Frontend Vanilla]
    |
    v
[FastAPI API Layer]
    |
    +--> [Auth Module]
    +--> [Document Workflow Module]
    +--> [Product Rules Module]
    +--> [Audit / Traceability Module]
    +--> [File Storage Module]
    |
    v
[Service Layer / Use Cases]
    |
    +--> [Word Formatting Engine]
    +--> [Header/Title Resolver]
    +--> [Validation Engine]
    +--> [Export Service]
    |
    v
[Persistence Layer]
    +--> MariaDB (desarrollo)
    +--> Oracle (producción)
```

---

## 4.2. Arquitectura modular del backend

### A. `auth`
Responsable de:
- login,
- emisión de access token,
- refresh token,
- revocación/rotación,
- validación de sesión,
- hash de contraseñas con Argon2.

### B. `users`
Responsable de:
- perfil mínimo del usuario,
- estado del usuario,
- roles básicos del MVP.

### C. `documents`
Responsable de:
- recepción del archivo,
- validaciones del archivo,
- asociación del archivo al usuario y a la operación,
- metadatos del documento procesado.

### D. `products`
Responsable de:
- catálogo de productos,
- definición de encabezado por producto,
- definición de título por producto,
- referencia a reglas de formateo aplicables.

### E. `formatting`
Responsable de:
- aplicar reglas base de formato,
- modificar encabezado,
- insertar título,
- preservar contenido y estructura,
- generar archivo de salida.

### F. `audit`
Responsable de:
- registrar eventos de uso,
- registrar quién procesó qué archivo,
- registrar fecha/hora, producto y resultado,
- almacenar trazabilidad técnica básica.

### G. `storage`
Responsable de:
- almacenamiento temporal seguro,
- convención de nombres,
- limpieza controlada,
- ubicación de archivos originales y generados.

### H. `core`
Responsable de:
- configuración,
- seguridad,
- utilidades compartidas,
- manejo de errores,
- logging estructurado.

---

## 5. Estructura recomendada del proyecto

```text
app/
  api/
    v1/
      routes/
        auth.py
        documents.py
        products.py
        audit.py
  core/
    config.py
    security.py
    logging.py
    exceptions.py
  domain/
    entities/
    schemas/
    enums/
  services/
    auth/
    documents/
    formatting/
    products/
    audit/
  repositories/
    users/
    documents/
    products/
    audit/
  infrastructure/
    db/
      base.py
      session.py
      models/
    storage/
    word/
  templates/
  static/
    css/
    js/
    img/
  main.py

docs/
  arquitectura/
  prompts_codex/

migrations/

tests/
  unit/
  integration/
  e2e/
```

---

## 6. Estrategia técnica para el procesamiento del Word

## 6.1. Restricción funcional clave
Para el MVP se debe soportar únicamente **`.docx`**.

Motivo:
- `.doc` obliga a conversiones o librerías menos estables.
- `.docx` permite trabajar sobre Open XML, que es mucho más controlable.

## 6.2. Estrategia correcta de intervención
La estrategia debe ser por niveles:

### Nivel 1 — Validación previa
- validar extensión,
- validar tamaño máximo,
- validar que el archivo no esté corrupto,
- validar que sea un paquete DOCX legible,
- generar identificador único de procesamiento.

### Nivel 2 — Inspección estructural básica
Antes de aplicar formato, detectar:
- número de secciones,
- existencia de encabezados,
- tablas,
- imágenes embebidas,
- estilos existentes,
- bloques iniciales aptos para insertar título.

### Nivel 3 — Aplicación mínima de reglas
Aplicar únicamente cambios controlados sobre:
- propiedades de página,
- estilos base,
- espaciado e interlineado,
- párrafos objetivo,
- header,
- título.

### Nivel 4 — Exportación segura
- guardar como nuevo archivo,
- nunca sobrescribir el original,
- registrar checksum o huella básica del archivo generado,
- asociar salida con usuario y operación.

---

## 6.3. Decisión de diseño crítica
Para preservar tablas e imágenes, el motor debe seguir esta política:

### Política de preservación
- **No remaquetar tablas** salvo que exista un requerimiento explícito.
- **No tocar imágenes** salvo reposicionamiento obligatorio.
- **No convertir el documento a HTML ni reconstruirlo desde cero.**
- **No regenerar el contenido textual completo.**

### Qué sí puede modificarse de forma segura
- márgenes de secciones,
- tamaño de hoja,
- estilos base,
- espaciado entre párrafos,
- interlineado,
- fuente base,
- encabezado,
- título,
- alineación/estilo de bloques definidos.

---

## 6.4. Modelo de reglas de formateo
El motor debe recibir una estructura conceptual como esta:

- `producto`
- `numero_poliza`
- `titulo_documento`
- `header_template`
- `page_setup`
- `font_defaults`
- `paragraph_defaults`
- `title_rules`

La idea no es codificar reglas dispersas sino centralizarlas en un **catálogo de reglas por producto**.

---

## 7. Diseño funcional del flujo principal

## 7.1. Flujo de usuario
1. El usuario inicia sesión.
2. El usuario accede al módulo “Formatear póliza”.
3. El usuario selecciona producto.
4. El usuario ingresa número de póliza.
5. El usuario carga la prepóliza `.docx`.
6. El sistema valida el archivo.
7. El sistema aplica reglas base + reglas del producto.
8. El sistema genera el archivo de salida.
9. El sistema registra la trazabilidad.
10. El usuario descarga el Word final.

---

## 7.2. Flujo interno del backend
1. Validar JWT.
2. Validar permisos mínimos del usuario.
3. Crear registro de operación en estado `RECIBIDO`.
4. Guardar archivo original en almacenamiento temporal.
5. Ejecutar inspección estructural.
6. Resolver configuración del producto.
7. Aplicar motor de formateo.
8. Guardar archivo generado.
9. Actualizar estado a `COMPLETADO` o `ERROR`.
10. Registrar trazabilidad detallada.
11. Responder con metadatos y enlace de descarga.

---

## 8. Propuesta de frontend MVP

## 8.1. Pantallas mínimas

### A. Login
- usuario,
- contraseña,
- feedback de error claro,
- expiración/control de sesión.

### B. Shell principal
- sidebar izquierdo colapsable,
- header superior simple,
- área de trabajo central.

### C. Módulo de formateo
- selector de producto,
- input de número de póliza,
- carga de archivo,
- resumen de reglas aplicadas,
- botón “Procesar”,
- botón “Descargar resultado”,
- historial simple de últimas operaciones del usuario.

### D. Módulo de trazabilidad
- lista de operaciones,
- fecha,
- usuario,
- producto,
- archivo,
- estado,
- descarga del resultado si aplica.

---

## 8.2. Principios UI/UX
- interfaz sobria, corporativa y rápida,
- sin dependencia de frameworks frontend,
- accesibilidad visual básica,
- componentes reutilizables en JS puro,
- mensajes de error accionables,
- estado visible del procesamiento.

---

## 9. Seguridad

## 9.1. Autenticación y sesión
Recomendación para el MVP:

### Access token
- JWT corto,
- vigencia de 30 minutos,
- enviado en header `Authorization: Bearer`.

### Refresh token
- persistido de forma segura,
- rotación periódica,
- invalidez al cerrar sesión,
- asociado a usuario y dispositivo/sesión.

### Renovación
La frase “renovación de token cada 30 min” conviene implementarla así:
- access token con TTL de 30 min,
- refresh token con duración mayor,
- renovación silenciosa controlada por frontend antes de expirar.

Esto evita pedir login frecuente y mantiene mejor seguridad.

---

## 9.2. Contraseñas
- hash con **Argon2**,
- nunca almacenar contraseñas en claro,
- política mínima de longitud y complejidad,
- posibilidad de deshabilitar usuarios.

---

## 9.3. Seguridad de archivos
- aceptar solo `.docx`,
- limitar tamaño,
- sanitizar nombre del archivo,
- usar nombres internos generados por el sistema,
- separar archivo original y archivo generado,
- evitar rutas arbitrarias del usuario,
- limpieza programada de temporales.

---

## 9.4. Seguridad API
- versionado `/api/v1`,
- validación estricta de payloads,
- manejo centralizado de errores,
- rate limiting opcional si el entorno lo requiere,
- logs sin exponer tokens ni datos sensibles.

---

## 10. Trazabilidad y auditoría

## 10.1. Qué registrar en el MVP
Por cada operación:
- id de operación,
- usuario,
- fecha/hora inicio,
- fecha/hora fin,
- producto,
- número de póliza,
- nombre original del archivo,
- nombre interno del archivo,
- estado,
- mensaje de error si aplica,
- hash o huella del archivo resultado,
- IP/equipo si el entorno local lo permite.

## 10.2. Beneficio
Esto permitirá:
- saber quién procesó qué,
- depurar errores,
- medir uso,
- construir historial básico,
- cumplir trazabilidad operativa.

---

## 11. Modelo de datos conceptual

## 11.1. Tablas mínimas

### `usuarios`
- id_usuario
- username
- password_hash
- nombre
- estado
- rol
- fecha_creacion
- fecha_ultimo_login

### `sesiones`
- id_sesion
- id_usuario
- refresh_token_hash
- fecha_emision
- fecha_expiracion
- estado
- metadata_dispositivo

### `productos`
- id_producto
- codigo_producto
- nombre_producto
- titulo_template
- header_template
- activo

### `reglas_formato`
- id_regla
- id_producto
- version_regla
- configuracion_serializada
- activo
- fecha_vigencia

### `documentos_procesados`
- id_documento_procesado
- id_usuario
- id_producto
- numero_poliza
- nombre_archivo_original
- nombre_archivo_salida
- ruta_logica_original
- ruta_logica_salida
- estado
- fecha_inicio
- fecha_fin
- hash_salida
- observacion_error

### `eventos_auditoria`
- id_evento
- id_usuario
- tipo_evento
- entidad
- id_entidad
- fecha_evento
- detalle

---

## 11.2. Portabilidad MariaDB / Oracle
Para evitar fricción entre desarrollo y producción:
- mantener el dominio desacoplado del motor,
- usar repositorios y modelos compatibles,
- minimizar SQL específico del vendor en el MVP,
- reservar particularidades Oracle para migraciones y tuning.

---

## 12. Estrategia escalable

## 12.1. Escalabilidad funcional
La arquitectura debe permitir incorporar luego:
- nuevos productos,
- más plantillas,
- reglas de formateo por sección,
- validaciones más complejas,
- vista previa del documento,
- plantillas administrables desde UI.

## 12.2. Escalabilidad técnica
Aunque el despliegue sea local, conviene dejar preparada la aplicación para:
- ejecución por servicio interno,
- almacenamiento desacoplado,
- cola futura para procesamiento si crece el volumen,
- logs estructurados,
- migraciones versionadas.

## 12.3. Escalabilidad de mantenimiento
La clave no es solo soportar más usuarios, sino poder cambiar reglas sin tocar demasiadas capas. Por eso el núcleo debe ser:

> **motor de formateo + configuración por producto + trazabilidad fuerte**

---

## 13. Riesgos técnicos y mitigación

## Riesgo 1: Pérdida de formato al tocar el DOCX
**Mitigación:** edición mínima; no reconstrucción completa; pruebas con documentos reales.

## Riesgo 2: Encabezados distintos por sección
**Mitigación:** diseñar el motor para detectar múltiples secciones y aplicar política explícita por sección.

## Riesgo 3: Inserción de título rompe maquetación
**Mitigación:** ubicar un punto de inserción claro y probar con documentos base representativos.

## Riesgo 4: Diferencias Oracle / MariaDB
**Mitigación:** repositorios y migraciones separados por entorno; dominio desacoplado.

## Riesgo 5: Tokens mal gestionados
**Mitigación:** refresh token rotativo, revocación y expiración controlada.

## Riesgo 6: Archivos temporales acumulados
**Mitigación:** estrategia de limpieza automática y nombres internos controlados.

---

## 14. Estrategia de pruebas para el MVP

## 14.1. Pruebas unitarias
- validación de reglas,
- resolución de producto,
- autenticación,
- expiración y renovación de tokens,
- naming seguro de archivos.

## 14.2. Pruebas de integración
- login + refresh,
- carga de `.docx`,
- procesamiento exitoso,
- descarga,
- auditoría registrada.

## 14.3. Pruebas funcionales con documentos reales
Preparar un set mínimo de documentos con:
- texto puro,
- tablas,
- imágenes,
- múltiples secciones,
- encabezados existentes,
- estilos mezclados.

Esta batería es crítica. En este producto la validación más importante no es el endpoint, sino el resultado Word final.

---

## 15. División de tareas recomendada

## Fase 0 — Descubrimiento y definición
- levantar catálogo inicial de productos,
- definir formato base,
- recopilar 10 a 20 prepólizas reales de prueba,
- definir reglas por producto,
- acordar criterio exacto de inserción de título y header.

## Fase 1 — Base técnica del proyecto
- bootstrap de FastAPI,
- estructura modular,
- configuración por entorno,
- conexión MariaDB,
- base de autenticación,
- shell frontend con sidebar colapsable.

## Fase 2 — Seguridad y sesión
- login,
- JWT access token,
- refresh token,
- hash Argon2,
- middleware/guardas.

## Fase 3 — Dominio documental
- módulo de carga,
- validaciones,
- almacenamiento temporal,
- metadatos del documento,
- catálogo de productos.

## Fase 4 — Motor de formateo MVP
- page setup,
- estilos base,
- header,
- título,
- exportación,
- preservación estructural.

## Fase 5 — Trazabilidad
- tabla de auditoría,
- tabla de documentos procesados,
- historial de operaciones.

## Fase 6 — Endurecimiento
- pruebas con documentos reales,
- manejo de errores,
- limpieza de temporales,
- observabilidad mínima,
- preparación para Oracle.

---

## 16. Backlog inicial priorizado

### Prioridad alta
- autenticación,
- refresh token,
- carga `.docx`,
- procesamiento base,
- encabezado dinámico,
- título por producto,
- exportación,
- trazabilidad.

### Prioridad media
- historial por usuario,
- configuración de productos administrable,
- mejoras visuales del shell.

### Prioridad futura
- preview,
- administración de plantillas desde UI,
- comparador antes/después,
- versionado de reglas,
- workflow de aprobación.

---

## 17. Criterios de aceptación del MVP

1. Un usuario autenticado puede iniciar sesión correctamente.
2. La sesión puede renovarse sin relogin dentro de la ventana definida.
3. El usuario puede cargar un `.docx` válido.
4. El sistema rechaza archivos inválidos.
5. El sistema aplica formato base sin alterar el contenido textual.
6. El sistema mantiene tablas e imágenes.
7. El sistema reemplaza el encabezado según producto y número de póliza.
8. El sistema inserta el título correcto según producto.
9. El sistema exporta el resultado en `.docx`.
10. El sistema registra la operación con trazabilidad básica.

---

## 18. Estrategia de trabajo con Codex en VS Code

La mejor manera de trabajar con Codex aquí no es pedir “haz todo el sistema”, sino dividirlo en entregables cerrados, con restricciones explícitas y criterios de aceptación claros.

### Reglas de interacción con el agente
- pedir siempre cambios modulares,
- exigir que no rompa la estructura existente,
- pedir lista de archivos a crear/modificar antes de implementar,
- pedir decisiones justificadas cuando toque autenticación, persistencia o procesamiento DOCX,
- pedir pruebas junto con cada módulo crítico.

---

## 19. Prompts precisos para Codex

## Prompt 1 — Bootstrap arquitectónico

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
6. minimices acoplamiento a MariaDB para facilitar paso a Oracle.

Antes de implementar, enumera los archivos que crearás y el propósito de cada uno.
Luego implementa solo el bootstrap estructural.
No generes funcionalidades incompletas ni mocks engañosos.
```

---

## Prompt 2 — Autenticación y sesión

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
- guardas para endpoints protegidos.

Necesito que:
1. propongas el modelo mínimo de tablas para usuarios y sesiones,
2. implementes la capa domain/service/repository,
3. evites lógica de seguridad duplicada en rutas,
4. prepares respuestas consistentes para frontend,
5. incluyas pruebas mínimas de login y refresh.

Antes de escribir código, explícame las decisiones de seguridad que tomarás y los archivos que vas a modificar.
```

---

## Prompt 3 — Shell frontend vanilla

```text
Quiero que construyas el shell frontend de una aplicación corporativa usando solo HTML, CSS y JavaScript vanilla.

Requerimientos:
- layout con sidebar izquierdo colapsable,
- header superior simple,
- área principal de contenido,
- vista de login,
- vista principal para carga y procesamiento de Word,
- estilo sobrio y profesional,
- sin frameworks frontend.

Necesito que:
1. estructures el frontend con componentes reutilizables aunque sea vanilla,
2. mantengas separación clara entre HTML, CSS y JS,
3. diseñes una experiencia limpia para carga de archivo y descarga de resultado,
4. dejes preparado un módulo JS para manejo de tokens y refresh silencioso,
5. no hardcodees textos repetidos si pueden centralizarse.

Antes de implementar, enumera archivos, responsabilidades y flujo de interacción entre pantallas.
```

---

## Prompt 4 — Modelo de productos y reglas de formato

```text
Quiero que diseñes el dominio de productos y reglas de formateo para una aplicación que procesa prepólizas Word.

Objetivo:
- cada producto debe poder definir su título,
- cada producto debe poder definir su encabezado,
- cada producto debe poder referenciar una configuración de formato base.

Restricciones:
- el diseño debe soportar crecimiento futuro,
- no quiero reglas duras dispersas en if/else por todo el código,
- el motor debe poder resolver configuración por producto de forma limpia,
- la persistencia debe ser compatible con MariaDB y Oracle.

Necesito que:
1. propongas entidades, tablas y relaciones,
2. definas cómo serializar la configuración de formato,
3. diseñes services y repositories del módulo,
4. dejes preparado el endpoint para listar productos activos,
5. incluyas validaciones para configuraciones inválidas.

Primero explícame el modelo conceptual. Luego implementa.
```

---

## Prompt 5 — Módulo de carga y validación documental

```text
Quiero que implementes el módulo de carga de documentos Word para el MVP.

Reglas obligatorias:
- aceptar solo archivos .docx,
- validar tamaño máximo configurable,
- sanitizar nombre del archivo,
- generar nombre interno seguro,
- guardar original y salida por separado,
- registrar metadatos de procesamiento,
- no permitir rutas arbitrarias definidas por el usuario.

Necesito que el módulo:
1. reciba archivo + producto + número de póliza,
2. valide el archivo,
3. cree un registro de operación en estado inicial,
4. deje el documento listo para pasar al motor de formateo,
5. devuelva errores claros para el frontend.

Antes de implementar, explícame la estrategia de almacenamiento temporal y limpieza futura.
```

---

## Prompt 6 — Motor de formateo DOCX MVP

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
- no quiero lógica mezclada en los endpoints.

Necesito que antes de implementar:
1. me expliques la estrategia técnica exacta para preservar estructura,
2. identifiques riesgos con múltiples secciones y headers,
3. propongas una política clara para inserción del título,
4. enumeres archivos y responsabilidades.

Luego implementa el MVP del motor y agrega pruebas con documentos de ejemplo si el repositorio ya tiene fixtures.
```

---

## Prompt 7 — Trazabilidad y auditoría

```text
Quiero que implementes la trazabilidad del MVP.

Por cada operación de formateo necesito registrar:
- usuario,
- producto,
- número de póliza,
- nombre del archivo original,
- nombre del archivo generado,
- fecha/hora de inicio,
- fecha/hora de fin,
- estado,
- mensaje de error si aplica.

Requisitos:
- diseño limpio y auditable,
- compatibilidad MariaDB / Oracle,
- logs técnicos y trazabilidad de negocio separados,
- endpoint para listar historial del usuario autenticado.

Antes de implementar, propón el modelo de tablas y la diferencia entre auditoría de negocio y logging técnico.
```

---

## Prompt 8 — Integración end-to-end del flujo principal

```text
Quiero que integres el flujo principal completo del MVP sin romper la modularidad.

Flujo objetivo:
1. usuario autenticado,
2. selecciona producto,
3. ingresa número de póliza,
4. sube archivo .docx,
5. se aplica el formato,
6. se genera el nuevo archivo,
7. se registra trazabilidad,
8. se ofrece descarga al usuario.

Restricciones:
- conservar la arquitectura por módulos,
- no mover lógica a las rutas,
- respuestas consistentes para frontend,
- manejo de errores centralizado,
- no sobrescribir archivos originales.

Necesito que primero me muestres:
1. el mapa exacto del flujo entre rutas, services y repositories,
2. los archivos a tocar,
3. los puntos de rollback si algo falla.

Luego implementa la integración completa.
```

---

## Prompt 9 — Hardening para paso a producción local

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
```

---

## Prompt 10 — QA técnico del motor documental

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

## 20. Recomendación operativa final

Para este proyecto, la mayor fuente de complejidad no es FastAPI ni la autenticación. Es el **motor de manipulación DOCX con preservación real del documento**. Por eso el orden de ejecución ideal es:

1. bootstrap técnico,
2. autenticación,
3. shell frontend,
4. catálogo de productos,
5. carga documental,
6. motor DOCX,
7. trazabilidad,
8. integración,
9. hardening.

Si se intenta construir primero la parte visual y dejar para después la manipulación del Word, el proyecto puede parecer avanzado pero fallar justo en el corazón del negocio.

---

## 21. Siguiente paso recomendado

El siguiente paso más rentable es preparar un **paquete de insumos funcionales** antes de pedir implementación a Codex:
- 3 a 5 productos reales,
- ejemplos reales de encabezados,
- ejemplos de títulos,
- 10 a 20 prepólizas de muestra,
- definición exacta del formato base.

Con eso, Codex podrá trabajar con restricciones reales y el MVP será mucho más estable desde la primera iteración.
