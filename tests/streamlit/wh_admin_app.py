"""Warehouse Admin Portal UI — Streamlit Application.

Run standalone with:
    uv run streamlit run tests/streamlit/wh_admin_app.py
"""

import sys
from pathlib import Path

# Add current directory to sys.path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from api_client import AuraAPIClient, extract_items


def render_wh_admin_ui(client: AuraAPIClient):
    st.markdown("## 🏬 Warehouse Admin Portal")
    st.caption("Aplikasi Manajer Gudang AURA — Product Master, Persetujuan Pendaftaran, Penerimaan Barang, Stock Adjustment & Opname")

    tab_products, tab_registrations, tab_receivings, tab_stock, tab_movements = st.tabs(
        ["📦 Catalog & Product Master", "📋 Request Produk Baru", "🚚 Approval Penerimaan Barang", "🔁 Penyesuaian & Transfer Stok", "📜 Stock Movement Logs"]
    )

    # ---------------- TAB 1: PRODUCT MASTER ----------------
    with tab_products:
        st.subheader("Master Katalog Produk")
        col_search, col_add = st.columns([3, 1])
        with col_search:
            q_product = st.text_input("Cari Produk (Nama / GTIN / Brand)", key="wh_admin_prod_search")
        
        ok_p, p_res = client.list_products(query=q_product.strip() if q_product and q_product.strip() else None)
        prods = extract_items(p_res) if ok_p else []
        st.caption(f"Total Produk Ditemukan: {len(prods)}")
        if prods:
            st.dataframe(prods, use_container_width=True)
        else:
            st.info("Produk tidak ditemukan.")

        st.divider()
        st.subheader("➕ Tambah Master Produk Baru Langsung")
        with st.form("form_create_product"):
            f_gtin = st.text_input("GTIN / Barcode (13 digit)", "8997001002003")
            f_name = st.text_input("Nama Produk", "Indomie Goreng Rasa Ayam Geprek")
            f_brand = st.text_input("Brand", "Indofood")
            f_unit = st.selectbox("Satuan Unit", ["pcs", "pack", "box", "kg"])
            f_purchase = st.number_input("Harga Beli (Purchase Price)", value=3000.0, step=500.0)
            f_selling = st.number_input("Harga Jual (Selling Price)", value=3800.0, step=500.0)
            btn_create = st.form_submit_button("Simpan Produk Ke Katalog Master")

            if btn_create:
                payload = {
                    "gtin": f_gtin.strip(),
                    "name": f_name.strip(),
                    "brand": f_brand.strip(),
                    "unit": f_unit,
                    "purchase_price": f_purchase,
                    "selling_price": f_selling,
                }
                ok_c, res_c = client.create_product(payload)
                if ok_c:
                    st.success(f"Produk '{f_name}' berhasil ditambahkan ke Katalog Master!")
                    st.rerun()
                else:
                    st.error(f"Gagal menambahkan produk: {res_c}")

    # ---------------- TAB 2: PENDING REGISTRATIONS ----------------
    with tab_registrations:
        st.subheader("Persetujuan Request Pendaftaran Produk Baru")
        ok_reg, reg_res = client.list_registration_requests(status="PENDING")
        requests_list = extract_items(reg_res) if ok_reg else []
        st.write(f"Pending Requests: **{len(requests_list)}**")
        if requests_list:
            for req in requests_list:
                with st.expander(f"📌 {req.get('suggested_name')} (GTIN: {req.get('gtin')})"):
                    st.write(f"- **Suggested Unit**: {req.get('suggested_unit')}")
                    st.write(f"- **Suggested Purchase**: Rp {req.get('suggested_purchase_price', 0):,.2f}")
                    st.write(f"- **Suggested Selling**: Rp {req.get('suggested_selling_price', 0):,.2f}")
                    notes_in = st.text_input("Catatan Review", "Disetujui Admin Gudang", key=f"notes_{req['id']}")
                    
                    col_app, col_rej = st.columns(2)
                    with col_app:
                        if st.button("✅ Approve & Daftarkan", key=f"app_{req['id']}"):
                            ok_a, res_a = client.approve_registration_request(req['id'], notes_in)
                            if ok_a:
                                st.success("Request disetujui! Produk otomatis dibuat di Product Master.")
                                st.rerun()
                            else:
                                st.error(f"Gagal approve: {res_a}")
                    with col_rej:
                        if st.button("❌ Tolak Request", key=f"rej_{req['id']}"):
                            ok_r, res_r = client.reject_registration_request(req['id'], notes_in)
                            if ok_r:
                                st.warning("Request ditolak.")
                                st.rerun()
                            else:
                                st.error(f"Gagal reject: {res_r}")
        else:
            st.info("Tidak ada request pendaftaran produk yang menunggu persetujuan.")

    # ---------------- TAB 3: RECEIVINGS ----------------
    with tab_receivings:
        st.subheader("Approval Penerimaan Barang Gudang")
        ok_rec, rec_res = client.list_receivings(status="SUBMITTED")
        receivings_list = extract_items(rec_res) if ok_rec else []
        st.write(f"Receivings Pending Approval: **{len(receivings_list)}**")
        if receivings_list:
            for rec in receivings_list:
                with st.expander(f"🚚 Receiving #{rec.get('receiving_number')} — Status: {rec.get('status')}"):
                    st.write(f"- **Catatan**: {rec.get('notes') or '-'}")
                    st.write("Items Received:")
                    st.dataframe(extract_items(rec.get("items", [])), use_container_width=True)
                    
                    col_ar, col_rj = st.columns(2)
                    with col_ar:
                        if st.button("✅ Setujui & Tambahkan ke Stok ON_HAND", key=f"app_rec_{rec['id']}"):
                            ok_ar, res_ar = client.approve_receiving(rec['id'])
                            if ok_ar:
                                st.success("Penerimaan barang disetujui! Stok ON_HAND bertambah.")
                                st.rerun()
                            else:
                                st.error(f"Gagal menyetujui penerimaan: {res_ar}")
                    with col_rj:
                        rej_notes = st.text_input("Alasan Penolakan", "Jumlah Fisik Tidak Sesuai Surat Jalan", key=f"rej_rec_notes_{rec['id']}")
                        if st.button("❌ Tolak Penerimaan Barang", key=f"rej_rec_{rec['id']}"):
                            ok_rj, res_rj = client.reject_receiving(rec['id'], rej_notes)
                            if ok_rj:
                                st.warning("Dokumen penerimaan barang ditolak.")
                                st.rerun()
                            else:
                                st.error(f"Gagal menolak penerimaan: {res_rj}")
        else:
            st.info("Tidak ada dokumen penerimaan barang yang menunggu persetujuan.")

    # ---------------- TAB 4: STOCK ADJUSTMENT & TRANSFER ----------------
    with tab_stock:
        st.subheader("Penyesuaian & Transfer Stok Gudang")

        # Build product dropdown options cleanly from both Inventory and Product Catalog
        prod_options = {}
        ok_inv, inv_res = client.get_inventory()
        inv_items = extract_items(inv_res) if ok_inv else []

        for item in inv_items:
            p_name = item.get("product_name") or (item.get("product", {}).get("name") if isinstance(item.get("product"), dict) else None)
            gtin = item.get("gtin") or (item.get("product", {}).get("gtin") if isinstance(item.get("product"), dict) else None)
            pid = item.get("product_id")
            disp = item.get("display_quantity", 0)
            oh = item.get("on_hand_quantity", 0)
            if pid and p_name:
                label = f"{p_name} (GTIN: {gtin}) [Display: {disp}, On-Hand: {oh}]"
                prod_options[label] = pid

        # Fallback to Product Master catalog if inventory list is empty
        if not prod_options:
            ok_p, p_res = client.list_products()
            prods = extract_items(p_res) if ok_p else []
            for p in prods:
                label = f"{p['name']} (GTIN: {p['gtin']})"
                prod_options[label] = p["id"]

        st.markdown("### 1. Internal Stock Transfer (ON_HAND ↔ DISPLAY)")
        with st.form("form_transfer_stock"):
            selected_prod_name = st.selectbox("Pilih Produk", list(prod_options.keys()) if prod_options else ["-"])
            transfer_direction = st.selectbox("Arah Transfer", ["ON_HAND -> DISPLAY", "DISPLAY -> ON_HAND"])
            transfer_qty = st.number_input("Jumlah Kuantitas", min_value=1, value=5)
            btn_transfer = st.form_submit_button("Lakukan Transfer")

            if btn_transfer and prod_options and selected_prod_name != "-":
                target_pid = prod_options[selected_prod_name]
                from_loc = "ON_HAND" if transfer_direction.startswith("ON_HAND") else "DISPLAY"
                to_loc = "DISPLAY" if from_loc == "ON_HAND" else "ON_HAND"

                ok_t, res_t = client.transfer_inventory(target_pid, from_loc, to_loc, transfer_qty)
                if ok_t:
                    st.success(f"Berhasil mentransfer {transfer_qty} pcs dari {from_loc} ke {to_loc}!")
                    st.rerun()
                else:
                    st.error(f"Gagal transfer: {res_t}")

        st.divider()
        st.markdown("### 2. Manual Inventory Adjustment")
        with st.form("form_adjust_stock"):
            adj_prod_name = st.selectbox("Pilih Produk untuk Adjustment", list(prod_options.keys()) if prod_options else ["-"], key="adj_prod")
            adj_loc = st.selectbox("Lokasi Stok", ["DISPLAY", "ON_HAND"])
            adj_qty_change = st.number_input("Perubahan Kuantitas (+ Tambah, - Kurang)", value=10)
            adj_reason = st.text_input("Alasan Penyesuaian", "Stock Opname Rutin Gudang")
            btn_adjust = st.form_submit_button("Simpan Penyesuaian Stok")

            if btn_adjust and prod_options and adj_prod_name != "-":
                target_pid = prod_options[adj_prod_name]
                ok_adj, res_adj = client.adjust_inventory(target_pid, adj_loc, adj_qty_change, adj_reason)
                if ok_adj:
                    st.success(f"Stok {adj_loc} berhasil disesuaikan ({adj_qty_change:+d} pcs)!")
                    st.rerun()
                else:
                    st.error(f"Gagal penyesuaian stok: {res_adj}")

    # ---------------- TAB 5: STOCK MOVEMENTS ----------------
    with tab_movements:
        st.subheader("Histori Pergerakan Stok (Stock Movement Logs)")
        ok_mov, mov_res = client.get_inventory_movements(limit=50)
        movements = extract_items(mov_res) if ok_mov else []
        st.caption(f"Total Movement Records: {len(movements)}")
        if movements:
            st.dataframe(movements, use_container_width=True)
        else:
            st.info("Belum ada catatan pergerakan stok.")


if __name__ == "__main__":
    st.set_page_config(page_title="AURA POS — Warehouse Admin Portal", page_icon="🏬", layout="wide")
    client = AuraAPIClient()
    ok, res = client.login("admin@aura.pos", "admin123")
    if not ok:
        st.error(f"⚠️ Gagal terhubung ke Backend (http://127.0.0.1:8000/api/v1): {res}")
        st.info("Pastikan server FastAPI backend sudah berjalan (`uvicorn app.main:app --reload`).")
    else:
        render_wh_admin_ui(client)
