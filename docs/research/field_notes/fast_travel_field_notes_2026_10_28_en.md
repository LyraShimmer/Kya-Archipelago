# Kya: Dark Lineage — FT01 progression mapping and APWorld 0.8.6 audit

**Consolidated October 28, 2026.** PAL version SLES_514.73. These historical notes preserve observations from the October 26–28 conversations, `mapping.txt`, `Logs(7).zip`, and the `kya_dark_lineage.apworld` source extracted from `Kya_Archipelago_Beta_0_8_6_LOGIC_RECOVERY_FULL(1).zip`.

> **Historical snapshot:** References to APWorld 0.8.6 and its generation rules describe the October 28 build, **not** the current 0.8.14 release. They should not override current source code or verified tests.

## 1. Actual player test protocol (not a vanilla run)

- Clean early-game savestate.
- **Six FT01 teleporters prepared/unlocked in Nativs City**, allowing access to several zones from the beginning in **Archipelago mode**. This was **not** a linear vanilla progression test.
- Archipelago Launcher closed during diagnostics; a standalone mapper/BAT used PINE. Equipment was obtained in-game or granted manually **only when the tester reported a blockage**.
- HP, mana, and one-hit-kill aids may have been enabled. They make fights easier but do not prove that a traversal obstacle can be bypassed.
- For progression order, manually entered **“need…” notes** and `DON OBJET TEST` (test item granted) entries are the authoritative timestamps. Releasing a Wolfen after receiving an item does not prove that every such Wolfen specifically requires that ability.

## 2. Recovered field progression data

### Flying Forest

| Cumulative equipment / situation | Wolfens obtained | Evidence |
|---|---:|---|
| Basic Boomy, no advanced upgrades | 01–16 (16) | Tester observations, October 26–27 |
| + Magic Board | 01–23 (23) | Tester observation, October 27 |
| + Climbing Gloves | 01–25 (25) | Tester observation, October 27 |
| 26–37 | Not individually validated in this sequence | Exploration mentioned, no firm gate established |

The map and Blue Egg were accessible early in the notes. Receptacle was obtained after Magic Board. A later rune, shortly before the boss, was mentioned but not confirmed as a collected check in this test.

### Hunters Domain and Wind Tower

| Cumulative equipment / situation | Wolfens obtained | Evidence |
|---|---:|---|
| Entry without advanced equipment | 0/46 | Recorded observation |
| + Jamgut Birdcall | 01–02 (2) | Field test |
| + Climbing Gloves | 01–25 (25) | Field test |
| + Silver Boomy | 01–28 (28) | Field test |
| + Magic Bouncers | 01–46 (46) | Field test |

**Wind Tower:** Magic Bouncers are required, but **Silver Boomy is not**, according to the tester. The sequential item additions do not establish whether Silver Boomy is strictly required for Wolfens 29–46, because it was already available when Magic Bouncers were tested.

### The Root

| Cumulative equipment / situation | Wolfens obtained | Evidence |
|---|---:|---|
| Basic Boomy | 5/7 | Field test |
| + Magic Board | Still 5/7 | Field test |
| + Climbing Gloves | 7/7 | Field test |

The map and FT01 were accessible without advanced upgrades. The rune was not collected in this test.

### The Quarry and Amber Quarry

Initial reconnaissance on October 26 found one Wolfen at the entrance to The Quarry. During a later October 27 session, Wolfens **01–10 were already released** when recording started, and **Hunters Domain Boss Defeated** was already confirmed. This is a staged field record, **not** proof that Wolfens 01–10 are obtainable before those events.

| The Quarry Wolfens | Chronological observation | Explicit gating/uncertainty |
|---|---|---|
| 01–10 | Already released when logging started | Level entrance accessible; gating before/after Hunter needs confirmation |
| 11–13 | Released during backtracking | Climbing Gloves and King Jamgut mount trigger, per tester notes |
| 14–19 | Released **before** the recorded Speed Board grant | Route and Hunter progression may matter; do not blindly place them behind Speed Board |
| 20–21 | Released **after** Speed Board, before Magic Bouncers | Speed Board triggers a cutscene for Amber Quarry |
| 22–31 | Released **after** Magic Bouncers | Magic Bouncers unlock the later Wall Jump segment |

Other field conclusions: King Jamgut appears after defeating Hunter and a vanilla event, without injected scenario flags; Climbing Gloves are needed for elevated passages; Amber Quarry progression needs both Speed Board **and** Climbing Gloves, followed by Magic Bouncers. No further required equipment was observed by the tester.

**Amber Quarry:** 14 Wolfens were identified in the reference list, but the V4 mapper detected 0/14 during these sessions. This is **not** evidence that they were inaccessible; actor detection still needed investigation. Per-Wolfen Amber Quarry gates were **not documented** in these archives.

### The Air Post

Source: `Logs(7).zip`, October 28, 06:59–07:16. The six Nativs City FT01 panels appeared as `OUVERT vanilla` (vanilla-open) in the log. This described the **panel behavior**, not the selected APWorld generation mode.

| Sequence | Wolfens actually released | Observation |
|---|---|---|
| Basic Boomy, before Golden was granted | Dark Island 03 | Free-form blockage note: `Need Golden Boomy` |
| After Silver and then Golden, before Gloves | Entrance 01–02; Energy Field Control Room 28–29 | Four more releases; total 5 |
| After Climbing Gloves and Magic Bouncers | Energy Field Control Room 30–33 | Four more releases; total 9 |

Free-form notes: `Need Golden Boomy`, `need climbing gloves`, `Need Magic Bouncer`. **Caution:** `Blocages.csv` incorrectly placed all three under `Required item = Climbing Gloves`; use the free-text comments and timestamped item grants instead. Wolfens 30–33 were not tested with Gloves and Bouncers isolated from each other. The requirements for all 61 Wolfens remain incompletely mapped.

### Forgotten Island, Wolfen City, The Fortress

No dependable per-Wolfen accessibility table was recovered from these specific source records. `0 Wolfens observed` does **not** mean `0 Wolfens accessible`. Wolfen City and The Fortress have separate elevator and rune access conditions.

## 3. APWorld 0.8.6 source audit (October 28)

The `.apworld` source was compared byte-for-byte with the source directory from the ZIP; `world.py`, `constants.py`, and `options.py` were **identical**.

| Component | Historical code behavior | Measured mismatch / risk |
|---|---|---|
| Flying Forest | `world.py` `set_rules`: FF01–21 freely available; FF22–28 require Board; FF29–37 require Board + Gloves | Tests indicate a first gate **after FF16** and a Gloves gate after FF23. The historical rules allow too many Wolfens too early. |
| Hunters Domain | HD01–25 require only Jamgut; HD26–46 require Jamgut + (`Silver` **OR** `Bouncers`) | Missing **Climbing Gloves** for HD03–25, and not modeling Silver 26–28 / Bouncers 29–46 progression. |
| Wind Tower | Access through Hunters with Jamgut + (`Silver` **OR** `Bouncers`) | Does not model the observed **Bouncers without needing Silver** condition. |
| The Root | No individual rules for Root Wolfens 01–07 | Last two should require Gloves according to the tested sequence. |
| The Quarry | `QUARRY_SPEED_LOCK_START = 11` at the end of `constants.py` overrides an earlier value of 20, making Speed Board required for Wolfens 11–31 | Conflicts with 14–19 being freed before Speed and conflates Gloves/Mount/Speed/Bouncers stages. |
| Amber Quarry | Connection `The Quarry → Amber Quarry` checks only Progressive Board ×2 | Missing Gloves for traversal and Bouncers for later segments; gates for 14 Wolfens remain to be located. |
| The Air Post | All 61 Wolfens placed into one region without individual requirements | A seed with direct FT access to Air Post would deem all 61 immediately reachable, despite Golden/Gloves/Bouncers obstacles. |
| Shops | Availability based on the number of **logically reachable Wolfens**, not guaranteed obtainable Nooties | Critical items could be placed behind purchases with insufficient available currency. |

## 4. Critical distinction between test Fast Travels and generated Fast Travels

**Field test:** six unlocked FT01 routes, each going to a zone entrance. **Historical APWorld:** `options.py` defaulted `starting_fast_travels` to **5** (maximum 6); `generate_early()` picked a **random permitted FT index in each zone**, not necessarily FT01. Starting with FT02/03/04 can change physical accessibility.

Additionally, `world.py::_effective_ft_value()` prioritizes the YAML alias `fast_travel`: `vanilla` forces a vanilla graph even if `fast_travel_progression` says Archipelago. The YAML bundled with that historical ZIP contains `fast_travel: vanilla`, and its README explicitly recommends vanilla mode. Such generation does **not** reproduce the test situation of six initially unlocked FT01 routes. Setting `fast_travel: archipelago` and `starting_fast_travels: 6` was necessary but **not sufficient** to force FT01 in that version: index selection remained random.

## 5. Actionable findings and remaining work (as recorded in October)

1. **Do not repeat completed tests.** Reuse these observed gates as evidence when revising APWorld rules.
2. Fix the known Flying Forest, Hunters, Wind Tower, Root, and Quarry gates; retain **to be confirmed** labels wherever item effects were not isolated.
3. Reconcile the **six FT01** test routes with AP generation, or model individual FT02/03/04 starting destinations if random routing is kept.
4. Do not treat a generated spoiler `playthrough` as proof against physical softlocks before all 315 historical location accesses are modeled correctly.
5. Do not infer that 14 Amber Quarry Wolfens are inaccessible; the mapper failed to detect their actors.
6. Complete Air Post and Forgotten Island from genuinely missing evidence rather than repeating confirmed observations.

**Historical conclusion:** Most tester evidence was recovered. In APWorld 0.8.6, that evidence had not yet been fully translated into logic rules, and generation settings differed from the field protocol. No seed was certified softlock-free **at that time**.
