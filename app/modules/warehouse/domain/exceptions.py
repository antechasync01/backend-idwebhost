from app.core.exceptions import ConflictError, NotFoundError, ValidationError


class ReceivingNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Receiving '{identifier}' not found.")


class InvalidReceivingStateError(ConflictError):
    def __init__(self, current_status: str, action: str):
        super().__init__(
            message=f"Cannot perform '{action}' on receiving in state '{current_status}'."
        )


class WarehouseRequestNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Warehouse request '{identifier}' not found.")


class InvalidReceivingItemError(ValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)
