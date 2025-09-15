import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .api import KenterAPI

class KenterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = KenterAPI(user_input["client_id"], user_input["client_secret"], session)
            try:
                await api.get_meters()
                return self.async_create_entry(title="Kenter", data=user_input)
            except Exception:
                errors["base"] = "auth"

        schema = vol.Schema({
            vol.Required("client_id"): str,
            vol.Required("client_secret"): str
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @callback
    def async_get_options_flow(config_entry):
        return KenterOptionsFlowHandler(config_entry)

class KenterOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_create_entry(title="", data={})
