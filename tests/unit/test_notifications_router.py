import pytest
from uuid import uuid4
from app.modules.users.infrastructure.models import User, Role
from app.modules.notifications.infrastructure.models import Notification, NotificationType, UserRole

def test_user_role_property():
    role = Role(id=uuid4(), code="WAREHOUSE_ADMIN", name="Warehouse Admin")
    user_with_role = User(id=uuid4(), username="admin", email="admin@example.com", full_name="Admin", role_rel=role)
    user_without_role = User(id=uuid4(), username="norole", email="norole@example.com", full_name="No Role")

    assert user_with_role.role == "WAREHOUSE_ADMIN"
    assert user_without_role.role is None


def test_create_response_message_param():
    from app.core.responses import create_response
    import json

    res = create_response(data={"id": "123"}, message="Notification marked as read")
    body = json.loads(res.body.decode())
    assert body["data"] == {"id": "123"}
    assert body["meta"]["message"] == "Notification marked as read"

