# Repository content guide — 9.0.0-beta1

The public `Github/` directory is the source repository. It includes all redistributable integration code, Python modules, release configuration, canonical JSON maps, CSV address mappings, an updated 19-sheet research workbook, English technical field notes, and project documentation.

- `launcher/`: actual launcher/bridge/Color Studio source code, build specifications, and canonical JSON data.
- `apworld/`: Archipelago world generation source. The separately shipped `.apworld` package contains the playable world.
- `docs/research/mapping_data/`: numerical mappings and IDs; addresses and integer values were preserved during English translation.
- `docs/research/field_notes/`: English translations of historic October 2026 progression studies (historical, not authoritative for latest logic).
- `docs/versions.md`: release label vs runtime compatibility versions.
- `CHANGELOG.md` and `README.md`: English release and installation guidance.

## What must not be uploaded as part of the repository

`Private/` is retained for the maintainer only: build scripts, optional texture replacements awaiting rights review, historical records and unedited original field notes. The original game ISO and extracted game files are intentionally excluded.

## GitHub release (player downloads)

Upload **exactly three files** from `Release_Assets/` once the Windows build has successfully produced and tested `Launcher.zip`:

1. `Launcher.zip` — compiled launcher and required runtime data.
2. `kya_dark_lineage.apworld` — Archipelago game package.
3. `Kya_Dark_Lineage.yaml` — example player configuration.

Before compilation, `Launcher.zip` is intentionally absent. Run `BUILD_RELEASE_ON_WINDOWS.bat` locally, and verify the EXE runs with PCSX2.
