import os
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN,
    ENV_WEWORK_NAME,
    ENV_WEWORK_CORPID,
    ENV_WEWORK_AGENTID,
    ENV_WEWORK_SECRET,
    ENV_WEWORK_TOUSER,
)

class WeWorkNotifyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        # 从环境变量读取默认值
        default_name = os.getenv(ENV_WEWORK_NAME, "企业微信通知")
        default_corpid = os.getenv(ENV_WEWORK_CORPID, "")
        default_agentid = os.getenv(ENV_WEWORK_AGENTID, "")
        default_secret = os.getenv(ENV_WEWORK_SECRET, "")
        default_touser = os.getenv(ENV_WEWORK_TOUSER, "@all")

        if user_input is not None:
            # 检查 name 是否重复（避免 notify 服务名冲突）
            await self.async_set_unique_id(user_input["name"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input
            )

        schema = vol.Schema({
            vol.Required("name", default=default_name): str,
            vol.Required("corpid", default=default_corpid): str,
            vol.Required("agentId", default=default_agentid): str,
            vol.Required("secret", default=default_secret): str,
            vol.Required("touser", default=default_touser): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WeWorkOptionsFlow(config_entry)


class WeWorkOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        data = self.config_entry.data
        default_name = data.get("name", os.getenv(ENV_WEWORK_NAME, "企业微信通知"))
        default_corpid = data.get("corpid", os.getenv(ENV_WEWORK_CORPID, ""))
        default_agentid = data.get("agentId", os.getenv(ENV_WEWORK_AGENTID, ""))
        default_secret = data.get("secret", os.getenv(ENV_WEWORK_SECRET, ""))
        default_touser = data.get("touser", os.getenv(ENV_WEWORK_TOUSER, "@all"))

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("name", default=default_name): str,
            vol.Required("corpid", default=default_corpid): str,
            vol.Required("agentId", default=default_agentid): str,
            vol.Required("secret", default=default_secret): str,
            vol.Required("touser", default=default_touser): str,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
