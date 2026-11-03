# Kya: Dark Lineage — Archipelago setup

**Release milestone:** `9.0.0-beta1`  
**APWorld implementation:** `0.8.14`  
**Launcher implementation:** `0.9.63`  
**Minimum Archipelago version:** `0.6.7`  
**Game:** PAL PS2 `SLES-51473`, through PCSX2 and PINE.

The previous standalone setup instructions in this directory referred to much older APWorld and Launcher versions. For the current beta, use these canonical guides instead:

- [Complete player installation](../../../docs/installation.md)
- [YAML options and defaults](../../../docs/configuration.md)
- [Known issues](../../../docs/known_issues.md)
- [Version and compatibility notes](../../../docs/versions.md)

## Summary

1. Install the `kya_dark_lineage.apworld` file in Archipelago.
2. In PCSX2 enable PINE at `127.0.0.1:28011`.
3. Under **Settings → Graphics → Rendering**, select **Vulkan** instead of **Software Renderer**; enable **Load Textures** in the **Texture Replacement** settings.
4. Edit the provided `Kya_Dark_Lineage.yaml`, especially the player `name`, and generate a new multiworld locally.
5. Extract `Launcher.zip`, keep its files together, run the game in PCSX2, start the Launcher, and connect to the room.

The default Fast Travel mode is `archipelago`, with six starting destinations and both late-game lift locks enabled. Nooties and shop-price modifiers both default to `0%`. Progression gating, memory monitoring, shop flags, and Final Goal logic remain governed by the shipped APWorld and Launcher code.

No game ISO is included. The integration supports the documented PAL version only.
