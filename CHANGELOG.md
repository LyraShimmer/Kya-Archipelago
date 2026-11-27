# Changelog

## v9.0.2-beta (2026-11-27)

- Fixed secure WebSocket (WSS) certificate verification failures on hosted Archipelago rooms, contributed by eNigma (@eBigma) through PR #1.
- Added certificate trust fallback via optional `KYA_CA_BUNDLE`, `certifi`, then the OS store. Certificate verification is never disabled.
- Updated Launcher packaging to bundle `certifi`.
- Added contributor credits and third-party notices.
- Confirmed successful connections to `archipelago.gg` in live testing.
- Launcher-only release: no changes to APWorld, YAML, game logic, progression conditions or location IDs.

## v9.0.1-beta (2026-11-15)

- Restored/retained all 318 AP checks, including Wolfen City 41.
- Six FT01 destinations open initially in Archipelago mode.
- Quarry/Root physical access rules tightened.
- Wolfen City and The Fortress checks may not hold advancement items.
- Previous bracelet shop accessibility rules retained.
- Updated Launcher Python source auto-credits a native Rune check on receiving
  its AP Rune item, to prevent an uncollectable native Rune pickup check.
- No Windows binary produced. SSL runtime untouched; recompile before gameplay test.


## 9.0.0-beta1 — private/open beta preparation

- Release naming adopted without modifying the underlying protocol or Archipelago IDs.
- Based on Launcher 0.9.63 and APWorld 0.8.14 compatibility behavior.
- Native shop sold-state recovery validated in a real Archipelago session with 18 shops acknowledged.
- Hunter's Domain defeated-state recovery added for already-completed saves; validate with a new room if necessary.
- Camera/map zoom preserved from the last user-verified launcher state.
- Launcher Options dialog height adjusted to its content.
- Optional texture replacements and the Archipelago logo are kept separate.
- Published source mappings and research indexes for inspection and beta reporting.

For full testing history, see the archived local development notes; not every check was end-to-end validated in a randomized playthrough.

### GitHub packaging and research documentation

- Translated research mapping notes and the research tracker text to English.
- Preserved all memory addresses, numeric keys, IDs and Archipelago location names.
- Shortened the staging archive paths to work with standard Windows extraction.
- Preserved separate source repository and three-player-asset release layout.
