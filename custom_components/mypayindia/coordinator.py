import logging
import requests
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ConfigEntryAuthFailed

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://mypayindia.com/api/v2"

class MyPayIndiaCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass,
        username,
        password=None,
        totp_code=None,
        session_id=None,
        auth_method="password",
        entry=None,
    ):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="MyPayIndia Coordinator",
            update_interval=timedelta(minutes=5),
        )
        self.username = username
        self.password = password
        self.totp_code = totp_code
        self.session_id = session_id
        self.auth_method = auth_method
        self.entry = entry
        self.session = requests.Session()
        if self.session_id:
            self.session.headers.update({"Authorization": f"Bearer {self.session_id}"})
        self.transfer_amount = 0.0
        self.transfer_recipient = ""
        self.transfer_note = ""

    def login(self, force=False):
        if self.session_id and not force:
            return True

        if self.auth_method == "oauth":
            _LOGGER.warning("MyPayIndia OAuth session has expired or is invalid.")
            return False

        if not self.username or not self.password:
            _LOGGER.error("MyPayIndia username and password are required for password auth.")
            return False

        payload = {
            "username": self.username,
            "password": self.password,
        }
        if self.totp_code:
            payload["totp_code"] = str(self.totp_code)

        try:
            resp = self.session.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
            res_data = resp.json()
            if res_data.get("success"):
                session_id = res_data.get("data", {}).get("session_id")
                if session_id:
                    self.session_id = session_id
                    self.session.headers.update({"Authorization": f"Bearer {self.session_id}"})
                return True
            else:
                _LOGGER.error(
                    "MyPayIndia login failed: %s (error code: %s)",
                    res_data.get("message"),
                    res_data.get("error"),
                )
                return False
        except Exception as e:
            _LOGGER.error("MyPayIndia login error: %s", e)
            return False

    def _request(self, method, endpoint, **kwargs):
        if not self.login():
            if self.auth_method == "oauth":
                raise ConfigEntryAuthFailed("MyPayIndia OAuth session expired. Please re-authenticate.")

        url = f"{BASE_URL}{endpoint}"
        try:
            resp = self.session.request(method, url, timeout=15, **kwargs)
            if resp.status_code == 401:
                _LOGGER.debug("401 from %s, attempting re-authentication...", endpoint)
                if self.login(force=True):
                    resp = self.session.request(method, url, timeout=15, **kwargs)
                elif self.auth_method == "oauth":
                    raise ConfigEntryAuthFailed("MyPayIndia OAuth session expired. Please re-authenticate.")
            return resp.json()
        except ConfigEntryAuthFailed:
            raise
        except Exception as e:
            _LOGGER.error("Error during request to %s: %s", url, e)
            return {"success": False, "error": str(e)}

    async def _async_update_data(self):
        def fetch():
            data = {}

            # Fetch user profile & balance
            info_resp = self._request("GET", "/user/info")
            if info_resp.get("success"):
                data["info"] = info_resp.get("data", {})
            elif info_resp.get("error") == 1001 and self.auth_method == "oauth":
                raise ConfigEntryAuthFailed("Authentication failed: session invalid.")

            # Fetch transaction history
            txn_resp = self._request("GET", "/transaction/list")
            if txn_resp.get("success"):
                raw_txns = txn_resp.get("data", {}).get("transactions", [])
                formatted_txns = []
                for txn in raw_txns:
                    t = dict(txn)
                    sender = txn.get("sender")
                    recipient = txn.get("recipient")
                    t["sender_name"] = (
                        sender.get("username") if isinstance(sender, dict) else txn.get("sender_name", "")
                    )
                    t["target_name"] = (
                        recipient.get("username")
                        if isinstance(recipient, dict)
                        else (recipient if isinstance(recipient, str) else txn.get("target_name", ""))
                    )
                    amount_paisa = txn.get("amount", 0)
                    t["amount_paisa"] = amount_paisa
                    t["amount"] = round(amount_paisa / 100, 2)
                    formatted_txns.append(t)
                data["transactions"] = formatted_txns

            # Fetch active payment links
            links_resp = self._request("GET", "/payment-link/list")
            if links_resp.get("success"):
                raw_links = links_resp.get("data", {}).get("links", [])
                formatted_links = []
                for link in raw_links:
                    l = dict(link)
                    amount_paisa = link.get("amount", 0)
                    l["amount_paisa"] = amount_paisa
                    l["amount"] = round(amount_paisa / 100, 2)
                    token = link.get("token", "")
                    l["claim_url"] = link.get("url") or (
                        f"https://mypayindia.com/pay/link?token={token}" if token else None
                    )
                    formatted_links.append(l)
                data["payment_links"] = formatted_links

            return data

        return await self.hass.async_add_executor_job(fetch)

    def transfer(self, amount, recipient, note=""):
        try:
            amt = float(amount)
        except (ValueError, TypeError):
            amt = 0.0
        amount_paisa = int(round(amt * 100))
        recip = (
            int(recipient)
            if isinstance(recipient, int) or (isinstance(recipient, str) and recipient.isdigit())
            else str(recipient)
        )
        payload = {"amount": amount_paisa, "recipient": recip, "note": str(note or "")}
        return self._request("POST", "/transaction/transfer", json=payload)

    def create_payment_link(self, amount, note=""):
        try:
            amt = float(amount)
        except (ValueError, TypeError):
            amt = 0.0
        amount_paisa = int(round(amt * 100))
        payload = {"amount": amount_paisa, "note": str(note or "")}
        return self._request("POST", "/payment-link/create", json=payload)

    def claim_payment_link(self, token):
        payload = {"token": str(token).strip()}
        return self._request("POST", "/payment-link/claim", json=payload)

    def cancel_payment_link(self, token):
        payload = {"token": str(token).strip()}
        return self._request("POST", "/payment-link/cancel", json=payload)