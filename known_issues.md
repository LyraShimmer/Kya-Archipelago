# Known limits for the first beta

- Native shop recovery has been validated on a completed save, but fresh-seed multiworlds should still be tested end-to-end.
- Certain Fast Travel locations require live state transitions and may not automatically recover from a 100% save. Fast Travel location progression-item placement is restricted by the APWorld policy.
- Boss and cinematic checks should be verified with the relevant scene triggers. The goal check is tied to the ending event, not an earlier defeated-state flag.
- No in-container Windows EXE build or real PCSX2 integration test has been run for this GitHub repository preparation.
- This repository contains game-specific memory addresses; builds outside PAL `SLES-51473` are unsupported.

## Fast Travel progression modes - testing status

### Archipelago progression - extensively tested

The **Archipelago Fast Travel progression mode** (`fast_travel: archipelago` and `fast_travel_progression: archipelago`) is the main tested mode. Community testing has included **dozens of successfully completed runs**, including solo and multiworld progression tests. No progression-blocking issues were reported in those runs.

### Vanilla progression - limited testing

The **Vanilla Fast Travel progression mode** (`fast_travel: vanilla` and `fast_travel_progression: vanilla`) has **not received the same level of testing**. Unlike Archipelago progression, it keeps the game's original zone and Fast Travel progression while Archipelago still randomizes items. Its end-to-end accessibility and completion have not yet been validated through comparable repeated runs.

**No specific softlock is currently confirmed in Vanilla mode**, but it should be considered less thoroughly validated than Archipelago progression. Additional Vanilla-mode testing and bug reports are welcome.
