from app.core.exceptions import ConflictError, NotFoundError, ValidationError


class SaleNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Sale '{identifier}' not found.")


class InsufficientDisplayStockError(ConflictError):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            message=f"Insufficient DISPLAY stock for '{product_name}'. Available: {available}, Requested: {requested}."
        )


class InsufficientPaymentError(ValidationError):
    def __init__(self, cash_paid: float, total_amount: float):
        super().__init__(
            message=f"Insufficient cash payment. Total Amount: {total_amount:.2f}, Cash Paid: {cash_paid:.2f}."
        )


class InvalidSaleStateError(ConflictError):
    def __init__(self, current_status: str, action: str):
        super().__init__(
            message=f"Cannot perform '{action}' on sale in status '{current_status}'."
        )


class RefundExceedsOriginalError(ValidationError):
    def __init__(self, message: str):
        super().__init__(message=message)


class DailyClosingNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Daily closing for '{identifier}' not found.")


class AlreadyClosedError(ConflictError):
    def __init__(self, closing_type: str, business_date: str):
        super().__init__(message=f"{closing_type} for date '{business_date}' is already closed.")


class InvalidClosingStateError(ConflictError):
    def __init__(self, message: str):
        super().__init__(message=message)
