from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import MyPayIndiaCoordinator
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = MyPayIndiaCoordinator(
        hass,
        entry.data["username"],
        entry.data["password"],
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        MyPayIndiaBalanceSensor(coordinator)
    ])


class MyPayIndiaBalanceSensor(CoordinatorEntity, Entity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyPayIndia Balance"
        self._attr_unique_id = "mypayindia_balance"

    @property
    def state(self):
        data = self.coordinator.data
        if data:
            return float(data.get("balance", 0))
        return None
