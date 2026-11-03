# Technical architecture

The integration works with a running copy of *Kya: Dark Lineage* PAL `SLES-51473` through PCSX2's PINE interface. The game is **not** modified or distributed as a patched ISO.

```text
PCSX2 (PAL game)
     |
PINE localhost:28011
     |
MemoryCore bridge (kya_memory_core.py)
     |
Launcher (Kya_Archipelago_Launcher.py)
     |-- Memory checks: Wolfen actors, shops, FT, bosses, maps, quests
     |-- Runtime JSON datasets in launcher/data/
     |-- Local pending-check queue and connection handling
     |
Archipelago server <--> apworld/kya_dark_lineage/
```

The launcher handles runtime observations and synchronization. The APWorld handles location/item IDs, options, placement and region logic. **Do not equate dynamic actor pointers with persistent IDs.** Data files are the source of truth for the observed addresses and associations.

## Relevant modules

| Component | Role |
| --- | --- |
| `launcher/Kya_Archipelago_Launcher.py` | Window and main controller/watch loop |
| `launcher/kya_memory_core.py` | Background memory bridge |
| `launcher/kya_pine_raw.py`, `launcher/kya_memory_bootstrap.py` | Low-level PINE and bootstrap helpers |
| `launcher/kya_ap_link.py` | Archipelago connection/check bridge |
| `launcher/kya_shop_native.py` | Native shop item identification and sold-state handling |
| `launcher/kya_map_guard.py` | Context-sensitive map/camera route safety |
| `launcher/kya_auto_save.py` | Save-state support |
| `apworld/kya_dark_lineage/world.py` | World generation, locations, region graph |
| `apworld/kya_dark_lineage/options.py` | Game-specific YAML configuration |
| `apworld/kya_dark_lineage/constants.py` | AP location and item constants |

See individual files for exact implementation. All address data here is specific to the tested PAL game version.
