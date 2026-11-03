# Kya: Dark Lineage — Archipelago

**First beta: `9.0.0-beta1`** · PAL PS2 `SLES-51473` · PCSX2 + PINE

An unofficial, community-developed Archipelago multiworld integration for *Kya: Dark Lineage*. This repository makes the **Launcher source, APWorld source, runtime memory maps, reverse-engineering research tables, and technical documentation** available for inspection.

> **Open development disclosure:** This project was led and experimentally tested by [LyraShimmer](https://github.com/LyraShimmer), with **substantial LLM assistance (especially ChatGPT)** for code, research analysis, troubleshooting, and documentation. **[Ghidra](https://github.com/NationalSecurityAgency/ghidra)**, developed by the NSA and its contributors, was an essential reverse-engineering tool. We explicitly credit both the AI assistance and the independent tools, while distinguishing suggestions from memory observations validated in PCSX2. See the full **[Credits and acknowledgments](CREDITS.md)**.

## Download and play

Get the following files from **GitHub Releases** (not from the repository's automatically generated `Source code.zip`):

| Download | Description |
| --- | --- |
| `Launcher.zip` | Compiled Windows Launcher, MemoryCore, runtime data and optional tools |
| `kya_dark_lineage.apworld` | Custom world for Archipelago |
| `Kya_Dark_Lineage.yaml` | Example player configuration |

**[Read the step-by-step installation guide](docs/installation.md)** before playing. It covers the supported PAL game version, enabling PINE, **switching PCSX2 from Software Renderer to Vulkan**, enabling replacement textures, generating a custom-world seed, and connecting the Launcher.

## Current features

- Wolfen rescue checks and persistent Wolfen-key mapping.
- Archipelago item and progression integration, with randomized access gates.
- Fast Travel destinations, logic and access options.
- Shop purchases, sold-state detection and recovery.
- Boss, map, rune and special-event locations.
- End-of-game goal detection.
- Launcher camera inversion and in-game Archipelago overlay.
- Optional Kya Color Studio for local appearance customization.

Some events and Fast Travels require live transitions or further beta testing. See [Known issues](docs/known_issues.md).

## Technical sources and research

| Directory | Contents |
| --- | --- |
| [`launcher/`](launcher/) | Actual Launcher Python modules and MemoryCore bridge |
| [`launcher/data/`](launcher/data/) | JSON definitions for memory data, items, Wolfen, Fast Travels, shops and zones |
| [`apworld/kya_dark_lineage/`](apworld/kya_dark_lineage/) | APWorld code, logic, options and internal setup docs |
| [`docs/research/`](docs/research/) | Readable memory-mapping tables and field notes |
| [`docs/research/mapping_data/`](docs/research/mapping_data/) | CSV exports and Excel research tracker |
| [`docs/research/methodology.md`](docs/research/methodology.md) | How addresses, persistent keys, and trigger candidates were investigated and tested |
| [`docs/architecture.md`](docs/architecture.md) | Runtime architecture |

The exported dataset includes **318 named locations** and **257 Wolfen key mappings**. These are source-table counts, not a claim that every location was independently validated end-to-end.

## Configuration and development

- [Player YAML options](docs/configuration.md)
- [Developer build instructions](docs/build.md)
- [Release/version compatibility](docs/versions.md)
- [Known issues](docs/known_issues.md)
- [Research methods and confidence](docs/research/methodology.md)

The **release label** `9.0.0-beta1` is a public milestone; the compatible implementation versions are Launcher `0.9.63` and APWorld `0.8.14`.

## Credits, AI disclosure, rights

The development process used **LLMs extensively**, particularly ChatGPT, alongside independent static analysis using **Ghidra** and empirical verification via **PCSX2/PINE**. The human maintainer directed the work, tested behavior in the game, and decided what to retain. For complete, explicit attribution to Ghidra/NSA, Archipelago, PCSX2, the AI providers and community references, read **[CREDITS.md](CREDITS.md)**.

*Kya: Dark Lineage* and its original assets are owned by their respective rights holders. This is an unofficial fan project, unaffiliated with the game rights holders, PCSX2, Archipelago, the NSA, or the listed AI providers. Game ISO files, bulk original game extracts and executable game binaries are not supplied. Review any bundled artwork or textures before distributing them publicly.

**License status:** A license for the project's original code has not yet been selected; see [`LICENSE_PENDING.md`](LICENSE_PENDING.md). Do not assume that repository visibility alone grants redistribution rights.
