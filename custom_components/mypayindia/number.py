from homeassistant.components.number import NumberEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        MyPayIndiaAmountNumber(coordinator)
    ])

class MyPayIndiaAmountNumber(NumberEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "MyPayIndia Transfer Amount"
        self._attr_unique_id = f"{coordinator.username}_transfer_amount"
        self._attr_native_value = 0.0
        self._attr_native_step = 0.01
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 1000000.0

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.coordinator.transfer_amount = value
        self.async_write_ha_state()