from __future__ import annotations

from dataclasses import dataclass, field

from watcharr.core.provider_mappings import (
    PROVIDER_ALIASES,
    PROVIDER_CATEGORIES,
    PROVIDER_CLEANUP_SUFFIXES,
)
from watcharr.core.tags import slug_provider


@dataclass(frozen=True)
class NormalizedProvider:
    canonical_name: str
    slug: str
    category: str | None = None
    original_names: list[str] = field(default_factory=list)


class ProviderNormalizer:
    def __init__(
        self,
        *,
        aliases: dict[str, str] | None = None,
        cleanup_suffixes: tuple[str, ...] | None = None,
        categories: dict[str, str] | None = None,
    ):
        self.aliases = aliases or PROVIDER_ALIASES
        self.cleanup_suffixes = cleanup_suffixes or PROVIDER_CLEANUP_SUFFIXES
        self.categories = categories or PROVIDER_CATEGORIES
        self._alias_lookup = {self._key(alias): canonical for alias, canonical in self.aliases.items()}

    def normalize_many(self, provider_names: list[str]) -> list[NormalizedProvider]:
        by_canonical: dict[str, list[str]] = {}

        for provider_name in provider_names:
            original = provider_name.strip()
            if not original:
                continue

            canonical = self.canonical_name(original)
            by_canonical.setdefault(canonical, [])
            if original not in by_canonical[canonical]:
                by_canonical[canonical].append(original)

        return [
            NormalizedProvider(
                canonical_name=canonical,
                slug=slug_provider(canonical),
                category=self.categories.get(canonical),
                original_names=originals,
            )
            for canonical, originals in sorted(by_canonical.items(), key=lambda item: item[0].casefold())
        ]

    def canonical_name(self, provider_name: str) -> str:
        cleaned = self.cleanup(provider_name)
        return self._alias_lookup.get(self._key(cleaned), cleaned)

    def cleanup(self, provider_name: str) -> str:
        value = " ".join(provider_name.strip().split())
        value = self._alias_lookup.get(self._key(value), value)

        for suffix in self.cleanup_suffixes:
            if value.casefold().endswith(suffix.casefold()):
                value = value[: -len(suffix)].strip()
                value = self._alias_lookup.get(self._key(value), value)
                break

        return value

    @staticmethod
    def canonical_names(providers: list[NormalizedProvider]) -> list[str]:
        return [provider.canonical_name for provider in providers]

    @staticmethod
    def original_names(providers: list[NormalizedProvider]) -> list[str]:
        originals: list[str] = []
        for provider in providers:
            originals.extend(provider.original_names)
        return originals

    @staticmethod
    def _key(value: str) -> str:
        return " ".join(value.strip().casefold().split())
