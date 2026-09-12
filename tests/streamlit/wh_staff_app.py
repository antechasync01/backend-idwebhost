"""Warehouse Staff Mobile / Desktop App UI — Streamlit Application.

Run standalone with:
    uv run streamlit run tests/streamlit/wh_staff_app.py
"""

import sys
from pathlib import Path

# Add current directory to sys.path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from api_client import AuraAPIClient, extract_items


def render_wh_staff_ui(client: AuraAPIClient):
    st.markdown("## 📦 Staf Gudang Operational App")
    st.caption("Aplikasi Operasional Staf Gudang AURA — Scan Barcode, Pengajuan Produk Baru, Penerimaan Fisik, dan Replenish Display")

    tab_scan, tab_register, tab_receiving, tab_replenish, tab_wh_req = st.tabs(
        ["🔍 Scan & Lookup Stok", "📝 Pengajuan Produk Baru", "🚚 Fisik Penerimaan Barang", "⚡ Replenish Rak Display", "📋 Permintaan Gudang"]
    )

    # Fetch inventory data for live stock lookup
    ok_inv, inv_res = client.get_inventory()
    inv_list = extract_items(inv_res) if ok_inv else []

    # Map product GTIN -> inventory details
    gtin_inv_map = {}
    for inv_item in inv_list:
        gtin = inv_item.get("gtin") or (inv_item.get("product", {}).get("gtin") if isinstance(inv_item.get("product"), dict) else None)
        p_name = inv_item.get("product_name") or (inv_item.get("product", {}).get("name") if isinstance(inv_item.get("product"), dict) else None)
        if gtin:
            gtin_inv_map[gtin] = {
                "display": inv_item.get("display_quantity", 0),
                "on_hand": inv_item.get("on_hand_quantity", 0),
                "total": inv_item.get("total_available", 0),
                "name": p_name,
            }

    # ---------------- TAB 1: SCAN & LOOKUP ----------------
    with tab_scan:
        st.subheader("Cari / Scan Barcode GTIN Produk")
        scan_gtin = st.text_input("Input Barcode GTIN (EAN-13)", value="8998888110015", key="staff_gtin_lookup")
        
        if scan_gtin and scan_gtin.strip():
            ok, p_res = client.list_products(query=scan_gtin.strip())
            items = extract_items(p_res) if ok else []
            if items:
                prod = items[0]
                gtin_val = prod['gtin']
                st.success(f"Ditemukan Produk: **{prod['name']}** ({prod.get('brand') or 'General'})")
                
                inv_info = gtin_inv_map.get(gtin_val, {"display": 0, "on_hand": 0, "total": 0})
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Stok Display (Rak Toko)", f"{inv_info['display']} pcs")
                c2.metric("Stok On-Hand (Gudang)", f"{inv_info['on_hand']} pcs")
                c3.metric("Total Ketersediaan", f"{inv_info['total']} pcs")

                st.write(f"- **GTIN Barcode**: `{prod['gtin']}`")
                st.write(f"- **Satuan Unit**: {prod['unit']}")
                st.write(f"- **Harga Beli (Modal)**: Rp {prod.get('purchase_price', 0):,.2f}")
                st.write(f"- **Harga Jual (Retail)**: Rp {prod.get('selling_price', 0):,.2f}")
            else:
                st.warning(f"GTIN '{scan_gtin}' belum terdaftar di Katalog Master.")

    # ---------------- TAB 2: REGISTER NEW PRODUCT REQUEST ----------------
    with tab_register:
        st.subheader("Form Pengajuan Pendaftaran Produk Baru")
        st.info("Produk baru yang ditemukan saat unboxing akan diajukan ke Admin Gudang untuk disetujui.")
        
        with st.form("form_staff_register"):
            r_gtin = st.text_input("GTIN Barcode", "8991234567890")
            r_name = st.text_input("Nama Usulan Produk", "Pop Mie Rasa Baso Special 75g")
            r_unit = st.selectbox("Satuan", ["pcs", "pack", "box"])
            r_purchase = st.number_input("Estimasi Harga Beli", value=4500.0, step=500.0)
            r_selling = st.number_input("Estimasi Harga Jual", value=6000.0, step=500.0)
            btn_sub_reg = st.form_submit_button("Submit Pengajuan Produk")

            if btn_sub_reg:
                payload = {
                    "gtin": r_gtin.strip(),
                    "suggested_name": r_name.strip(),
                    "suggested_unit": r_unit,
                    "suggested_purchase_price": r_purchase,
                    "suggested_selling_price": r_selling,
                }
                ok_r, res_r = client.submit_product_registration(payload)
                if ok_r:
                    st.success(f"Pengajuan produk '{r_name}' berhasil dikirim ke Admin Gudang!")
                else:
                    st.error(f"Gagal mengajukan produk: {res_r}")

    # ---------------- TAB 3: RECEIVING SUBMISSION ----------------
    with tab_receiving:
        st.subheader("Pengajuan Form Penerimaan Barang Fisik")
        ok_p, p_res = client.list_products()
        prods = extract_items(p_res) if ok_p else []
        prod_dict = {f"{p['name']} (GTIN: {p['gtin']})": p['id'] for p in prods}

        if prod_dict:
            sel_p_name = st.selectbox("Pilih Produk Diterima", list(prod_dict.keys()), key="staff_rec_prod")
            rec_qty = st.number_input("Kuantitas Diterima (pcs)", min_value=1, value=50)
            rec_notes = st.text_input("Catatan Pengiriman / Surat Jalan", "Diterima dari Truk Supplier A", key="staff_rec_notes")

            if st.button("📦 Submit Penerimaan Fisik Barang"):
                pid = prod_dict[sel_p_name]
                items_payload = [{"product_id": pid, "quantity_received": rec_qty}]
                ok_sub, res_sub = client.submit_receiving(supplier_id=None, items=items_payload, notes=rec_notes)
                if ok_sub:
                    st.success("Dokumen penerimaan barang fisik berhasil diajukan!")
                else:
                    st.error(f"Gagal submit penerimaan: {res_sub}")
        else:
            st.info("Katalog produk belum tersedia.")

    # ---------------- TAB 4: REPLENISH DISPLAY ----------------
    with tab_replenish:
        st.subheader("Pindahkan Stok dari Gudang Belakang (ON_HAND) ke Rak Toko (DISPLAY)")
        
        inv_dict = {}
        for item in inv_list:
            p_name = item.get("product_name") or (item.get("product", {}).get("name") if isinstance(item.get("product"), dict) else None)
            pid = item.get("product_id")
            oh = item.get("on_hand_quantity", 0)
            if pid and p_name:
                inv_dict[f"{p_name} (Stok On-Hand: {oh} pcs)"] = pid

        # Fallback to Product catalog if needed
        if not inv_dict and prod_dict:
            inv_dict = prod_dict

        if inv_dict:
            rep_p_name = st.selectbox("Pilih Produk Replenish", list(inv_dict.keys()), key="rep_p")
            rep_qty = st.number_input("Jumlah Pindah ke Display", min_value=1, value=10, key="rep_qty")
            if st.button("🚀 Replenish Ke Display Toko"):
                target_pid = inv_dict[rep_p_name]
                ok_rep, res_rep = client.transfer_inventory(target_pid, "ON_HAND", "DISPLAY", rep_qty)
                if ok_rep:
                    st.success(f"Berhasil memindahkan {rep_qty} pcs ke display toko!")
                    st.rerun()
                else:
                    st.error(f"Gagal transfer replenish: {res_rep}")
        else:
            st.info("Data stok inventori tidak ditemukan.")

    # ---------------- TAB 5: WAREHOUSE REQUEST ----------------
    with tab_wh_req:
        st.subheader("Permintaan Barang Dari Gudang Belakang (Warehouse Request)")
        if prod_dict:
            req_p_name = st.selectbox("Pilih Produk Diminta", list(prod_dict.keys()), key="wh_req_p")
            req_p_qty = st.number_input("Jumlah Kuantitas Diminta", min_value=1, value=20, key="wh_req_qty")
            req_notes = st.text_input("Alasan Permintaan", "Stok Rak Toko Hampir Habis", key="wh_req_notes")
            if st.button("📨 Kirim Form Permintaan Gudang"):
                target_pid = prod_dict[req_p_name]
                ok_wr, res_wr = client.create_warehouse_request(items=[{"product_id": target_pid, "quantity_requested": req_p_qty}], notes=req_notes)
                if ok_wr:
                    st.success("Permintaan gudang berhasil dibuat!")
                else:
                    st.error(f"Gagal buat permintaan gudang: {res_wr}")


if __name__ == "__main__":
    st.set_page_config(page_title="AURA POS — Warehouse Staff App", page_icon="📦", layout="wide")
    client = AuraAPIClient()
    ok, res = client.login("staff@aura.pos", "staff123")
    if not ok:
        st.error(f"⚠️ Gagal terhubung ke Backend (http://127.0.0.1:8000/api/v1): {res}")
        st.info("Pastikan server FastAPI backend sudah berjalan (`uvicorn app.main:app --reload`).")
    else:
        render_wh_staff_ui(client)
