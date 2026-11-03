from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle


class TenPercentStepRange(Range):
    """Range normalized to 10-point percentage steps.

    Archipelago's Range UI accepts arbitrary integers. Kya economy modifiers are
    intentionally kept on a -100, -90, ... +990, +1000 grid so the generated
    values stay readable and deterministic. Values between two steps are rounded
    to the nearest 10, with .5 rounded away from zero.
    """

    step = 10

    def __init__(self, value: int):
        value = int(value)
        if value >= 0:
            value = ((value + 5) // self.step) * self.step
        else:
            value = -(((-value + 5) // self.step) * self.step)
        value = max(self.range_start, min(self.range_end, value))
        super().__init__(value)


class APNootiesModifier(TenPercentStepRange):
    """Changes Nooties received from Archipelago Nooties rewards.

    Uses 10% steps. 0 keeps the normal AP reward value, -100 makes AP Nooties
    rewards give 0, +100 doubles them and +1000 makes them worth x11.
    """

    display_name = "AP Nooties Modifier (%)"
    range_start = -100
    range_end = 1000
    default = 0


class ShopPriceModifier(TenPercentStepRange):
    """Changes the prices of the 18 one-time AP Shop items.

    Uses 10% steps. 0 keeps vanilla prices, -100 makes those items free,
    +100 doubles their prices and +1000 makes them cost x11.
    """

    display_name = "Shop Price Modifier (%)"
    range_start = -100
    range_end = 1000
    default = 0


class FastTravelProgression(Choice):
    """How Fast Travel access is handled.

    Archipelago: the seed chooses a configurable number of unique destination
    zones that are available from Nativs City immediately.
    Vanilla: no AP Fast Travel injection; Kya follows the normal game order.
    """

    display_name = "Fast Travel Progression"
    option_archipelago = 0
    option_vanilla = 1
    default = 0


class StartingFastTravels(Range):
    """Number of unique destination zones opened at the start in AP mode.

    The first beta deliberately limits this to one destination per zone. This
    avoids the confirmed/observed same-zone sequential-teleport instability.
    """

    display_name = "Starting Fast Travels"
    range_start = 1
    range_end = 6
    default = 6


class LockWolfenCity(Toggle):
    """Require the randomized Wolfen City Access to use The Quarry lift."""
    display_name = "Lock Wolfen City Elevator"
    default = 1


class LockTheFortress(Toggle):
    """Require the randomized Fortress Access to use the Wolfen City lift."""
    display_name = "Lock The Fortress Elevator"
    default = 1


class KyaFastTravelCreatorCompatibility(Choice):
    """YAML Creator compatibility: auto uses the original FT progression option."""
    display_name = "Fast Travel Mode (Creator Alias)"
    option_auto = 0
    option_archipelago = 1
    option_vanilla = 2
    default = option_auto


@dataclass
class KyaDarkLineageOptions(PerGameCommonOptions):
    fast_travel: KyaFastTravelCreatorCompatibility
    fast_travel_progression: FastTravelProgression
    starting_fast_travels: StartingFastTravels
    lock_wolfen_city: LockWolfenCity
    lock_the_fortress: LockTheFortress
    ap_nooties_modifier: APNootiesModifier
    shop_price_modifier: ShopPriceModifier
