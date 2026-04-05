from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        MyPayIndiaBalanceSensor(coordinator),
        MyPayIndiaLatestTransactionSensor(coordinator),
        MyPayIndiaPaymentLinksSensor(coordinator)
    ])

class MyPayIndiaBalanceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyPayIndia Balance"
        self._attr_unique_id = f"{coordinator.username}_balance"
        self._attr_native_unit_of_measurement = "INR"

    @property
    def native_value(self):
        data = self.coordinator.data.get("info", {})
        if data:
            return float(data.get("balance", 0))
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get("info", {})
        return {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": data.get("email"),
            "created": data.get("created"),
        }

class MyPayIndiaLatestTransactionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyPayIndia Latest Transaction"
        self._attr_unique_id = f"{coordinator.username}_latest_txn"
        self._attr_native_unit_of_measurement = "INR"

    @property
    def native_value(self):
        txns = self.coordinator.data.get("transactions", [])
        if txns:
            return float(txns[0].get("amount", 0))
        return None

    @property
    def extra_state_attributes(self):
        txns = self.coordinator.data.get("transactions", [])
        if txns:
            txn = txns[0]
            return {
                "transaction_id": txn.get("transaction_id"),
                "sender": txn.get("sender_name"),
                "target": txn.get("target_name"),
                "status": txn.get("status"),
                "date": txn.get("created")
            }
        return {}

class MyPayIndiaPaymentLinksSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyPayIndia Active Payment Links"
        self._attr_unique_id = f"{coordinator.username}_payment_links"

    @property
    def native_value(self):
        links = self.coordinator.data.get("payment_links", [])
        return len(links)