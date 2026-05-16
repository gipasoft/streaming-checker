import re


def slug_provider(provider_name: str) -> str:
    value = provider_name.strip().lower()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def provider_tag(prefix: str, provider_name: str) -> str:
    return f"{prefix}{slug_provider(provider_name)}"


def desired_tags(
    provider_names: list[str],
    *,
    tag_generic: bool,
    tag_providers: bool,
    generic_tag: str,
    tag_prefix: str,
) -> set[str]:
    tags: set[str] = set()

    if provider_names and tag_generic:
        tags.add(generic_tag)

    if tag_providers:
        for provider_name in provider_names:
            tags.add(provider_tag(tag_prefix, provider_name))

    return tags

