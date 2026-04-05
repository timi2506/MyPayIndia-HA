import logging
import requests
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

LOGIN_URL = "https://mypayindia.com/api/v1/login"
INFO_URL = "https://mypayindia.com/api/v1/info"


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

    def login(self):
        self.session.post(
            LOGIN_URL,
            json={"username": self.username, "password": self.password},
        )

    async def _async_update_data(self):
        def fetch():
            self.login()
            response = self.session.get(INFO_URL)
            return response.json()

        return await self.hass.async_add_executor_job(fetch)