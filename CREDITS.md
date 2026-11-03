# Credits, acknowledgments and development transparency

## Project development

**Kya Archipelago** is an independent community project maintained by **[LyraShimmer](https://github.com/LyraShimmer)**.

LyraShimmer led the project, defined its gameplay and Archipelago integration goals, gathered and compared game-state observations, performed hands-on PCSX2 testing, investigated edge cases, and evaluated whether memory mappings and features behaved correctly in real gameplay. The published mappings document an iterative reverse-engineering process, not a complete or official game specification.

## Reverse engineering: Ghidra

A particularly important acknowledgment goes to **[Ghidra](https://github.com/NationalSecurityAgency/ghidra)**, the open-source software reverse-engineering framework developed and maintained by the **National Security Agency (NSA)** and its contributors.

Ghidra was a **central tool** in this project. Its disassembler, decompiler, cross-references, structure and memory views, and program-analysis facilities made it possible to inspect PlayStation 2 game code, trace functions, study runtime object structures, and investigate memory addresses and persistent game-state data. The project also relied on repeated practical checks with PCSX2 and memory observation through PINE to validate those findings.

**Ghidra is a reverse-engineering tool, not a large language model.** It deserves explicit credit independently from any AI assistance.

## AI-assisted development disclosure

**Large language models played a substantial role in the development of this project.** In particular, **ChatGPT (OpenAI)** assisted with interpreting observations and Ghidra outputs, generating and reviewing code, developing memory-scanning and diagnostic tools, troubleshooting, drafting documentation, and organizing the mapping data.

AI-generated suggestions and code were not treated as inherently reliable. Memory addresses, flags, actor identifiers, save/load behavior, and gameplay logic required independent investigation and hands-on testing. Not every mapping or edge case should be considered fully verified; confidence levels and known limitations are documented in the repository.

The project is **not presented as entirely hand-written or entirely AI-generated**. It is a collaborative, tool-assisted engineering effort directed and tested by its maintainer. This disclosure is intended to be transparent about how the work was produced.

## Tools and communities

- **[Archipelago](https://github.com/ArchipelagoMW/Archipelago)** — the multiworld randomizer framework and community for which this integration was built.
- **[PCSX2](https://github.com/PCSX2/pcsx2)** — PlayStation 2 emulator used for runtime testing, graphics, and memory observation.
- **[Ghidra](https://github.com/NationalSecurityAgency/ghidra)** — reverse engineering of game code and object behavior; special thanks to its maintainers and contributors.
- **PINE** — the emulator communication interface used by the Launcher to interact with a running game.
- **[Python](https://www.python.org/)** and **[PyInstaller](https://pyinstaller.org/)** — implementation and Windows executable packaging.
- **[Pillow](https://python-pillow.github.io/)** — image handling used by the optional Kya Color Studio.

### Community documentation references

The public setup guides for **[Ratchet & Clank 2 Archipelago](https://github.com/evilwb/APRac2/blob/main/docs/setup_en.md)** and **[Sly 2 Archipelago](https://github.com/NikolajDanger/APSly2/blob/main/README.md)** are useful examples of how to explain PCSX2/PINE setup, APWorld installation, and troubleshooting. They are credited here as **documentation references only**. This acknowledgment is **not** a claim that their code was incorporated into Kya Archipelago.

If a future version adds or adapts third-party source code, that code should receive explicit authorship, attribution, and license documentation at the point of use.

## Unofficial project and rights

*Kya: Dark Lineage*, its characters, artwork, and original game assets remain the property of their respective rights holders. Kya Archipelago is an unofficial fan-made integration and is not affiliated with or endorsed by the game's rights holders, the Archipelago project, PCSX2, the NSA, or the AI/tool providers named above.

A license for this project's original source code has not yet been selected. The presence of source code on GitHub alone is not permission to redistribute proprietary game assets or to reuse the code under an assumed open-source license. See [`LICENSE_PENDING.md`](LICENSE_PENDING.md).
