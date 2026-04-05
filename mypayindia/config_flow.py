import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class MyPayIndiaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["username"],
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)

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

        schema = vol.Schema({
            vol.Required("username", default=self.config_entry.data.get("username")): str,
            vol.Required("password", default=self.config_entry.data.get("password")): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
