import logging
import requests
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://mypayindia.com/api/v1"

class MyPayIndiaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, username, password):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="MyPayIndia Coordinator",
            update_interval=timedelta(minutes=5),
        )
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.transfer_amount = 0.0
        self.transfer_recipient = ""
        self.transfer_note = ""

    def login(self):
        self.session.post(
            f"{BASE_URL}/login",
            json={"username": self.username, "password": self.password},
        )

    async def _async_update_data(self):
        def fetch():
            self.login()
            data = {}
            
            info_resp = self.session.get(f"{BASE_URL}/info").json()
            if info_resp.get("success"):
                data["info"] = info_resp

            txn_resp = self.session.get(f"{BASE_URL}/transaction_history").json()
            if txn_resp.get("success"):
                data["transactions"] = txn_resp.get("data", [])

            links_resp = self.session.get(f"{BASE_URL}/list_payment_links").json()
            if links_resp.get("success"):
                links_data = links_resp.get("data")
                if isinstance(links_data, dict):
                    data["payment_links"] = links_data.get("links", [])
                elif isinstance(links_data, list) and len(links_data) > 0 and isinstance(links_data[0], dict):
                    data["payment_links"] = links_data[0].get("links", [])
                else:
                    data["payment_links"] = []

            return data

        return await self.hass.async_add_executor_job(fetch)

    def transfer(self, amount, recipient, note=""):
        self.login()
        payload = {"amount": str(amount), "recipient": recipient, "note": note}
        return self.session.post(f"{BASE_URL}/transfer", json=payload).json()

    def create_payment_link(self, amount, note=""):
        self.login()
        payload = {"amount": float(amount), "note": note}
        return self.session.post(f"{BASE_URL}/create_payment_link", json=payload).json()

    def claim_payment_link(self, token):
        self.login()
        return self.session.get(f"{BASE_URL}/claim_payment_link?token={token}").json()