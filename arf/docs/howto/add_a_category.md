# How to Add a Category

## Goal

Register a new category in [`meta/categories/`](../../../meta/categories/) so it can tag assets,
suggestions, and tasks.

## Prerequisites

* A kebab-case slug (e.g. `supervised-learning`, `bi-encoder`)
* Read
  [`arf/specifications/category_specification.md`](../../specifications/category_specification.md)

## Steps

1. Create the folder: `meta/categories/<slug>/`. The folder name is the canonical slug and must be
   lowercase letters, digits, and hyphens only, starting with a letter.
2. Create `meta/categories/<slug>/description.json` with these fields:
   * `spec_version` — integer, currently `1`
   * `name` — human-friendly display name (title case)
   * `short_description` — one-sentence summary of the category's scope
   * `detailed_description` — 2-5 sentence paragraph covering scope, boundaries, and examples
3. Use
   [`meta/categories/bi-encoder/description.json`](../../../meta/categories/bi-encoder/description.json)
   as a reference.
4. Run
   [`uv run python -m arf.scripts.verificators.verify_categories`](../../scripts/verificators/verify_categories.py).
5. Tag new assets, suggestions, and tasks with the slug.

## Verification

```bash
uv run python -m arf.scripts.verificators.verify_categories
```

Expected: no errors, new slug listed among validated categories.

## Pitfalls

* Slug not kebab-case — lowercase letters, digits, hyphens only
* Slug starts with a digit — must start with a letter
* `spec_version` written as a string instead of an integer
* `detailed_description` under 50 characters — too short to tell when to apply the tag
* Near-duplicate of an existing category
* Using a category in an asset before registering it

## See Also

* `../reference/categories.md`
* `../../specifications/category_specification.md`
