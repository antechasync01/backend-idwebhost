from app.core.exceptions import ConflictError, NotFoundError


class TaskNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(message=f"Task '{identifier}' not found.")


class InvalidTaskStateError(ConflictError):
    def __init__(self, current_status: str, action: str):
        super().__init__(
            message=f"Cannot perform '{action}' on task in state '{current_status}'."
        )
