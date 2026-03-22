"""claw-reliability: Discord webhook alerter."""

import json
import urllib.request
import urllib.error
from alerts.base import BaseAlerter, Alert, Severity


class DiscordAlerter(BaseAlerter):
    COLORS = {Severity.INFO: 0x3498DB, Severity.WARNING: 0xF39C12, Severity.CRITICAL: 0xE74C3C}

    def __init__(self, webhook_url):
        if not webhook_url:
            raise ValueError("Discord webhook_url is required")
        self.webhook_url = webhook_url

    def send_alert(self, alert):
        embed = {
            "title": f"claw-reliability: {alert.alert_type.value.replace('_', ' ').title()}",
            "description": alert.message,
            "color": self.COLORS.get(alert.severity, 0x95A5A6),
            "fields": [{"name": k.replace("_", " ").title(), "value": str(v)[:1024], "inline": True}
                       for k, v in alert.details.items()],
            "footer": {"text": f"Severity: {alert.severity.value.upper()}"}
        }
        payload = {"embeds": [embed]}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.webhook_url, data=data,
                                      headers={"Content-Type": "application/json",
                                               "User-Agent": "DiscordBot (claw-reliability, 1.0)"},
                                      method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in (200, 204)
        except Exception as e:
            print(f"[claw-reliability] Discord alert failed: {e}")
            return False
