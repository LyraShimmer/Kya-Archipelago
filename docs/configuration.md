# Archipelago YAML configuration

Download `Kya_Dark_Lineage.yaml` from the release. Edit the **player name** and any optional world settings, then submit it to the person generating the multiworld or put it in Archipelago's `Players/` directory for local generation.

The sample provided with the beta contains:

```yaml
name: Kya
description: Kya Archipelago beta - default settings
game: 'Kya: Dark Lineage'
'Kya: Dark Lineage':
  progression_balancing: normal
  accessibility: full
  fast_travel: archipelago
  fast_travel_progression: archipelago
  starting_fast_travels: 6
  lock_wolfen_city: true
  lock_the_fortress: true
  ap_nooties_modifier: 0
  shop_price_modifier: 0
  local_items: []
  non_local_items: []
  start_inventory: {}
  start_hints: []
  start_location_hints: []
  exclude_locations: []
  priority_locations: []
```

**Important:** `name` must match the player's exact slot name. The `game` identifier and the `'Kya: Dark Lineage'` options block should not be renamed.

## Game-specific settings

| YAML key | Default | Meaning |
| --- | --- | --- |
| `fast_travel_progression` | `archipelago` | `archipelago` uses randomized starting access; `vanilla` follows the original game's progression |
| `fast_travel` | `archipelago` | Compatibility alias for YAML creators; use the same value as `fast_travel_progression` |
| `starting_fast_travels` | `6` | Number of unique starting destinations, from `1` to `6` when using Archipelago progression |
| `lock_wolfen_city` | `true` | Requires the randomized access item to use the Wolfen City elevator |
| `lock_the_fortress` | `true` | Requires the randomized access item to use the Fortress elevator |
| `ap_nooties_modifier` | `0` | Modifier to Nooties awarded by AP rewards, from `-100` to `1000` in steps of 10 |
| `shop_price_modifier` | `0` | Modifier to the 18 AP shop prices, from `-100` to `1000` in steps of 10 |

The economy convention is **`0` = unchanged**, `-100` = zero/free, `100` = double, and `1000` = eleven times the original value. These affect the relevant Archipelago mechanisms, not every transaction in the original game.

The available settings are defined in [`options.py`](../apworld/kya_dark_lineage/options.py). The release label is `9.0.0-beta1`, while the actual APWorld implementation remains `0.8.14` for compatibility; see [versions](versions.md).

## Generating and joining

1. Install the APWorld using **Install APWorld** in the Archipelago Launcher.
2. Put each player's YAML into the `Players` folder of the Archipelago installation used to generate the seed.
3. Generate a new multiworld locally, and host/join it using Archipelago's standard procedure.
4. In the Kya Launcher, connect to the room with its host address, slot name, and password if required.

See the complete [player installation guide](installation.md) for PCSX2/PINE and graphics configuration.
