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