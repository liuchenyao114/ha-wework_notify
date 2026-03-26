from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

async def async_setup(hass, config):
    """设置集成（支持YAML配置，此处忽略）"""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """设置配置条目"""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # 将配置条目转发到 notify 平台
    await hass.config_entries.async_forward_entry_setup(entry, "notify")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸载配置条目"""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "notify")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True
