class AppError(Exception):
    """Base application exception."""

    def __init__(
        self,
        *,
        message: str,
        code: str,
        status_code: int = 400,
        details: object | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ConfigurationError(AppError):
    def __init__(self, message: str = "Configuracion invalida.") -> None:
        super().__init__(
            message=message,
            code="configuration_error",
            status_code=500,
        )


class AuthenticationError(AppError):
    def __init__(
        self,
        message: str = "Credenciales invalidas.",
        *,
        code: str = "authentication_error",
        status_code: int = 401,
        details: object | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


class AuthorizationError(AppError):
    def __init__(
        self,
        message: str = "No autorizado.",
        *,
        code: str = "authorization_error",
        status_code: int = 403,
        details: object | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


class ResourceNotFoundError(AppError):
    def __init__(
        self,
        message: str = "Recurso no encontrado.",
        *,
        code: str = "resource_not_found",
    ) -> None:
        super().__init__(message=message, code=code, status_code=404)
