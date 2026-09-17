"""Cashier POS Terminal & Cash Closing UI — Streamlit Application.

Run standalone with:
    uv run streamlit run tests/streamlit/cashier_app.py
"""

import sys
from pathlib import Path

# Add current directory to sys.path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uuid
import streamlit as st
from api_client import AuraAPIClient, extract_items


def render_cashier_ui(client: AuraAPIClient):
    # Check Attendance Status
    ok, att_status = client.get_attendance_status()
    if ok and isinstance(att_status, dict) and not att_status.get("is_clocked_in"):
        st.markdown("## 🛑 Akses Terkunci (Clock-Out)")
        st.warning("Anda saat ini sedang dalam status Clock-Out. Silakan mulai shift (Clock-in) untuk dapat mengakses sistem kasir.")
        if st.button("▶️ Mulai Shift (Clock-In)", type="primary"):
            ok_in, res_in = client.clock_in()
            if ok_in:
                st.success("Berhasil clock-in! Memuat ulang sistem...")
                st.rerun()
            else:
                st.error(f"Gagal clock-in: {res_in}")
        return

    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("## 🛒 Kasir Toko POS Terminal")
        st.caption("Aplikasi Kasir AURA POS — Transaksi Kasir, Cetak Struk, Void/Refund & Penutupan Kas Harian")
    with c2:
        st.write("")
        if st.button("⏹️ Akhiri Shift (Clock-Out)"):
            ok_out, res_out = client.clock_out()
            if ok_out:
                st.success("Berhasil clock-out! Menutup akses...")
                st.rerun()
            else:
                st.error(f"Gagal clock-out: {res_out}")

    tab_pos, tab_receipt, tab_closing = st.tabs(["💳 POS Terminal Transaksi", "🧾 Cetak Struk & Void/Refund", "💰 Cash Closing Harian"])

    # Initialize Cart state
    if "cart" not in st.session_state:
        st.session_state["cart"] = []

    # ---------------- TAB 1: POS TERMINAL ----------------
    with tab_pos:
        col_catalog, col_cart = st.columns([3, 2])

        # Left Column: Product Search & Add to Cart
        with col_catalog:
            st.subheader("Katalog Produk POS")
            pos_search = st.text_input("Scan Barcode GTIN / Cari Nama Produk", key="pos_search")
            
            ok_p, p_res = client.list_products(query=pos_search.strip() if pos_search and pos_search.strip() else None)
            prods = extract_items(p_res) if ok_p else []

            # Also fetch inventory display quantities for real-time stock status
            ok_inv, inv_res = client.get_inventory()
            inv_items = extract_items(inv_res) if ok_inv else []
            inv_map = {item.get("product_id"): item.get("display_quantity", 0) for item in inv_items if item.get("product_id")}

            if prods:
                for prod in prods:
                    pid = prod["id"]
                    disp_qty = inv_map.get(pid, 0)
                    with st.container():
                        st.markdown(f"**{prod['name']}** ({prod.get('brand') or 'General'})")
                        st.write(f"GTIN: `{prod['gtin']}` | Harga: **Rp {prod['selling_price']:,.2f}** | Stok Display: **{disp_qty} pcs**")
                        
                        col_qty, col_btn = st.columns([1, 2])
                        with col_qty:
                            qty_add = st.number_input("Qty", min_value=1, value=1, key=f"qty_{pid}")
                        with col_btn:
                            st.write("")
                            if st.button("➕ Tambah Ke Keranjang", key=f"add_{pid}"):
                                existing_item = next((item for item in st.session_state["cart"] if item["product_id"] == pid), None)
                                if existing_item:
                                    existing_item["quantity"] += qty_add
                                else:
                                    st.session_state["cart"].append({
                                        "product_id": pid,
                                        "name": prod["name"],
                                        "gtin": prod["gtin"],
                                        "unit_price": prod["selling_price"],
                                        "quantity": qty_add,
                                    })
                                st.success(f"Ditambahkan {qty_add} pcs {prod['name']} ke keranjang!")
                                st.rerun()
                        st.divider()
            else:
                st.info("Produk tidak ditemukan.")

        # Right Column: Active Cart & Checkout
        with col_cart:
            st.subheader("🛒 Keranjang Belanja Active")
            cart_items = st.session_state["cart"]

            if cart_items:
                total_checkout = 0.0
                for idx, item in enumerate(cart_items):
                    subtotal = item["unit_price"] * item["quantity"]
                    total_checkout += subtotal
                    
                    c_info, c_del = st.columns([4, 1])
                    with c_info:
                        st.write(f"**{item['name']}** (`{item['gtin']}`)")
                        st.write(f"{item['quantity']} pcs x Rp {item['unit_price']:,.2f} = **Rp {subtotal:,.2f}**")
                    with c_del:
                        if st.button("❌", key=f"remove_{idx}"):
                            st.session_state["cart"].pop(idx)
                            st.rerun()
                    st.divider()

                st.markdown(f"### Total Belanja: **Rp {total_checkout:,.2f}**")

                cash_paid = st.number_input("Nominal Uang Tunai (Cash Paid)", min_value=0.0, value=float(total_checkout), step=5000.0)
                cash_change = cash_paid - total_checkout

                if cash_change >= 0:
                    st.success(f"Kembalian Kasir: **Rp {cash_change:,.2f}**")
                else:
                    st.error(f"Uang kurang: Rp {abs(cash_change):,.2f}")

                col_checkout, col_clear = st.columns(2)
                with col_checkout:
                    if st.button("💳 Selesaikan Transaksi", type="primary"):
                        if cash_paid < total_checkout:
                            st.error("Uang tunai kurang dari total belanja!")
                        else:
                            items_payload = [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in cart_items]
                            idempotency_key = str(uuid.uuid4())
                            ok_sale, sale_res = client.create_sale(
                                items=items_payload,
                                payment_method="CASH",
                                cash_paid=cash_paid,
                                idempotency_key=idempotency_key
                            )
                            if ok_sale and isinstance(sale_res, dict):
                                st.balloons()
                                st.success(f"Transaksi Sukses! Struk No: **{sale_res.get('receipt_number')}**")
                                st.info(f"Total: Rp {sale_res.get('total_amount', 0):,.2f} | Kembalian: Rp {sale_res.get('cash_change', 0):,.2f}")
                                st.session_state["last_receipt"] = sale_res.get('receipt_number')
                                st.session_state["cart"] = []
                                if st.button("Mulai Transaksi Baru", key="new_sale_btn"):
                                    st.rerun()
                            else:
                                st.error(f"Gagal memproses transaksi: {sale_res}")

                with col_clear:
                    if st.button("🗑️ Kosongkan Keranjang"):
                        st.session_state["cart"] = []
                        st.rerun()

            else:
                st.info("Keranjang belanja masih kosong.")

    # ---------------- TAB 2: RECEIPT LOOKUP & VOID/REFUND ----------------
    with tab_receipt:
        st.subheader("Cari Struk Transaksi & Pembatalan / Refund")
        receipt_no_in = st.text_input("Nomor Struk (mis. REC-20260906-XXXX)", value=st.session_state.get("last_receipt", ""))
        
        if receipt_no_in:
            ok_rc, rc_data = client.get_sale_by_receipt(receipt_no_in.strip())
            if ok_rc and isinstance(rc_data, dict):
                st.success(f"Struk #{rc_data.get('receipt_number')} — Status: **{rc_data.get('status')}**")
                st.write(f"- **Tanggal Transaksi**: {rc_data.get('created_at')}")
                st.write(f"- **Total Amount**: Rp {rc_data.get('total_amount', 0):,.2f}")
                st.write(f"- **Cash Paid**: Rp {rc_data.get('cash_paid', 0):,.2f} | **Cash Change**: Rp {rc_data.get('cash_change', 0):,.2f}")
                
                st.write("Item Struk:")
                st.dataframe(extract_items(rc_data.get("items", [])), use_container_width=True)

                if rc_data.get("status") == "COMPLETED":
                    st.divider()
                    col_v, col_r = st.columns(2)
                    with col_v:
                        st.markdown("### Pembatalan Transaksi (Void)")
                        void_reason = st.text_input("Alasan Void", "Kesalahan Input Kasir", key="v_reason")
                        if st.button("🚫 Void Transaksi Ini", key="btn_void"):
                            ok_vd, res_vd = client.void_sale(rc_data['id'], void_reason)
                            if ok_vd:
                                st.warning("Transaksi berhasil dibatalkan (VOIDED)!")
                                st.rerun()
                            else:
                                st.error(f"Gagal void: {res_vd}")

                    with col_r:
                        st.markdown("### Pengembalian Barang (Refund)")
                        refund_reason = st.text_input("Alasan Refund", "Barang Cacat / Rusak", key="r_reason")
                        if st.button("💸 Refund Seluruh Item", key="btn_refund"):
                            ref_items = [{"sale_item_id": item['id'], "quantity": item['quantity']} for item in extract_items(rc_data.get("items", []))]
                            ok_rf, res_rf = client.refund_sale(rc_data['id'], ref_items, refund_reason)
                            if ok_rf:
                                st.success("Refund berhasil diproses!")
                                st.rerun()
                            else:
                                st.error(f"Gagal refund: {res_rf}")
            else:
                st.warning(f"Struk #{receipt_no_in} tidak ditemukan.")

    # ---------------- TAB 3: CASH CLOSING ----------------
    with tab_closing:
        st.subheader("Form Penutupan Kas Harian (Cash Closing)")
        ok_sum, sum_data = client.get_cash_summary()
        if ok_sum and isinstance(sum_data, dict):
            st.info("Estimasi Kas Toko Berdasarkan Transaksi Hari Ini:")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Modal Awal Kas", f"Rp {sum_data.get('opening_cash', 0):,.2f}")
            s2.metric("Penjualan Cash", f"Rp {sum_data.get('cash_sales', 0):,.2f}")
            s3.metric("Total Refund", f"Rp {sum_data.get('refunds', 0):,.2f}")
            s4.metric("Ekspektasi Kas Fisik", f"Rp {sum_data.get('expected_cash', 0):,.2f}")

            st.divider()
            with st.form("form_cash_closing"):
                opening_cash_in = st.number_input("Modal Awal Kas (Opening Cash)", value=float(sum_data.get("opening_cash", 100000.0)))
                actual_cash_in = st.number_input("Jumlah Uang Fisik Di Laci Kasir", value=float(sum_data.get("expected_cash", 100000.0)))
                adj_in = st.number_input("Penyesuaian Kas Manual", value=0.0)
                closing_notes_in = st.text_input("Catatan Closing Kasir", "Hitungan kas laci sesuai.")
                btn_close_cash = st.form_submit_button("Submit Penutupan Kas")

                if btn_close_cash:
                    ok_cc, res_cc = client.submit_cash_closing(
                        opening_cash=opening_cash_in,
                        actual_cash=actual_cash_in,
                        cash_adjustment=adj_in,
                        notes=closing_notes_in,
                    )
                    if ok_cc and isinstance(res_cc, dict):
                        st.success("Cash closing berhasil dikirim!")
                        st.json(res_cc)
                    else:
                        st.error(f"Gagal cash closing: {res_cc}")


if __name__ == "__main__":
    st.set_page_config(page_title="AURA POS — Cashier POS Terminal", page_icon="🛒", layout="wide")
    client = AuraAPIClient()
    ok, res = client.login("cashier@aura.pos", "cashier123")
    if not ok:
        st.error(f"⚠️ Gagal terhubung ke Backend (http://127.0.0.1:8000/api/v1): {res}")
        st.info("Pastikan server FastAPI backend sudah berjalan (`uvicorn app.main:app --reload`).")
    else:
        render_cashier_ui(client)
