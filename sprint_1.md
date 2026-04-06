
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