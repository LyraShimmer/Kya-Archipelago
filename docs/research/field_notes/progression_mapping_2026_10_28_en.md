# Kya Archipelago — Recovered progression mapping

**Preserved references:** `mapping.txt` (The Quarry / Amber Quarry session transcript), `Logs(7).zip` (The Air Post session, October 28, 2026), and the October 28 progression matrix referenced in project history.

> **Caution:** This document summarizes observed facts, **not** an Archipelago ruleset certified to be free of softlocks. Releasing a Wolfen *after* receiving an item does not prove that this specific Wolfen requires that item. It is a historical research snapshot, not a substitute for the current APWorld implementation.

## 1. The Quarry and Amber Quarry — tester-reported requirements

| Segment | Reported requirement | Evidence / limitation |
|---|---|---|
| The Quarry entrance | No advanced equipment | Tester account; session resumed with 10 Wolfens already released and Hunter defeated |
| King Jamgut mount | Hunter defeated + vanilla mount/spawn event | Reported by tester; exact event trigger still to be confirmed |
| High platforms | Climbing Gloves | Explicit traversal blockage recorded |
| Amber Quarry cutscene | Speed Board and Climbing Gloves | Speed Board granted manually; cutscene observed and considered mandatory |
| Amber Quarry Wall Jump | Magic Bouncers | Blockage explicitly recorded, followed by test item grant |
| Later path | No other equipment mentioned | Tester observation; not proof that every location was exhaustively tested |

### 1.1 The Quarry Wolfens (31/31 persistent keys present in the session log)

| No. | Recorded subarea | Persistent key | Session observation |
|---:|---|---|---|
| 01 | Entrance | `0x296A` | Already released when this session began; individual requirements unknown |
| 02 | Entrance | `0x046A` | Already released when this session began; individual requirements unknown |
| 03 | Entrance | `0x176F` | Already released when this session began; individual requirements unknown |
| 04 | Entrance | `0x177A` | Already released when this session began; individual requirements unknown |
| 05 | Entrance | `0x048A` | Already released when this session began; individual requirements unknown |
| 06 | Entrance | `0x0476` | Already released when this session began; individual requirements unknown |
| 07 | Entrance | `0x0477` | Already released when this session began; individual requirements unknown |
| 08 | Quarry | `0x25AC` | Already released when this session began; individual requirements unknown |
| 09 | Quarry | `0x25AE` | Already released when this session began; individual requirements unknown |
| 10 | Quarry | `0x25AD` | Already released when this session began; individual requirements unknown |
| 11 | Quarry | `0x24FA` | Released on return after Climbing Gloves and mount were mentioned |
| 12 | Quarry | `0x24DD` | Released on return after Climbing Gloves and mount were mentioned |
| 13 | Quarry | `0x24DC` | Released on return after Climbing Gloves and mount were mentioned |
| 14 | Quarry | `0x0595` | Released before the recorded Speed Board grant (initial possession of other items uncertain) |
| 15 | Quarry | `0x0337` | Released before the recorded Speed Board grant (initial possession of other items uncertain) |
| 16 | Quarry | `0x1088` | Released before the recorded Speed Board grant (initial possession of other items uncertain) |
| 17 | Quarry | `0x25F9` | Released before the recorded Speed Board grant (initial possession of other items uncertain) |
| 18 | Quarry | `0x059D` | Released before the recorded Speed Board grant (initial possession of other items uncertain) |
| 19 | Quarry | `0x1781` | Released before the recorded Speed Board grant (initial possession of other items uncertain) |
| 20 | Arena | `0x24B0` | Released after Speed Board, before Magic Bouncers were granted |
| 21 | Arena | `0x24B2` | Released after Speed Board, before Magic Bouncers were granted |
| 22 | Arena | `0x0F1C` | Released after Magic Bouncers were granted |
| 23 | Arena | `0x0CC3` | Released after Magic Bouncers were granted |
| 24 | Arena | `0x09FC` | Released after Magic Bouncers were granted |
| 25 | Arena | `0x247B` | Released after Magic Bouncers were granted |
| 26 | Arena | `0x197E` | Released after Magic Bouncers were granted |
| 27 | Arena | `0x197F` | Released after Magic Bouncers were granted |
| 28 | Arena | `0x17BE` | Released after Magic Bouncers were granted |
| 29 | Arena | `0x17D0` | Released after Magic Bouncers were granted |
| 30 | Arena | `0x17BF` | Released after Magic Bouncers were granted |
| 31 | Arena | `0x17CD` | Released after Magic Bouncers were granted |

### 1.2 The Quarry cautions

- The Hunter boss was already defeated when the log began; The Quarry Map Discovery was also already confirmed.
- `Speed Board`: `ScenarioVar[16]` / `0x00425454` changed from 1 to 2 at 07:20:00.
- `Magic Bouncers`: `ScenarioVar[7]` / `0x0042540C` changed from 0 to 1 at 07:51:42.
- The main blockage field consistently said “need Climbing Gloves”; **read the free-text comment** to identify the actual additional requested items.
- Amber Quarry: 14 Wolfens expected, but the referenced archive detected 0/14; the mapper issue was unresolved in the reviewed materials. This is **not** evidence that they are inaccessible.
- The Quarry Rune location was reported, but no successful collection was proven in this log.

## 2. The Air Post — observations from `Logs(7).zip`, October 28

- Test used HP/mana/one-hit-kill aids and 10,000 DEBUG Nooties; Basic Boomy had been purchased. Debug teleport mode was disabled at session end, but panels for all six destinations were opened in-game.
- First noted gate: `Need Golden Boomy`; Silver and then Golden Boomy were granted at 07:02.
- Second noted gate: `need climbing gloves`; Climbing Gloves were granted at 07:13.
- Third noted gate: `Need Magic Bouncer`; Magic Bouncers were granted at 07:14.
- **Caution:** all three notes listed Climbing Gloves in the `Required item` column. The free-text comment is stronger evidence when distinguishing these three obstacles.

| Time | Subarea | Wolfen | Persistent key | Observed timing |
|---|---|---:|---|---|
| 07:00:58 | Dark Island | 03 | `0x054D` | Before Golden Boomy (Basic Boomy already owned) |
| 07:03:09 | Entrance | 01 | `0x26D4` | After Golden Boomy, before Climbing Gloves |
| 07:03:20 | Entrance | 02 | `0x26D7` | After Golden Boomy, before Climbing Gloves |
| 07:07:46 | Energy Field Control Room | 29 | `0x2659` | After Golden Boomy, before Climbing Gloves |
| 07:07:46 | Energy Field Control Room | 28 | `0x1D15` | After Golden Boomy, before Climbing Gloves |
| 07:15:07 | Energy Field Control Room | 30 | `0x2649` | After Climbing Gloves and Magic Bouncers |
| 07:16:15 | Energy Field Control Room | 32 | `0x01A4` | After Climbing Gloves and Magic Bouncers |
| 07:16:17 | Energy Field Control Room | 31 | `0x01A2` | After Climbing Gloves and Magic Bouncers |
| 07:16:22 | Energy Field Control Room | 33 | `0x01AE` | After Climbing Gloves and Magic Bouncers |

### 2.1 The Air Post cautions

- Nine The Air Post Wolfens were released during this session, plus one in Nativs City: ten in total.
- The log does not prove that every Wolfen 28–29 requires Golden Boomy; it only shows that they were released after receiving it.
- Wolfens 30–33 were released after two items were granted seconds apart; a controlled test would be needed to isolate the effects of Climbing Gloves and Magic Bouncers.

## 3. Initial progression survey — October 26 (older project matrix)

| Zone | Observed released Wolfens | Reported gate or limitation |
|---|---:|---|
| Nativs City | 1 | Initial unlock / shops |
| Flying Forest | 16 | Subsequent obstacles not individually characterized |
| Hunters Domain | 0 | Jamgut Birdcall reported necessary for the mount |
| The Quarry | 1 | Observation preceding the detailed Quarry session above |
| The Root | 5 | Map obtained; further locations to be mapped |
| The Air Post | 1 | Golden Boomy reported necessary for progress |
| Forgotten Island | 0 observed | FT01 was not seen; not proof that the zone is inaccessible |
| Wolfen City / The Fortress | Not tested in this survey | Separate elevator/progression requirements |

Context: six FT01 routes enabled, Basic Boomy purchased, combat aids active. These counts are **not** a strict itemless, unassisted test.

## 4. Evidence still required for a complete APWorld logic model

1. Test access to each Wolfen with a controlled set of items, starting from the same clean savestate and recording order and location.
2. Finish identifying/classifying the 14 Amber Quarry Wolfens and distinguish their gates from the rest of The Quarry.
3. Associate each obstacle with its **subregion** and exact AP check ID, not merely the zone name.
4. Validate progress with Climbing Gloves, Jamgut Birdcall, Magic Board / Speed Board, Golden Boomy, and Magic Bouncers across other zones.
5. Model non-inventory events and gates: Hunter / King Jamgut, cutscenes, runes, Fast Travels, shop costs, and access to Wolfen City / The Fortress.
6. Simulate all 315 historical checks rigorously, then validate in-game; a generated seed with a spoiler playthrough does not rule out physical softlocks.

**Historical status:** partial but valuable evidence recovery. Do **not** use these notes alone to mark all Wolfens as reachable or blocked. Check the current APWorld rules and newer runtime tests first.
