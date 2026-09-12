from app.core.exceptions import ConflictError, NotFoundError, ValidationError


class InventoryNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Inventory for product '{identifier}' not found.")


class InsufficientStockError(ConflictError):
    def __init__(self, available: int, requested: int, location: str):
        super().__init__(
            message=f"Insufficient stock in '{location}'. Available: {available}, Requested: {requested}."
        )


class InvalidTransferQuantityError(ValidationError):
    def __init__(self, quantity: int):
        super().__init__(message=f"Transfer quantity must be greater than 0. Got: {quantity}.")


class InvalidAdjustmentError(ValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)
