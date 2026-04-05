import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN
from .coordinator import MyPayIndiaCoordinator

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry):
    coordinator = MyPayIndiaCoordinator(
        hass,
        entry.data["username"],
        entry.data["password"],
    )
    
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    async def handle_transfer(call):
        amount = call.data.get("amount")
        recipient = call.data.get("recipient")
        note = call.data.get("note", "")
        await hass.async_add_executor_job(coordinator.transfer, amount, recipient, note)

    async def handle_create_link(call):
        amount = call.data.get("amount")
        note = call.data.get("note", "")
        await hass.async_add_executor_job(coordinator.create_payment_link, amount, note)

    async def handle_claim_link(call):
        token = call.data.get("token")
        await hass.async_add_executor_job(coordinator.claim_payment_link, token)

    hass.services.async_register(DOMAIN, "transfer", handle_transfer)
    hass.services.async_register(DOMAIN, "create_payment_link", handle_create_link)
    hass.services.async_register(DOMAIN, "claim_payment_link", handle_claim_link)

    return True