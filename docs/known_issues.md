# Known limits for the first beta

- Native shop recovery has been validated on a completed save, but fresh-seed multiworlds should still be tested end-to-end.
- Certain Fast Travel locations require live state transitions and may not automatically recover from a 100% save. Fast Travel location progression-item placement is restricted by the APWorld policy.
- Boss and cinematic checks should be verified with the relevant scene triggers. The goal check is tied to the ending event, not an earlier defeated-state flag.
- No in-container Windows EXE build or real PCSX2 integration test has been run for this GitHub repository preparation.
- This repository contains game-specific memory addresses; builds outside PAL `SLES-51473` are unsupported.
