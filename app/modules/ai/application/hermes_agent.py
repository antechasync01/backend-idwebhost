import uuid
import requests
from typing import Any
from sqlalchemy.orm import Session

from app.mcp.gateway import MCPContextGateway
from app.modules.users.infrastructure.models import User, UserRole
from app.modules.audit.infrastructure.models import AuditLog, ActorType
from app.modules.ai.api.schemas import HermesChatResponse
from app.core.config import settings


class HermesAgentService:
    @staticmethod
    def process_chat(
        db: Session,
        user: User,
        prompt: str,
        conversation_id: str | None = None
    ) -> HermesChatResponse:
        session_id = conversation_id or f"hermes-session-{uuid.uuid4().hex[:8]}"
        role_str = user.role_rel.code if user.role_rel else "USER"

        messages = [
            {
                "role": "system", 
                "content": f"You are Hermes Agent for AURA POS. The user talking to you is {user.full_name} and their role is {role_str}. Please use the provided MCP tools to help them if needed. Answer in Indonesian unless requested otherwise."
            },
            {"role": "user", "content": prompt}
        ]

        headers = {
            "Authorization": f"Bearer {settings.HERMES_API_SERVER_KEY}",
            "Content-Type": "application/json"
        }
        if conversation_id:
            headers["X-Hermes-Session-Id"] = conversation_id

        reply = ""
        tools_used = []
        try:
            response = requests.post(
                f"{settings.HERMES_API_URL}/v1/chat/completions",
                headers=headers,
                json={
                    "model": "hermes-agent",
                    "messages": messages,
                    "stream": False
                },
                timeout=120  # allow time for tool execution
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                # Capture real session ID from Hermes response headers to maintain continuity
                hermes_sid = response.headers.get("X-Hermes-Session-Id")
                if hermes_sid:
                    session_id = hermes_sid
                # Optional: parse tool calls if returned in the message to populate tools_used
                if "tool_calls" in data["choices"][0]["message"] and data["choices"][0]["message"]["tool_calls"]:
                    for tc in data["choices"][0]["message"]["tool_calls"]:
                        tools_used.append(tc["function"]["name"])
            else:
                reply = f"Maaf, terjadi kesalahan saat menghubungi Hermes Agent. (Status: {response.status_code})"
                print(f"Hermes API Error: {response.text}")
        except Exception as e:
            reply = f"Maaf, tidak dapat terhubung ke Hermes Agent saat ini. Error: {str(e)}"
            print(f"Hermes Connection Error: {str(e)}")

        # Record AI Audit Log
        audit = AuditLog(
            actor_id=user.id,
            actor_type=ActorType.AI,
            action="HERMES_REASONING_CHAT",
            entity_type="HERMES_CHAT_SESSION",
            entity_id=None,
            before_data=None,
            after_data={"prompt": prompt, "reply_summary": reply[:200]},
            metadata_info={
                "conversation_id": session_id,
                "user_role": role_str,
                "tools_used": tools_used,
            }
        )
        db.add(audit)
        db.commit()

        return HermesChatResponse(
            reply=reply,
            conversation_id=session_id,
            tools_used=tools_used,
            data_evidence=None
        )

