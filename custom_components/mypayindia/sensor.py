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
        if data and "balance" in data:
            # In v2, balance is returned in paisa (100 paisa = 1 INR)
            return round(float(data["balance"]) / 100, 2)
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get("info", {})
        return {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": data.get("email"),
            "username": data.get("username") or self.coordinator.username,
            "created": data.get("created"),
            "role": data.get("role"),
            "mfa_enabled": data.get("mfa_enabled"),
            "balance_paisa": data.get("balance"),
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
            amount = link.get("amount")
            if "amount_paisa" in link:
                amount_inr = link["amount"]
            else:
                amount_inr = round(float(amount) / 100, 2) if amount else 0.0

            formatted_links.append({
                "id": link.get("id"),
                "token": token,
                "amount": amount_inr,
                "amount_paisa": link.get("amount_paisa", link.get("amount")),
                "note": link.get("note"),
                "status": link.get("status"),
                "created": link.get("created"),
                "claim_url": link.get("claim_url") or link.get("url") or (
                    f"https://mypayindia.com/pay/link?token={token}" if token else None
                ),
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
            sender_name = txn.get("sender_name")
            if not sender_name and isinstance(txn.get("sender"), dict):
                sender_name = txn["sender"].get("username")
            if sender_name == self.coordinator.username:
                amount = txn.get("amount", 0)
                if "amount_paisa" not in txn and amount > 0:
                    amount = amount / 100
                total += float(amount)
        return round(total, 2)

    @property
    def extra_state_attributes(self):
        txns = self.coordinator.data.get("transactions", [])
        return {"transactions": txns}