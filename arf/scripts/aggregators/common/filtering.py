"""Shared filtering logic for asset aggregators."""


def matches_categories(
    *,
    asset_categories: list[str],
    filter_categories: list[str] | None,
) -> bool:
    if filter_categories is None:
        return True
    filter_set: set[str] = set(filter_categories)
    return len(filter_set.intersection(asset_categories)) > 0


def matches_ids(
    *,
    asset_id: str,
    filter_ids: list[str] | None,
) -> bool:
    if filter_ids is None:
        return True
    return asset_id in set(filter_ids)
