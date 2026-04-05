from homeassistant.components.button import ButtonEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MyPayIndiaSendTransferButton(coordinator)
    ])

class MyPayIndiaSendTransferButton(ButtonEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "MyPayIndia Send Transfer"
        self._attr_unique_id = f"{coordinator.username}_send_transfer"
        self._attr_icon = "mdi:send"

    async def async_press(self) -> None:
        amount = self.coordinator.transfer_amount
        recipient = self.coordinator.transfer_recipient
        note = self.coordinator.transfer_note

        if recipient and amount > 0:
            await self.coordinator.hass.async_add_executor_job(
                self.coordinator.transfer, amount, recipient, note
            )
            await self.coordinator.async_request_refresh()