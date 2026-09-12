from app.core.exceptions import ValidationError


class InvalidDateRangeError(ValidationError):
    def __init__(self, message: str = "Start date must be before or equal to end date."):
        super().__init__(message)
