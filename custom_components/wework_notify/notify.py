import os
import json
import asyncio
import requests
from homeassistant.components.notify import BaseNotificationService
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import (
    DOMAIN,
    ENV_WEWORK_NAME,
    ENV_WEWORK_CORPID,
    ENV_WEWORK_AGENTID,
    ENV_WEWORK_SECRET,
    ENV_WEWORK_TOUSER,
)

# ------------------- YAML 配置支持（保留） -------------------
def get_service(hass, config, discovery_info=None):
    """同步方式，用于YAML配置（兼容）"""
    corpid = os.getenv(ENV_WEWORK_CORPID)
    agentid = os.getenv(ENV_WEWORK_AGENTID)
    secret = os.getenv(ENV_WEWORK_SECRET)
    touser = os.getenv(ENV_WEWORK_TOUSER, "@all")
    return WeWorkNotificationService(corpid, agentid, secret, touser)


async def async_get_service(hass, config, discovery_info=None):
    """异步方式，用于YAML配置（兼容）"""
    corpid = os.getenv(ENV_WEWORK_CORPID)
    agentid = os.getenv(ENV_WEWORK_AGENTID)
    secret = os.getenv(ENV_WEWORK_SECRET)
    touser = os.getenv(ENV_WEWORK_TOUSER, "@all")
    return WeWorkNotificationService(corpid, agentid, secret, touser)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """YAML 配置入口（兼容）"""
    service = await async_get_service(hass, config)
    async_add_entities([service])
    return True


# ------------------- 配置流入口 -------------------
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """配置流入口，返回通知服务实例"""
    data = hass.data[DOMAIN][entry.entry_id]
    corpid = data.get("corpid")
    agentid = data.get("agentId")
    secret = data.get("secret")
    touser = data.get("touser", "@all")

    service = WeWorkNotificationService(corpid, agentid, secret, touser)
    # 返回服务实例，notify组件将自动注册为 notify.<entry.title>
    return service


# ------------------- 通知服务类 -------------------
class WeWorkNotificationService(BaseNotificationService):
    def __init__(self, corpid, agentid, secret, touser):
        self.corpid = corpid
        self.agentid = agentid
        self.secret = secret
        self.touser = touser

    def send_message(self, message="", **kwargs):
        """同步发送消息（供异步方法调用）"""
        if not all([self.corpid, self.agentid, self.secret]):
            raise Exception("企业微信参数不完整：corpid、agentId、secret 必须配置")

        # 获取 token
        token_url = (
            f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            f"?corpid={self.corpid}&corpsecret={self.secret}"
        )
        try:
            ret = requests.get(token_url, timeout=10).json()
        except Exception as e:
            raise Exception(f"获取token失败: {e}")

        if ret.get("errcode") != 0:
            raise Exception(f"token错误: {ret.get('errmsg')}")
        access_token = ret["access_token"]

        # 发送消息
        send_url = (
            f"https://qyapi.weixin.qq.com/cgi-bin/message/send"
            f"?access_token={access_token}"
        )
        payload = {
            "touser": self.touser,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {"content": message},
            "safe": 0
        }

        resp = requests.post(send_url, data=json.dumps(payload), timeout=10).json()
        if resp.get("errcode") != 0:
            raise Exception(f"发送失败: {resp.get('errmsg')}")

    async def async_send_message(self, message="", **kwargs):
        """异步发送消息，在线程中调用同步方法避免阻塞"""
        await asyncio.to_thread(self.send_message, message, **kwargs)
