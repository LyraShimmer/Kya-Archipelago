# Reverse-engineering data and mapping references

The purpose of this folder is **maximum inspectable detail on the integration's own code and address mapping**, not a mirror of the copyrighted game data.

## Canonical exported tables

- `mapping_data/archipelago_locations.csv` — 318 names and stable AP location IDs
- `mapping_data/archipelago_items.csv` — AP item IDs
- `mapping_data/wolfen_persistent_keys.csv` — 257 persistent Wolfen keys mapped to AP names
- `mapping_data/fast_travel_persistent_keys.csv` — 23 zone-local Fast Travel key mappings
- `mapping_data/shops_and_stock_flags.csv` — 18 candidate stock flags/bitmasks (**not authoritative purchased-state flags**)
- `mapping_data/special_events_conditions.csv` — recorded conditions for special locations and quest events
- `mapping_data/fast_travel_buttons_canonical.csv` and `fast_travel_buttons_reviewed.csv` — observed route/button association studies
- `mapping_data/fast_travel_bridge_results.csv` — observed FT bridge relationships
- `mapping_data/memory_and_location_research_tracker.xlsx` — detailed research spreadsheet, with public text translated to English while preserving technical values

The full, original JSON mapping is in [`launcher/data/`](../../launcher/data/) and the world data is in [`apworld/kya_dark_lineage/`](../../apworld/kya_dark_lineage/). They take precedence over older research when values conflict.

## Research process

See [methodology.md](methodology.md) for the static-analysis, Ghidra, PCSX2/PINE testing, and LLM-assisted development disclosure.

## Confidence and risks

Research tables contain **observed, provisional and obsolete** data. Runtime addresses can shift; they are not all safe to read or write at every moment. Some shop serialization flags were demonstrated **not** to represent purchases reliably. Shop sold-state recovery uses actor-based identification in `kya_shop_native.py`; do not substitute these stock flags for it. A saved 100% game's opened routes are not a substitute for verified live check transitions.

Historical field notes in `field_notes/` are translated to English for publication. The untranslated French originals are retained only in the private staging folder for traceability. Original ISO assets, executable game binaries, decompilation dumps, test logs and local user paths are deliberately excluded.
