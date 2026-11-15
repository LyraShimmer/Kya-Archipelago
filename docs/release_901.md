# Kya Archipelago v9.0.1 RC2 — GitHub preparation kit

This repository is a **release candidate**, not a verified 100% playable build.

## Release asset names (preserved from v9.0.0-beta)

- `Launcher.zip`
- `Kya_Dark_Lineage.yaml`
- `kya_dark_lineage.apworld`

The APWorld has 318 location IDs, including Wolfen City 40 Wolfens and Map Discovery.
RC2 rule adjustments: six initial FT01 destinations in Archipelago mode; Quarry/Bouncers gate;
Wolfen City and Fortress progression-item exclusions; vanilla rune pickups cannot hold progression.
The source Launcher auto-acknowledges a rune's native check when its AP item is received.

## IMPORTANT: Windows launcher compilation

`Release/Launcher.zip` in the outer kit is a **Python source-mode launcher**, NOT a compiled EXE.
The corrected rune-check behavior requires the updated Launcher source. The existing v9.0.0
Launcher.exe does **not** contain this change; do not relabel it as v9.0.1.

On Windows, from the OUTER extracted kit run `BUILD_RELEASE_WINDOWS.bat`.
This installs the build dependencies, builds `Kya_Archipelago_Launcher.exe` and
`Kya_MemoryCore.exe`, and replaces `Release/Launcher.zip` with the compiled Windows bundle.
Keep the whole `data` folder next to the EXEs. Verify SSL connectivity, inventory, shops,
local Fast Travels, rune checks and goal in PCSX2 before publishing.

For generation-only tests, install `Release/kya_dark_lineage.apworld` and use
`Release/Kya_Dark_Lineage.yaml`; Launcher recompilation is not necessary.

## Known limitations and publication prerequisites

- Previous 5 RC2 seeds passed the currently implemented AP world graph; this is not a
  physical-game proof that every check is reachable.
- Complete a real in-game test before claiming 100% completion.
- Original game-derived artwork and external dependencies require rights/license review.
  `LICENSE_PENDING.md` has not been silently converted into an open-source license.
- Neither this packaging step nor the included scripts modify GitHub remotely.
