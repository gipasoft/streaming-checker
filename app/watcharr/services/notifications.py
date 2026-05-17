from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

import requests

from watcharr.core.config import Settings
from watcharr.storage.sqlite import AvailabilityChange


@dataclass(frozen=True)
class NtfyMessage:
    title: str
    body: str
    priority: str
    tags: list[str]


class NtfyNotifier:
    def __init__(self, settings: Settings, timeout: int = 10):
        self.url = settings.ntfy_url
        self.topic = settings.ntfy_topic
        self.token = settings.ntfy_token
        self.username = settings.ntfy_username
        self.password = settings.ntfy_password
        self.priority = settings.ntfy_priority
        self.tags = settings.ntfy_tags
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.topic)

    def notify_provider_change(self, *, kind: str, title: str, change: AvailabilityChange) -> bool:
        if not self.enabled:
            return False

        message = self.build_provider_change_message(kind=kind, title=title, change=change)
        headers = {
            "Title": message.title,
            "Priority": message.priority,
        }
        if message.tags:
            headers["Tags"] = ",".join(message.tags)
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        auth = (self.username, self.password) if self.username and self.password and not self.token else None
        response = requests.post(
            self._topic_url(),
            data=message.body.encode("utf-8"),
            headers=headers,
            auth=auth,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return True

    def build_provider_change_message(self, *, kind: str, title: str, change: AvailabilityChange) -> NtfyMessage:
        added = self._join(change.added_providers)
        removed = self._join(change.removed_providers)
        current = self._join(change.current_providers)
        body = (
            f"{title} ({kind})\n"
            f"Disponibile ora: {current}\n"
            f"Aggiunti: {added}\n"
            f"Rimossi: {removed}"
        )
        return NtfyMessage(
            title="Provider streaming cambiati",
            body=body,
            priority=self.priority,
            tags=self.tags,
        )

    def _topic_url(self) -> str:
        assert self.url is not None
        assert self.topic is not None
        return f"{self.url}/{quote(self.topic.strip('/'))}"

    @staticmethod
    def _join(values: list[str]) -> str:
        return ", ".join(values) if values else "-"

