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