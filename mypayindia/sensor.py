from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        MyPayIndiaBalanceSensor(coordinator),
        MyPayIndiaPaymentLinksSummarySensor(coordinator)
    ]

    for i in range(5):
        entities.append(MyPayIndiaTransactionSensor(coordinator, i))

    for i in range(5):
        entities.append(MyPayIndiaPaymentLinkSensor(coordinator, i))

    async_add_entities(entities)


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


class MyPayIndiaTransactionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, index):
        super().__init__(coordinator)
        self.index = index
        self._attr_name = f"MyPayIndia Transaction {index + 1}"
        self._attr_unique_id = f"{coordinator.username}_txn_{index}"

    @property
    def available(self):
        return super().available and len(self.coordinator.data.get("transactions", [])) > self.index

    @property
    def native_value(self):
        txns = self.coordinator.data.get("transactions", [])
        if len(txns) > self.index:
            txn = txns[self.index]
            amount = txn.get("amount", 0)
            sender = txn.get("sender_name")
            target = txn.get("target_name")
            
            if sender == self.coordinator.username:
                return f"-{amount} INR (To: {target})"
            return f"+{amount} INR (From: {sender})"
        return None

    @property
    def extra_state_attributes(self):
        txns = self.coordinator.data.get("transactions", [])
        if len(txns) > self.index:
            txn = txns[self.index]
            return {
                "id": txn.get("id"),
                "transaction_id": txn.get("transaction_id"),
                "sender_id": txn.get("sender_id"),
                "target_id": txn.get("target_id"),
                "sender_name": txn.get("sender_name"),
                "target_name": txn.get("target_name"),
                "status": txn.get("status"),
                "date": txn.get("created"),
                "amount": txn.get("amount")
            }
        return {}


class MyPayIndiaPaymentLinksSummarySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "MyPayIndia Total Active Links"
        self._attr_unique_id = f"{coordinator.username}_links_summary"

    @property
    def native_value(self):
        links = self.coordinator.data.get("payment_links", [])
        return len(links)


class MyPayIndiaPaymentLinkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, index):
        super().__init__(coordinator)
        self.index = index
        self._attr_name = f"MyPayIndia Payment Link {index + 1}"
        self._attr_unique_id = f"{coordinator.username}_link_{index}"

    @property
    def available(self):
        return super().available and len(self.coordinator.data.get("payment_links", [])) > self.index

    @property
    def native_value(self):
        links = self.coordinator.data.get("payment_links", [])
        if len(links) > self.index:
            link = links[self.index]
            amount = link.get("amount", 0)
            status = link.get("status", "Unknown")
            return f"{amount} INR ({status})"
        return None

    @property
    def extra_state_attributes(self):
        links = self.coordinator.data.get("payment_links", [])
        if len(links) > self.index:
            link = links[self.index]
            token = link.get("token", "")
            return {
                "id": link.get("id"),
                "token": token,
                "amount": link.get("amount"),
                "note": link.get("note"),
                "status": link.get("status"),
                "created": link.get("created"),
                "claim_url": f"https://mypayindia.com/pay/link?token={token}" if token else None
            }
        return {}
