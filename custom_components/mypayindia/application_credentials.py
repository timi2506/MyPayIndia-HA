"""Application credentials platform for MyPayIndia."""
from homeassistant.components.application_credentials import (
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2Implementation,
    LocalOAuth2ImplementationWithPkce,
)

async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server endpoints."""
    return AuthorizationServer(
        authorize_url="https://mypayindia.com/oauth/authorize",
        token_url="https://mypayindia.com/oauth/token",
    )

async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> AbstractOAuth2Implementation:
    """Return an implementation that uses PKCE S256."""
    return LocalOAuth2ImplementationWithPkce(
        hass,
        auth_domain,
        credential.client_id,
        authorize_url="https://mypayindia.com/oauth/authorize",
        token_url="https://mypayindia.com/oauth/token",
        client_secret=credential.client_secret or "",
    )
