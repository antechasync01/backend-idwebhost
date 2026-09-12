from typing import Any
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.users.infrastructure.models import User, UserRole
from app.mcp.registry import TOOL_REGISTRY, get_available_tools_for_role


class MCPContextGateway:
    @staticmethod
    def list_tools(user: User) -> list[dict[str, Any]]:
        """List all tools accessible by the authenticated user."""
        return get_available_tools_for_role(user.role)

    @staticmethod
    def execute_tool(
        tool_name: str,
        arguments: dict[str, Any],
        db: Session,
        user: User
    ) -> Any:
        """Execute an MCP tool within the user's security authorization context."""
        tool_def = TOOL_REGISTRY.get(tool_name)
        if not tool_def:
            raise NotFoundError(f"MCP Tool '{tool_name}' tidak ditemukan.")

        if not user.role or user.role not in tool_def.allowed_roles:
            role_str = user.role.value if isinstance(user.role, UserRole) else (user.role or "NONE")
            raise ForbiddenError(
                f"Pengguna dengan role '{role_str}' tidak diizinkan menjalankan tool '{tool_name}'."
            )

        # Execute tool safely
        return tool_def.func(db=db, **arguments)
