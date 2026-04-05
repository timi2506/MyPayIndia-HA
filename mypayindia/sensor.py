from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        MyPayIndiaBalanceSensor(coordinator),
        MyPayIndiaPaymentLinksSummarySensor(coordinator),
        MyPayIndiaTotalTransferredSensor(coordinator)
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
            "username": self.coordinator.username,
            "created": data.get("created"),
        }


class MyPayIndiaPaymentLinksSummarySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyPayIndia Total Active Links"
        self._attr_unique_id = f"{coordinator.username}_links_summary"

    @property
    def native_value(self):
        links = self.coordinator.data.get("payment_links", [])
        return len(links)

    @property
    def extra_state_attributes(self):
        links = self.coordinator.data.get("payment_links", [])
        formatted_links = []
        for link in links:
            token = link.get("token", "")
            formatted_links.append({
                "id": link.get("id"),
                "token": token,
                "amount": link.get("amount"),
                "note": link.get("note"),
                "status": link.get("status"),
                "created": link.get("created"),
                "claim_url": f"https://mypayindia.com/pay/link?token={token}" if token else None
            })
        return {"links": formatted_links}


class MyPayIndiaTotalTransferredSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyPayIndia Total Transferred"
        self._attr_unique_id = f"{coordinator.username}_total_transferred"
        self._attr_native_unit_of_measurement = "INR"

    @property
    def native_value(self):
        txns = self.coordinator.data.get("transactions", [])
        total = 0.0
        for txn in txns:
            if txn.get("sender_name") == self.coordinator.username:
                total += float(txn.get("amount", 0))
        return round(total, 2)

    @property
    def extra_state_attributes(self):
        txns = self.coordinator.data.get("transactions", [])
        return {"transactions": txns}