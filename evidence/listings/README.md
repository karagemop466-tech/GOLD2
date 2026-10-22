# Listing evidence index

The authoritative evidence for the current dataset is **item-scoped**: each `data/listings/*.json` row points to one file named after its item ID (for example, `bn-203348.md`). Each file identifies the official product URL, retrieval date, field-specific excerpts, capture limitations, and any rejected non-primary values.

The five category-named files (`solitaire.md`, `halo-pave.md`, `three-stone-vintage.md`, `18k.md`, and `budget.md`) are inherited shared-category capture notes retained for audit history. They are **not** used by the current field-level provenance audit, because shared files can allow one item’s values to be mistaken for another’s.

No evidence file is a full HTML archive, and none represents physical inspection. The generated site and `tools/qa.py` use only the per-item references stored in the JSON records.
