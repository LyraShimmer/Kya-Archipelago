"""Read-only Brazul capture/return state machine, Kya PAL SLES-51473.

Evidence: own scanner report 2026-10-30 16:18-16:21 (vanilla, launcher off).
At seizure: bracelet gains bit 0x10000; items, Receptacle, six Runes,
magic gauge vanish. About 17 seconds later ScenarioVar 57 changes 0->1.
At vanilla pickup: bracelet loses bit, Boomy and Magic Bouncers return,
while Runes, Receptacle and magic gauge remain removed.

No writes. This is a *candidate* using one full capture trace; test on real PCSX2.
"""
from __future__ import annotations

class BrazulCaptureGuard:
    BRACELET = 0x00425424
    BOOMY = 0x0042541C
    BOUNCERS = 0x0042540C
    STORY_57 = 0x0042559C
    CAPTURE_BIT = 0x00010000

    def __init__(self):
        self.phase = "normal"

    @property
    def captive(self):
        return self.phase == "captive"

    @property
    def recovered(self):
        return self.phase == "recovered"

    def poll(self, pine):
        """Return normal / captive / recovered from *only* native reads.

        ScenarioVar 57 persists through gear pickup (verified in scanner);
        the high bracelet bit identifies active seizure even before SV57 flips.
        If a pre-capture savestate is loaded, SV57 resets to 0 and so does us.
        """
        bracelet = int(pine.read32(self.BRACELET))
        story = int(pine.read32(self.STORY_57))
        if bracelet & self.CAPTURE_BIT:
            self.phase = "captive"
            return self.phase
        if story == 0:
            self.phase = "normal"
            return self.phase
        # Once the story flag is present, vanilla's equipment return is seen
        # via two independent fields, NOT inferred from the cage breaking.
        boomy = int(pine.read32(self.BOOMY))
        bouncers = int(pine.read32(self.BOUNCERS))
        if boomy > 0 and bouncers > 0:
            self.phase = "recovered"
        else:
            self.phase = "captive"
        return self.phase

    def defer_ap_item(self, name, game_data):
        if self.captive:
            if name in game_data.get("ITEM_MONEY_VALUES", {}):
                return False
            if name in game_data.get("ITEM_HP_RESTORE_AMOUNTS", {}):
                return False
            if name in game_data.get("ITEM_MAGIC_RESTORE_AMOUNTS", {}):
                return False
            if name in game_data.get("ITEM_COMBAT_BONUSES", {}):
                return False
            if name in ("Wolfen City Access", "The Fortress Access"):
                return False
            # Equipment and permanent magic progress cannot bypass captivity.
            return name != "Unknown item"
        if self.recovered:
            # Runes and Receptacle stay removed by the vanilla story after the
            # gear-return cutscene, regardless of prior AP inventory ownership.
            return name.startswith("Progressive Rune: ") or name in (
                "Receptacle", game_data.get("ITEM_PROGRESSIVE_MAGIC_GAUGE")
            ) or name in game_data.get("ITEM_RUNE_SCENARIO_VARS", {})
        return False
