"""AURA POS Streamlit Unified Multi-Role Test Application.

Run with:
    uv run streamlit run tests/streamlit/app.py
"""

import os
import sys
from pathlib import Path

# Add current directory to sys.path for module resolution
sys.path.insert(0, str(Path(__file__).resolve().parent))

import importlib
import streamlit as st
import api_client
importlib.reload(api_client)
from api_client import AuraAPIClient
from cashier_app import render_cashier_ui
from owner_app import render_owner_ui
from wh_admin_app import render_wh_admin_ui
from wh_staff_app import render_wh_staff_ui

DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000/api/v1")

st.set_page_config(
    page_title="AURA POS — Multi-Role Interactive Suite",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for premium look
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    .stMetric {
        background-color: #1e222d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e3440;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state initialization
if "client" not in st.session_state:
    st.session_state["client"] = AuraAPIClient(base_url=DEFAULT_API_BASE_URL)
else:
    # Re-instantiate AuraAPIClient to ensure fresh methods from api_client.py are used
    _old_token = st.session_state["client"].token
    _old_user = st.session_state["client"].user_info
    _old_url = getattr(st.session_state["client"], "base_url", DEFAULT_API_BASE_URL)
    _new_client = AuraAPIClient(base_url=_old_url)
    _new_client.token = _old_token
    _new_client.user_info = _old_user
    st.session_state["client"] = _new_client

client: AuraAPIClient = st.session_state["client"]

# Sidebar Navigation & User Auth
with st.sidebar:
    st.image("https://img.icons8.com/color/96/shop.png", width=64)
    st.title("AURA POS System")
    st.caption("AI-Native Minimarket Operating Platform")

    st.divider()

    st.subheader("🔑 Select System Role")
    role_choice = st.selectbox(
        "Pilih Role Pengguna",
        [
            "👑 Pemilik Toko (OWNER)",
            "🏬 Manajer Gudang (WAREHOUSE_ADMIN)",
            "📦 Staf Gudang (WAREHOUSE_STAFF)",
            "🛒 Kasir Toko (CASHIER)",
        ],
    )

    # Demo Accounts Mapping
    demo_accounts = {
        "👑 Pemilik Toko (OWNER)": ("owner@aura.pos", "owner123"),
        "🏬 Manajer Gudang (WAREHOUSE_ADMIN)": ("admin@aura.pos", "admin123"),
        "📦 Staf Gudang (WAREHOUSE_STAFF)": ("staff@aura.pos", "staff123"),
        "🛒 Kasir Toko (CASHIER)": ("cashier@aura.pos", "cashier123"),
    }

    default_email, default_pw = demo_accounts[role_choice]

    st.divider()

    st.markdown("### Authentication Settings")
    backend_url = st.text_input("Backend Base URL", value=DEFAULT_API_BASE_URL)
    client.base_url = backend_url.rstrip("/")

    email = st.text_input("Email / Username", value=default_email)
    password = st.text_input("Password", value=default_pw, type="password")

    btn_login = st.button("🔐 Login Ke Backend", type="primary", use_container_width=True)

    if btn_login or not client.token:
        ok, res = client.login(email, password)
        if ok:
            st.success(f"Logged in as {email}")
        else:
            st.error(f"Login failed: {res}")

    if client.token and client.user_info:
        st.info(f"Active User: **{client.user_info.get('full_name')}** ({client.user_info.get('username')})")

    st.divider()
    st.caption("AURA POS v0.1.0 — Hackathon MVP Build")


# Main Content Area
if not client.token:
    st.warning("⚠️ Silakan login terlebih dahulu melalui panel di sebelah kiri.")
    st.stop()

# Route to role UIs
if "OWNER" in role_choice:
    render_owner_ui(client)
elif "WAREHOUSE_ADMIN" in role_choice:
    render_wh_admin_ui(client)
elif "WAREHOUSE_STAFF" in role_choice:
    render_wh_staff_ui(client)
elif "CASHIER" in role_choice:
    render_cashier_ui(client)
