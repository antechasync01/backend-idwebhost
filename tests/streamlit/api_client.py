"""AURA POS Backend API Client for Streamlit UIs.
"""

from typing import Any
import requests


def extract_items(data: Any) -> list[dict]:
    """Helper to extract a list of items regardless of whether data is a list or dict with 'items'."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "items" in data and isinstance(data["items"], list):
            return data["items"]
        if "data" in data and isinstance(data["data"], list):
            return data["data"]
    return []


import os


class AuraAPIClient:
    def __init__(self, base_url: str | None = None):
        if not base_url:
            base_url = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None
        self.user_info: dict[str, Any] | None = None


    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _parse_error(self, res: requests.Response) -> str:
        try:
            data = res.json()
            if isinstance(data, dict) and "error" in data:
                err = data["error"]
                if isinstance(err, dict):
                    msg = err.get("message")
                    code = err.get("code")
                    details = err.get("details")
                    if msg:
                        return f"[{code or 'ERROR'}] {msg}" + (f" ({details})" if details else "")
            return data.get("detail", res.text)
        except Exception:
            return f"HTTP {res.status_code}: {res.text}"

    def login(self, username_or_email: str, password: str) -> tuple[bool, str | dict]:
        url = f"{self.base_url}/auth/login"
        try:
            res = requests.post(url, json={"username_or_email": username_or_email, "password": password})
            if res.status_code == 200:
                data = res.json().get("data", {})
                self.token = data.get("access_token")
                self.user_info = data.get("user")
                return True, data
            return False, self._parse_error(res)
        except Exception as e:
            return False, f"Connection error: {e}"

    def get_me(self) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/auth/me"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Analytics ----------------
    def get_analytics_summary(self, period: str = "7d") -> tuple[bool, dict | str]:
        url = f"{self.base_url}/analytics/summary"
        try:
            res = requests.get(url, params={"period": period}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_top_products(self, limit: int = 10, period: str = "7d") -> tuple[bool, dict | str]:
        url = f"{self.base_url}/analytics/top-products"
        try:
            res = requests.get(url, params={"limit": limit, "period": period}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_inventory_health(self, low_stock_threshold: int = 10) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/analytics/inventory-health"
        try:
            res = requests.get(url, params={"low_stock_threshold": low_stock_threshold}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_sales_trend(self, period: str = "7d") -> tuple[bool, dict | str]:
        url = f"{self.base_url}/analytics/sales-trend"
        try:
            res = requests.get(url, params={"period": period}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_periodic_insights(self, period_type: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/analytics/periodic-insights"
        try:
            res = requests.get(url, params={"period_type": period_type}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Attendance ----------------
    def clock_in(self) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/attendance/clock-in"
        try:
            res = requests.post(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def clock_out(self) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/attendance/clock-out"
        try:
            res = requests.post(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_attendance_status(self) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/attendance/status"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Audit Logs ----------------
    def list_audit_logs(
        self,
        action: str | None = None,
        entity_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/audit/logs"
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if action and action.strip():
            params["action"] = action.strip()
        if entity_type and entity_type.strip():
            params["entity_type"] = entity_type.strip()

        try:
            res = requests.get(url, params=params, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Products ----------------
    def list_products(self, query: str | None = None, limit: int = 100) -> tuple[bool, list[dict] | str]:
        url = f"{self.base_url}/products"
        params: dict[str, Any] = {"limit": limit}
        if query and query.strip():
            params["query"] = query.strip()

        try:
            res = requests.get(url, params=params, headers=self._headers())
            if res.status_code == 200:
                raw_data = res.json().get("data", [])
                return True, extract_items(raw_data)
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_product_by_gtin(self, gtin: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/products/gtin/{gtin}"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def create_product(self, payload: dict) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/products"
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def submit_product_registration(self, payload: dict) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/products/register"
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def list_registration_requests(self, status: str | None = None) -> tuple[bool, list[dict] | str]:
        url = f"{self.base_url}/products/registration-requests"
        params = {}
        if status and status.strip():
            params["status"] = status.strip()
        try:
            res = requests.get(url, params=params, headers=self._headers())
            if res.status_code == 200:
                raw_data = res.json().get("data", [])
                return True, extract_items(raw_data)
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def approve_registration_request(self, request_id: str, review_notes: str = "Approved") -> tuple[bool, dict | str]:
        url = f"{self.base_url}/products/registration-requests/{request_id}/approve"
        try:
            res = requests.post(url, json={"review_notes": review_notes}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def reject_registration_request(self, request_id: str, review_notes: str = "Rejected") -> tuple[bool, dict | str]:
        url = f"{self.base_url}/products/registration-requests/{request_id}/reject"
        try:
            res = requests.post(url, json={"review_notes": review_notes}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Inventory ----------------
    def get_inventory(self) -> tuple[bool, list[dict] | str]:
        url = f"{self.base_url}/inventory"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                raw_data = res.json().get("data", [])
                return True, extract_items(raw_data)
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def transfer_inventory(self, product_id: str, from_loc: str, to_loc: str, quantity: int) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/inventory/transfer"
        direction = "ON_HAND_TO_DISPLAY" if from_loc.upper() == "ON_HAND" else "DISPLAY_TO_ON_HAND"
        payload = {
            "product_id": product_id,
            "quantity": quantity,
            "direction": direction,
        }
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def adjust_inventory(self, product_id: str, location: str, quantity_change: int, reason: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/inventory/adjust"
        payload = {
            "product_id": product_id,
            "location": location.upper(),
            "quantity_change": quantity_change,
            "reason": reason,
        }
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_inventory_movements(self, limit: int = 50) -> tuple[bool, list[dict] | str]:
        url = f"{self.base_url}/inventory/movements"
        try:
            res = requests.get(url, params={"limit": limit}, headers=self._headers())
            if res.status_code == 200:
                raw_data = res.json().get("data", [])
                return True, extract_items(raw_data)
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Warehouse Workflow ----------------
    def submit_receiving(self, supplier_id: str | None, items: list[dict], notes: str | None = None) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/warehouse/receivings"
        payload: dict[str, Any] = {"items": items}
        if supplier_id:
            payload["supplier_id"] = supplier_id
        if notes:
            payload["notes"] = notes
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def list_receivings(self, status: str | None = None) -> tuple[bool, list[dict] | str]:
        url = f"{self.base_url}/warehouse/receivings"
        params = {}
        if status and status.strip():
            params["status"] = status.strip()
        try:
            res = requests.get(url, params=params, headers=self._headers())
            if res.status_code == 200:
                raw_data = res.json().get("data", [])
                return True, extract_items(raw_data)
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def approve_receiving(self, receiving_id: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/warehouse/receivings/{receiving_id}/approve"
        try:
            res = requests.post(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def reject_receiving(self, receiving_id: str, rejection_reason: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/warehouse/receivings/{receiving_id}/reject"
        try:
            res = requests.post(url, json={"rejection_reason": rejection_reason}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def create_warehouse_request(self, items: list[dict], notes: str | None = None) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/warehouse/requests"
        payload: dict[str, Any] = {"items": items}
        if notes:
            payload["notes"] = notes
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def list_warehouse_requests(self) -> tuple[bool, list[dict] | str]:
        url = f"{self.base_url}/warehouse/requests"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                raw_data = res.json().get("data", [])
                return True, extract_items(raw_data)
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Sales & POS ----------------
    def create_sale(self, items: list[dict], payment_method: str = "CASH", cash_paid: float = 0.0, idempotency_key: str | None = None) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/sales"
        payload = {
            "items": items,
            "payment_method": payment_method,
            "cash_paid": cash_paid,
        }
        if idempotency_key:
            payload["idempotency_key"] = idempotency_key
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_sale_by_receipt(self, receipt_number: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/sales/receipt/{receipt_number}"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def void_sale(self, sale_id: str, void_reason: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/sales/{sale_id}/void"
        try:
            res = requests.post(url, json={"void_reason": void_reason}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def refund_sale(self, sale_id: str, items: list[dict], reason: str) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/sales/{sale_id}/refund"
        payload = {"items": items, "reason": reason}
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- Closing ----------------
    def get_today_closing(self) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/closing/today"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_cash_summary(self) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/closing/cash/summary"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def submit_cash_closing(self, opening_cash: float, actual_cash: float, cash_adjustment: float = 0.0, notes: str | None = None) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/closing/cash"
        payload = {
            "opening_cash": opening_cash,
            "actual_cash": actual_cash,
            "cash_adjustment": cash_adjustment,
            "notes": notes,
        }
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def submit_inventory_closing(self, physical_items: list[dict], notes: str | None = None) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/closing/inventory"
        payload: dict[str, Any] = {"physical_items": physical_items}
        if notes:
            payload["notes"] = notes
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code in (200, 201):
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def finalize_daily_closing(self, notes: str | None = None) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/closing/daily/finalize"
        payload = {"notes": notes} if notes else {}
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    # ---------------- AI & Hermes ----------------
    def get_ai_insights(self) -> tuple[bool, dict | list | str]:
        url = f"{self.base_url}/ai/insights"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", [])
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_stockout_risks(self) -> tuple[bool, dict | list | str]:
        url = f"{self.base_url}/ai/stockout-risk"
        try:
            res = requests.get(url, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", [])
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def get_demand_forecasts(self, days_ahead: int = 7) -> tuple[bool, dict | list | str]:
        url = f"{self.base_url}/ai/forecasts"
        try:
            res = requests.get(url, params={"days_ahead": days_ahead}, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", [])
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

    def send_hermes_chat(self, prompt: str, conversation_id: str | None = None) -> tuple[bool, dict | str]:
        url = f"{self.base_url}/ai/hermes/chat"
        payload = {"prompt": prompt}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        try:
            res = requests.post(url, json=payload, headers=self._headers())
            if res.status_code == 200:
                return True, res.json().get("data", {})
            return False, self._parse_error(res)
        except Exception as e:
            return False, str(e)

