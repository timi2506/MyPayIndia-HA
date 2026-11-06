import logging
from typing import Any
import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://mypayindia.com/api/v2"

class MyPayIndiaConfigFlow(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler,
    domain=DOMAIN,
):
    """Handle a config flow for MyPayIndia (supports OAuth2 and credentials)."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "scope": "openid session",
        }

    async def async_step_user(self, user_input=None):
        """Handle the initial step - choose between OAuth2 and Credentials."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_show_menu(
            step_id="user",
            menu_options=["oauth", "credentials"],
        )

    async def async_step_oauth(self, user_input=None):
        """Handle OAuth setup path."""
        return await self.async_step_pick_implementation(user_input)

    async def async_step_credentials(self, user_input=None):
        """Handle manual username/password setup path."""
        errors = {}

        if user_input is not None:
            # Validate credentials against v2 login endpoint
            try:
                def validate():
                    payload = {
                        "username": user_input["username"],
                        "password": user_input["password"],
                    }
                    if user_input.get("totp_code"):
                        payload["totp_code"] = str(user_input["totp_code"])
                    resp = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=10)
                    return resp.json()

                res_data = await self.hass.async_add_executor_job(validate)
                if res_data.get("success"):
                    session_id = res_data.get("data", {}).get("session_id")
                    username = res_data.get("data", {}).get("user", {}).get(
                        "username", user_input["username"]
                    )
                    return self.async_create_entry(
                        title=username,
                        data={
                            **user_input,
                            "session_id": session_id,
                            "username": username,
                            "auth_method": "password",
                        },
                    )
                else:
                    err_code = res_data.get("error")
                    if err_code in (1002, 1010):
                        errors["base"] = "invalid_2fa"
                    elif err_code == 1005:
                        errors["base"] = "invalid_auth"
                    elif err_code == 1016:
                        errors["base"] = "password_auth_disabled"
                    else:
                        errors["base"] = "cannot_connect"
            except Exception as e:
                _LOGGER.error("Error validating credentials: %s", e)
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
            vol.Optional("totp_code", default=""): str,
        })

        return self.async_show_form(
            step_id="credentials",
            data_schema=schema,
            errors=errors,
        )

    async def async_oauth_create_entry(self, data: dict[str, Any]):
        """Create entry after OAuth token exchange, trading token for v2 session."""
        access_token = data.get("token", {}).get("access_token")
        if not access_token:
            return self.async_abort(reason="oauth_error")

        def exchange():
            resp = requests.post(
                f"{BASE_URL}/auth/oauth",
                json={"access_token": access_token},
                timeout=10,
            )
            return resp.json()

        try:
            res_data = await self.hass.async_add_executor_job(exchange)
            if not res_data.get("success"):
                _LOGGER.error("Failed to exchange OAuth token for API v2 session: %s", res_data)
                return self.async_abort(reason="oauth_error")

            session_id = res_data.get("data", {}).get("session_id")
            user_info = res_data.get("data", {}).get("user", {})
            username = user_info.get("username", "MyPayIndia User")

            return self.async_create_entry(
                title=username,
                data={
                    **data,
                    "session_id": session_id,
                    "username": username,
                    "auth_method": "oauth",
                },
            )
        except Exception as e:
            _LOGGER.error("Exception during OAuth exchange: %s", e)
            return self.async_abort(reason="cannot_connect")

    async def async_step_reauth(self, entry_data: dict[str, Any]):
        """Perform reauth upon an authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Confirm reauth dialog."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MyPayIndiaOptionsFlowHandler(config_entry)


class MyPayIndiaOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input
            )
            return self.async_create_entry(title="", data={})

        if self.config_entry.data.get("auth_method") == "oauth":
            return self.async_show_form(step_id="init", data_schema=vol.Schema({}))

        schema = vol.Schema({
            vol.Required("username", default=self.config_entry.data.get("username", "")): str,
            vol.Required("password", default=self.config_entry.data.get("password", "")): str,
            vol.Optional("totp_code", default=self.config_entry.data.get("totp_code", "")): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)