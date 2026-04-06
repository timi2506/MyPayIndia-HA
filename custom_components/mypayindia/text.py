from homeassistant.components.text import TextEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MyPayIndiaRecipientText(coordinator),
        MyPayIndiaNoteText(coordinator)
    ])

class MyPayIndiaRecipientText(TextEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "MyPayIndia Transfer Recipient"
        self._attr_unique_id = f"{coordinator.username}_transfer_recipient"
        self._attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        self._attr_native_value = value
        self.coordinator.transfer_recipient = value
        self.async_write_ha_state()

class MyPayIndiaNoteText(TextEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "MyPayIndia Transfer Note"
        self._attr_unique_id = f"{coordinator.username}_transfer_note"
        self._attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        self._attr_native_value = value
        self.coordinator.transfer_note = value
        self.async_write_ha_state()