from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_permissions
from app.core.exceptions import AuthenticationError
from app.core.responses import create_response
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.modules.auth.domain.schemas import LoginRequest, RefreshTokenRequest
from app.modules.users.infrastructure.models import Role, RolePermission, User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", status_code=status.HTTP_200_OK)
def login(request_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with username/email and password, returning access and refresh JWT tokens."""
    identifier = request_data.username_or_email.strip()
    
    user = (
        db.query(User)
        .options(joinedload(User.role_rel))
        .filter(
            (User.username == identifier) | (User.email == identifier)
        )
        .first()
    )

    if not user or not user.is_active:
        raise AuthenticationError("Invalid username or password")

    if not verify_password(request_data.password, user.hashed_password):
        raise AuthenticationError("Invalid username or password")

    role_code = user.role_rel.code if user.role_rel else "USER"
    access_token = create_access_token(subject=user.id, role_code=role_code)
    refresh_token = create_refresh_token(subject=user.id, role_code=role_code)

    return create_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Issue a new access token using a valid refresh token."""
    payload = decode_token(request_data.refresh_token)
    if not payload or payload.get("token_type") != "refresh":
        raise AuthenticationError("Invalid or expired refresh token")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Invalid refresh token payload")

    user = (
        db.query(User)
        .options(joinedload(User.role_rel))
        .filter(User.id == user_id_str, User.is_active == True)
        .first()
    )

    if not user:
        raise AuthenticationError("User not found or inactive")

    role_code = user.role_rel.code if user.role_rel else "USER"
    new_access_token = create_access_token(subject=user.id, role_code=role_code)

    return create_response(
        data={
            "access_token": new_access_token,
            "token_type": "bearer",
        }
    )


@router.get("/me", status_code=status.HTTP_200_OK)
def get_me(
    current_user: User = Depends(get_current_user),
    user_permissions: set[str] = Depends(get_current_user_permissions),
):
    """Get current authenticated user profile, role, and granted permissions."""
    role_code = current_user.role_rel.code if current_user.role_rel else None
    role_name = current_user.role_rel.name if current_user.role_rel else None

    return create_response(
        data={
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role_code": role_code,
            "role_name": role_name,
            "permissions": sorted(list(user_permissions)),
        }
    )
