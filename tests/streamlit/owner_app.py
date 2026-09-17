"""Owner Dashboard & Analytics UI — Streamlit Application.

Run standalone with:
    uv run streamlit run tests/streamlit/owner_app.py
"""

import sys
from pathlib import Path

# Add current directory to sys.path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from api_client import AuraAPIClient, extract_items


def render_owner_ui(client: AuraAPIClient):
    st.markdown("## 👑 Owner Dashboard & Decision Intelligence")
    st.caption("Aplikasi Pemilik Toko AURA — Overview Analytics, Inventory Health, Audit Trail & Daily Closing")

    # Quick Navigation Tabs
    tab_analytics, tab_inventory, tab_hermes, tab_audit, tab_closing = st.tabs(
        ["📊 Executive Analytics", "📦 Stock & Inventory Health", "🤖 Hermes AI Assistant", "📜 Immutable Audit Logs", "🔒 Daily Closing Finalization"]
    )

    # ---------------- TAB 1: EXECUTIVE ANALYTICS ----------------
    with tab_analytics:
        st.subheader("Ringkasan Kinerja Bisnis")
        col_period, col_refresh = st.columns([3, 1])
        with col_period:
            period = st.selectbox("Rentang Waktu Analytics", ["7d", "today", "30d", "this_month"], key="owner_period")
        with col_refresh:
            st.write("")
            st.write("")
            btn_refresh = st.button("🔄 Refresh Data", key="refresh_analytics")

        ok, summary = client.get_analytics_summary(period=period)
        if ok and isinstance(summary, dict):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Gross Revenue", f"Rp {summary.get('gross_revenue', 0):,.2f}")
            c2.metric("Total Refunds", f"Rp {summary.get('total_refunds', 0):,.2f}")
            c3.metric("Net Revenue", f"Rp {summary.get('net_revenue', 0):,.2f}")
            c4.metric("Total Transaksi", f"{summary.get('transaction_count', 0)} sales")

            c5, c6 = st.columns(2)
            c5.metric("Avg Basket Size", f"Rp {summary.get('average_transaction_value', 0):,.2f}")
            c6.metric("Total Item Terjual", f"{summary.get('total_items_sold', 0)} pcs")
        else:
            st.error(f"Gagal memuat summary analytics: {summary}")

        st.divider()

        # Sales Trend Chart
        st.subheader("📈 Trend Penjualan Harian")
        ok_trend, trend_data = client.get_sales_trend(period=period)
        if ok_trend and isinstance(trend_data, dict):
            items = extract_items(trend_data)
            if items:
                chart_data = {
                    "Gross Revenue": {item["date"]: item["gross_revenue"] for item in items},
                    "Net Revenue": {item["date"]: item["net_revenue"] for item in items},
                }
                st.line_chart(chart_data)
                st.dataframe(items, use_container_width=True)
            else:
                st.info("Belum ada data transaksi pada rentang waktu ini.")

        st.divider()
        
        st.subheader("🧠 Automated AI Sales Insights (Weekly & Monthly)")
        with st.spinner("Mengambil analisis otomatis terbaru..."):
            col_7d, col_30d = st.columns(2)
            
            with col_7d:
                st.markdown("#### Analisis 7 Hari Terakhir")
                ok_7, data_7 = client.get_periodic_insights("WEEKLY")
                if ok_7 and isinstance(data_7, dict):
                    st.caption(f"Dibuat pada: {data_7.get('generated_at', '')[:16].replace('T', ' ')}")
                    # Extracted summary (first 150 chars or first paragraph)
                    full_text_7 = data_7.get('analysis_result', '')
                    summary_7 = full_text_7.split('\n')[0] if full_text_7 else ""
                    st.write(summary_7[:150] + "...")
                    with st.expander("Baca Analisis Selengkapnya (7 Hari)"):
                        st.markdown(full_text_7)
                else:
                    st.info("Belum ada analisis mingguan yang digenerate oleh sistem.")
                    
            with col_30d:
                st.markdown("#### Analisis 30 Hari Terakhir")
                ok_30, data_30 = client.get_periodic_insights("MONTHLY")
                if ok_30 and isinstance(data_30, dict):
                    st.caption(f"Dibuat pada: {data_30.get('generated_at', '')[:16].replace('T', ' ')}")
                    # Extracted summary
                    full_text_30 = data_30.get('analysis_result', '')
                    summary_30 = full_text_30.split('\n')[0] if full_text_30 else ""
                    st.write(summary_30[:150] + "...")
                    with st.expander("Baca Analisis Selengkapnya (30 Hari)"):
                        st.markdown(full_text_30)
                else:
                    st.info("Belum ada analisis bulanan yang digenerate oleh sistem.")

        st.divider()

        # Top Products
        st.subheader("🔥 Top 5 Produk Terlaris")
        ok_top, top_data = client.get_top_products(limit=5, period=period)
        if ok_top and isinstance(top_data, dict):
            top_items = extract_items(top_data)
            if top_items:
                st.dataframe(top_items, use_container_width=True)
            else:
                st.info("Belum ada data penjualan produk.")

    # ---------------- TAB 2: INVENTORY HEALTH ----------------
    with tab_inventory:
        st.subheader("Kesehatan & Valuasi Inventori")
        ok_health, health_data = client.get_inventory_health(low_stock_threshold=10)
        if ok_health and isinstance(health_data, dict):
            h1, h2, h3, h4 = st.columns(4)
            h1.metric("Total Produk Master", health_data.get("total_products", 0))
            h2.metric("Total Stok Display", f"{health_data.get('total_display_quantity', 0)} pcs")
            h3.metric("Total Stok On-Hand", f"{health_data.get('total_on_hand_quantity', 0)} pcs")
            h4.metric("Total Stok Fisik", f"{health_data.get('total_inventory_quantity', 0)} pcs")

            h5, h6, h7, h8 = st.columns(4)
            h5.metric("Valuasi Modal (Cost)", f"Rp {health_data.get('total_inventory_cost_value', 0):,.2f}")
            h6.metric("Valuasi Jual (Retail)", f"Rp {health_data.get('total_inventory_retail_value', 0):,.2f}")
            h7.metric("Stok Menipis (<=10)", health_data.get("low_stock_product_count", 0))
            h8.metric("Stok Habis (0)", health_data.get("out_of_stock_product_count", 0))

        st.divider()
        st.subheader("Daftar Inventori Lengkap")
        ok_inv, inv_res = client.get_inventory()
        inv_items = extract_items(inv_res) if ok_inv else []
        if inv_items:
            st.dataframe(inv_items, use_container_width=True)
        else:
            st.info("Data inventori kosong.")

    # ---------------- TAB 3: HERMES AI ASSISTANT ----------------
    with tab_hermes:
        st.subheader("🤖 Hermes AI Conversational Reasoning Agent")
        st.caption("Hermes terintegrasi dengan MCP Gateway untuk analisis stok & transaksi secara real-time.")

        col_chat, col_insights = st.columns([1, 1])

        with col_chat:
            st.markdown("### 💬 Chat Percakapan Hermes")

            if "hermes_conversation_id" not in st.session_state:
                st.session_state.hermes_conversation_id = None
            if "hermes_chat_history" not in st.session_state:
                st.session_state.hermes_chat_history = []

            # Session Header & Controls
            col_sess_info, col_sess_btn = st.columns([2, 1])
            with col_sess_info:
                if st.session_state.hermes_conversation_id:
                    st.caption(f"🆔 **Session Aktif:** `{st.session_state.hermes_conversation_id}`")
                else:
                    st.caption("ℹ️ *Percakapan baru (session akan tersimpan otomatis)*")
            with col_sess_btn:
                if st.button("🔄 Reset Percakapan", key="btn_reset_hermes_session"):
                    st.session_state.hermes_conversation_id = None
                    st.session_state.hermes_chat_history = []
                    st.rerun()

            # Chat History Display
            chat_container = st.container(height=360)
            with chat_container:
                if not st.session_state.hermes_chat_history:
                    st.info("👋 Mulai percakapan dengan Hermes Agent. Konteks percakapan akan terus berlanjut dalam satu session.")
                for msg in st.session_state.hermes_chat_history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        if msg.get("tools"):
                            st.caption(f"🛠️ **Tools Digunakan:** {', '.join(msg['tools'])}")

            # Chat Input Form
            with st.form(key="hermes_chat_form", clear_on_submit=True):
                user_input = st.text_input(
                    "Tanyakan ke Hermes AI...",
                    placeholder="Contoh: Produk apa yang berisiko habis? Lalu buatkan rekomendasinya...",
                    key="hermes_input_field"
                )
                submitted = st.form_submit_button("🚀 Kirim Pertanyaan")

            if submitted and user_input.strip():
                st.session_state.hermes_chat_history.append({"role": "user", "content": user_input.strip()})
                with st.spinner("Hermes sedang menganalisis via MCP..."):
                    ok_h, res_h = client.send_hermes_chat(
                        prompt=user_input.strip(),
                        conversation_id=st.session_state.hermes_conversation_id
                    )
                    if ok_h and isinstance(res_h, dict):
                        new_sid = res_h.get("conversation_id")
                        if new_sid:
                            st.session_state.hermes_conversation_id = new_sid
                        st.session_state.hermes_chat_history.append({
                            "role": "assistant",
                            "content": res_h.get("reply", ""),
                            "tools": res_h.get("tools_used", [])
                        })
                        st.rerun()
                    else:
                        st.error(f"Gagal berkomunikasi dengan Hermes: {res_h}")

        with col_insights:
            st.markdown("### 🚨 Stockout Risk & AI Insights")
            ok_r, risk_list = client.get_stockout_risks()
            if ok_r and isinstance(risk_list, list):
                st.markdown("#### ⚠️ Risiko Kehabisan Barang:")
                if risk_list:
                    st.dataframe(risk_list, use_container_width=True)
                else:
                    st.success("Seluruh stok dalam batas aman!")

            st.divider()
            ok_in, insights_list = client.get_ai_insights()
            if ok_in and isinstance(insights_list, list):
                st.markdown("#### 💡 Insight Kecerdasan Toko:")
                if insights_list:
                    st.dataframe(insights_list, use_container_width=True)

    # ---------------- TAB 4: AUDIT LOGS ----------------
    with tab_audit:
        st.subheader("Audit Trail Aktivitas Sistem")
        c_act, c_ent = st.columns(2)
        with c_act:
            filter_action = st.text_input("Filter Action (mis. CREATE, APPROVE)", key="audit_action")
        with c_ent:
            filter_entity = st.text_input("Filter Entity (mis. Product, Sale, Receiving)", key="audit_entity")

        ok_audit, audit_data = client.list_audit_logs(action=filter_action, entity_type=filter_entity)
        if ok_audit and isinstance(audit_data, dict):
            logs = extract_items(audit_data)
            st.caption(f"Total Log: {audit_data.get('total', len(logs))} records")
            if logs:
                st.dataframe(logs, use_container_width=True)
            else:
                st.info("Tidak ada log aktivitas yang sesuai filter.")

    # ---------------- TAB 5: DAILY CLOSING FINALIZATION ----------------
    with tab_closing:
        st.subheader("Finalisasi Penutupan Toko Harian")
        ok_cls, cls_data = client.get_today_closing()
        if ok_cls and isinstance(cls_data, dict):
            st.json(cls_data)
            status_val = cls_data.get("status")
            if status_val == "FINALIZED":
                st.success("Daily closing hari ini sudah FINALIZED!")
            else:
                st.warning(f"Status Daily Closing saat ini: {status_val}")
                closing_notes = st.text_area("Catatan Finalisasi Owner", "Penutupan harian toko disetujui.")
                if st.button("✅ Finalisasi Daily Closing Hari Ini"):
                    ok_fin, fin_res = client.finalize_daily_closing(notes=closing_notes)
                    if ok_fin:
                        st.success("Daily closing berhasil di-finalize!")
                        st.rerun()
                    else:
                        st.error(f"Gagal finalize closing: {fin_res}")



if __name__ == "__main__":
    st.set_page_config(page_title="AURA POS — Owner Dashboard", page_icon="👑", layout="wide")
    client = AuraAPIClient()
    ok, res = client.login("owner@aura.pos", "owner123")
    if not ok:
        st.error(f"⚠️ Gagal terhubung ke Backend (http://127.0.0.1:8000/api/v1): {res}")
        st.info("Pastikan server FastAPI backend sudah berjalan (`uvicorn app.main:app --reload`).")
    else:
        render_owner_ui(client)
