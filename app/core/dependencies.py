import uuid
from typing import Annotated, Callable
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.security import decode_token
from app.modules.users.infrastructure.models import Permission, Role, RolePermission, User, UserRole
from app.modules.users.application.attendance_service import AttendanceService

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(security_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate JWT Bearer token, returning current authenticated User."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Missing Authorization Bearer token")

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise AuthenticationError("Invalid or expired token")

    if payload.get("token_type") != "access":
        raise AuthenticationError("Invalid token type. Expected access token")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Invalid token payload: missing subject")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid token payload: invalid user UUID")

    user = (
        db.query(User)
        .options(
            joinedload(User.role_rel)
            .joinedload(Role.permissions)
            .joinedload(RolePermission.permission)
        )
        .filter(User.id == user_id, User.is_active == True)
        .first()
    )

    if not user:
        raise AuthenticationError("User not found or inactive")

    return user


def get_current_user_permissions(user: User = Depends(get_current_user)) -> set[str]:
    """Retrieve all permission codes granted to the current user's role."""
    permissions: set[str] = set()
    if user.role_rel and user.role_rel.permissions:
        for rp in user.role_rel.permissions:
            if rp.permission and rp.permission.code:
                permissions.add(rp.permission.code)
    return permissions


def require_permission(permission_code: str) -> Callable:
    """Dependency factory for granular permission checks and clock-in validation."""
    def dependency(
        user: User = Depends(get_current_user),
        user_permissions: set[str] = Depends(get_current_user_permissions),
        db: Session = Depends(get_db)
    ) -> User:
        if permission_code not in user_permissions:
            raise ForbiddenError(f"Forbidden: Permission '{permission_code}' is required")
        
        if user.role != UserRole.OWNER:
            attendance_service = AttendanceService(db)
            if not attendance_service.is_clocked_in(user.id):
                raise ForbiddenError("Forbidden: You must clock in to access the system")
                
        return user

    return dependency


def require_role(role_code: str) -> Callable:
    """Dependency factory for role code checks and clock-in validation."""
    def dependency(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        if not user.role_rel or user.role_rel.code != role_code:
            raise ForbiddenError(f"Forbidden: Role '{role_code}' is required")
            
        if user.role != UserRole.OWNER:
            attendance_service = AttendanceService(db)
            if not attendance_service.is_clocked_in(user.id):
                raise ForbiddenError("Forbidden: You must clock in to access the system")
                
        return user

    return dependency
