import voluptuous as vol
from pathlib import Path
from homeassistant.core import HomeAssistant
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.frontend import add_extra_js_url
from .const import DOMAIN
from .coordinator import MyPayIndiaCoordinator

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry):
    coordinator = MyPayIndiaCoordinator(
        hass,
        entry.data.get("username"),
        entry.data.get("password"),
    )
    
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    files_path = Path(__file__).parent / "www"
    await hass.http.async_register_static_paths([
        StaticPathConfig("/mypayindia_static", str(files_path), True)
    ])

    add_extra_js_url(hass, "/mypayindia_static/mypayindia-card.js")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    async def handle_transfer(call):
        amount = call.data.get("amount")
        recipient = call.data.get("recipient")
        note = call.data.get("note", "")
        await hass.async_add_executor_job(coordinator.transfer, amount, recipient, note)
        await coordinator.async_request_refresh()

    async def handle_create_link(call):
        amount = call.data.get("amount")
        note = call.data.get("note", "")
        await hass.async_add_executor_job(coordinator.create_payment_link, amount, note)
        await coordinator.async_request_refresh()

    async def handle_claim_link(call):
        token = call.data.get("token")
        await hass.async_add_executor_job(coordinator.claim_payment_link, token)
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "transfer", handle_transfer)
    hass.services.async_register(DOMAIN, "create_payment_link", handle_create_link)
    hass.services.async_register(DOMAIN, "claim_payment_link", handle_claim_link)

    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def update_listener(hass: HomeAssistant, entry):
    await hass.config_entries.async_reload(entry.entry_id)