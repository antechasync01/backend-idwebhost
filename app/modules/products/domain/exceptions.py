from app.core.exceptions import ConflictError, NotFoundError


class ProductNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Product '{identifier}' not found.")


class CategoryNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Category '{identifier}' not found.")


class RegistrationRequestNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Product registration request '{identifier}' not found.")


class DuplicateGTINError(ConflictError):
    def __init__(self, gtin: str):
        super().__init__(message=f"Product with GTIN '{gtin}' already exists.")


class InvalidRegistrationStateError(ConflictError):
    def __init__(self, current_status: str):
        super().__init__(message=f"Registration request is in state '{current_status}' and cannot be modified.")
