from __future__ import annotations

from streaming_checker.clients.arr_client import ArrClient, ArrItem
from streaming_checker.core.config import Settings
from streaming_checker.core.tags import desired_tags


class TaggingService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def desired_labels(self, providers: list[str]) -> set[str]:
        return desired_tags(
            providers,
            tag_generic=self.settings.tag_generic,
            tag_providers=self.settings.tag_providers,
            generic_tag=self.settings.generic_tag,
            tag_prefix=self.settings.tag_prefix,
        )

    def apply(self, client: ArrClient, item: ArrItem, providers: list[str]):
        labels = self.desired_labels(providers)

        if providers:
            print(f"[{client.kind}] {item.title}: {', '.join(providers)}")
        else:
            print(f"[{client.kind}] {item.title}: no providers")

        client.update_tags(
            item,
            labels,
            generic_tag=self.settings.generic_tag,
            tag_prefix=self.settings.tag_prefix,
            remove_stale=self.settings.remove_stale_tags,
            dry_run=self.settings.dry_run,
        )

