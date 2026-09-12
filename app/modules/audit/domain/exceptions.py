from app.core.exceptions import NotFoundError


class AuditLogNotFoundError(NotFoundError):
    def __init__(self, log_id: str):
        super().__init__(f"Audit log entry with ID '{log_id}' not found.")
