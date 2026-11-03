# Memory research methodology and verification

This project shares its memory-address mappings to help readers understand how the Archipelago integration was built and where its assumptions come from.

## Research workflow

1. **Static investigation with [Ghidra](https://github.com/NationalSecurityAgency/ghidra).** Disassemble and examine game routines, data references, actor layouts, vtables, and code paths relevant to progression, maps, events, and shops.
2. **Runtime observation in PCSX2.** Use PINE and controlled gameplay experiments to observe candidate memory values before and after specific actions. Compare multiple saves, zones, restarts, and game states when possible.
3. **Identity before addresses.** Runtime actor allocation addresses can move. Prefer confirmed persistent object keys and context over assuming that one absolute actor address remains valid.
4. **Cross-validation.** Confirm that a value changes in the expected direction when an action happens, remains meaningful across reloads, and does not simply reflect an unrelated visual/UI state.
5. **Archipelago integration.** Encode source-derived checks in the Launcher/APWorld, then verify server acknowledgment and avoid duplicate checks.
6. **Regression tests.** Re-check interactions between scene transitions, FT, the shop watcher, boss triggers, the ending, and reconnect recovery. Document unverified paths instead of claiming them as complete.

## Important distinctions

- **Observation is not proof of causation.** A flag that changes during a cinematic may be a useful candidate but needs follow-up validation.
- **Dynamic pointers are not persistent IDs.** Research sheets distinguish actor pointers from durable Wolfen keys.
- **An item being available is not the same as it being bought.** Shop stock and native sold-state observations must not be interchanged.
- **A completed save cannot prove all live-trigger paths.** Certain Fast Travel and boss events require the action to occur during the session.
- **Version specificity matters.** The addresses were researched for PAL `SLES-51473`. Do not apply them blindly to other revisions.

## Use of AI tools

LLM assistants, especially ChatGPT, contributed significantly to analysis, code generation, diagnostics, and documentation. Their outputs were suggestions and hypotheses, **not substitutes for game-memory measurements and in-game tests**. See [Credits](../../CREDITS.md) for the detailed disclosure.

## Data sources

The JSON files in [`launcher/data/`](../../launcher/data/) and APWorld modules in [`apworld/kya_dark_lineage/`](../../apworld/kya_dark_lineage/) are the primary implementation references. The files in [`mapping_data/`](mapping_data/) and [`field_notes/`](field_notes/) are readable research records with different degrees of confidence; some entries may be historical or provisional.

The repository does not include any original game ISO, raw executable, or bulk extracted game files.
