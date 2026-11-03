from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import set_rule, add_item_rule

from .options import KyaDarkLineageOptions

from .constants import (
    GAME_NAME,
    ITEM_PROGRESSIVE_BOOMY,
    ITEM_PROGRESSIVE_BRACELET,
    ITEM_PROGRESSIVE_BOARD,
    ITEM_MAGIC_BOUNCERS,
    ITEM_CLIMBING_GLOVES,
    ITEM_JAMGUT,
    ITEM_WOLFEN_CITY_ACCESS,
    ITEM_FORTRESS_ACCESS,
    ITEM_NAME_TO_ID,
    ITEM_REWARD_COUNTS,
    ITEM_PROGRESSION_COUNTS,
    ITEM_USEFUL,
    ITEM_MONEY_VALUES,
    ITEM_HP_RESTORE_AMOUNTS,
    ITEM_MAGIC_RESTORE_AMOUNTS,
    ITEM_RUNES,
    LOCATION_NAME_TO_ID,
    LOCATION_NAMES_BY_ZONE,
    PROTOTYPE_VERSION,
    SPECIAL_LOCATION_CONDITIONS,
    SHOP_LOCATION_CONDITIONS,
    FAST_TRAVEL_LOCATION_ZONES,
    STARTER_LOCATION_NAME,
    WOLFEN_ZONE_KEY_TO_LOCATION,
    WOLFEN_LOCATIONS_BY_ZONE,
    ZONE_ORDER,
    BRACELET_ZONE_LOCATIONS,
    EARLY_ZONE_FORBIDDEN_ITEMS,
    MID_ZONE_FORBIDDEN_ITEMS,
    SHOP_UNLOCK_GROUPS,
    FAST_TRAVEL_ALLOWED_ROUTES,
)


class KyaItem(Item):
    game = GAME_NAME


class KyaLocation(Location):
    game = GAME_NAME


class KyaWeb(WebWorld):
    game_info_languages = []
    theme = "ocean"
    tutorials = [
        Tutorial(
            "Demo Setup Guide",
            "PAL SLES_514.73 PCSX2/PINE Archipelago demo setup.",
            "English",
            "setup_en.md",
            "setup/en",
            ["Kya Archipelago project"],
        )
    ]


class KyaDarkLineageWorld(World):
    """Kya: Dark Lineage PAL SLES_514.73 validation/balance playtest."""

    game = GAME_NAME
    web = KyaWeb()
    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    options_dataclass = KyaDarkLineageOptions
    options: KyaDarkLineageOptions

    def _effective_ft_value(self) -> int:
        """Preserve original FT options; also accept current Creator's fast_travel."""
        alias = int(self.options.fast_travel.value)
        if alias == 2:  # vanilla
            return 1
        if alias == 1:  # archipelago
            return 0
        return int(self.options.fast_travel_progression.value)

    def generate_early(self) -> None:
        """Choose the beta starting Fast Travels once, deterministically per seed."""
        self.starting_fast_travel_routes = []
        if int(self._effective_ft_value()) != 0:
            return

        zones = list(FAST_TRAVEL_ALLOWED_ROUTES)
        count = max(1, min(len(zones), int(self.options.starting_fast_travels.value)))

        # In AP-FT mode BOTH normal Nativ exits are always locked.  Keep the
        # validated Flying Forest FT01 among starting routes so small FT counts
        # never strand Kya behind two closed entrances.  The remaining FT01
        # starting destinations are randomized normally.
        if "Flying Forest" not in zones:
            raise ValueError("No validated Flying Forest FT01; cannot safely lock both Nativ exits")
        chosen_zones = ["Flying Forest"]
        remaining = [zone for zone in zones if zone != "Flying Forest"]
        chosen_zones.extend(self.random.sample(remaining, count - 1))

        # Only FT01 destinations have a documented early-access terrain route.
        # Never seed FT02/03/04 as entry points until their physical start
        # position and return safety have been mapped separately.
        for zone in chosen_zones:
            primary = next(
                (r for r in FAST_TRAVEL_ALLOWED_ROUTES[zone] if int(r["source_index"]) == 0),
                None,
            )
            if primary is None:
                raise ValueError(f"No validated FT01 route for {zone}")
            self.starting_fast_travel_routes.append(dict(primary))

    def create_item(self, name: str) -> KyaItem:
        if (name in ITEM_MONEY_VALUES or name in ITEM_HP_RESTORE_AMOUNTS or name in ITEM_MAGIC_RESTORE_AMOUNTS
                or name.startswith(("Nooties +", "HP Restore +", "Magic Restore +"))):
            classification = ItemClassification.filler
        elif name in ITEM_USEFUL:
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.progression
        return KyaItem(name, classification, self.item_name_to_id[name], self.player)

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        regions = {}
        for zone in ZONE_ORDER:
            region = Region(zone, self.player, self.multiworld)
            regions[zone] = region
            for location_name in LOCATION_NAMES_BY_ZONE[zone]:
                region.locations.append(
                    KyaLocation(self.player, location_name, self.location_name_to_id[location_name], region)
                )
        self.multiworld.regions.append(menu)
        self.multiworld.regions.extend(regions.values())

        # 0.7.8 route graph from the live validation run. The Root is reachable
        # before Jamgut/Hunters progression, so it is deliberately a parallel
        # branch from Flying Forest rather than only a post-Quarry destination.
        menu.connect(regions["Nativs City"])

        fast_travel_vanilla = int(self._effective_ft_value()) == 1
        # 0.8.10: these locks are derived from FT mode, never selectable.
        effective_lock_flying = not fast_travel_vanilla
        effective_lock_root = not fast_travel_vanilla
        starting_zones = (
            set()
            if fast_travel_vanilla
            else {route["zone"] for route in getattr(self, "starting_fast_travel_routes", [])}
        )

        # Vanilla mode keeps the established game-order graph. In AP mode the two
        # Nativs City exits can be physically locked and logic follows that lock.
        # If a zone is already a starting Fast Travel destination, the unconditional
        # AP route is authoritative and we deliberately avoid creating a duplicate
        # conditional Nativs City entrance to the same Region.
        if (fast_travel_vanilla or not effective_lock_flying) and "Flying Forest" not in starting_zones:
            regions["Nativs City"].connect(
                regions["Flying Forest"],
                rule=lambda state: True,
            )
        if (not fast_travel_vanilla) and not effective_lock_root and "The Root" not in starting_zones:
            regions["Nativs City"].connect(
                regions["The Root"],
                rule=lambda state, p=self.player: state.has(ITEM_PROGRESSIVE_BOOMY, p, 1),
            )

        # Starting AP Fast Travels are real seed routes, so generation must treat
        # their destination regions as reachable from Nativs City immediately.
        if not fast_travel_vanilla:
            for route in getattr(self, "starting_fast_travel_routes", []):
                regions["Nativs City"].connect(regions[route["zone"]])

        ff_exit = lambda state, p=self.player: (
            state.has(ITEM_PROGRESSIVE_BOARD, p, 1)
            and state.has(ITEM_CLIMBING_GLOVES, p)
        )
        regions["Flying Forest"].connect(regions["Hunters Domain"], rule=ff_exit)
        regions["Flying Forest"].connect(regions["The Root"], rule=ff_exit)

        # Wind Tower: Bouncers are required, Silver is explicitly NOT a
        # prerequisite in the player's terrain notes. Quarry has its own FT01;
        # normal Hunter->Quarry passage is later, but we must not require Silver
        # merely to reach Wind Tower.
        regions["Hunters Domain"].connect(
            regions["Wind Tower"],
            rule=lambda state, p=self.player:
                state.has(ITEM_JAMGUT, p) and state.has(ITEM_MAGIC_BOUNCERS, p),
        )
        regions["Hunters Domain"].connect(
            regions["The Quarry"],
            rule=lambda state, p=self.player:
                state.has(ITEM_JAMGUT, p)
                and state.has(ITEM_CLIMBING_GLOVES, p)
                and state.has(ITEM_PROGRESSIVE_BOARD, p, 2),
        )
        regions["The Quarry"].connect(
            regions["Amber Quarry"],
            rule=lambda state, p=self.player:
                state.has(ITEM_PROGRESSIVE_BOARD, p, 2)
                and state.has(ITEM_CLIMBING_GLOVES, p),
        )
        regions["Amber Quarry"].connect(regions["The Root"])

        # 0.7.9 hard deadline gate. The validation run showed that both Jamgut
        # and the second Progressive Board (Speed Board) must already be owned
        # before normal progression can continue beyond The Root. Golden Boomy
        # remains the vanilla Air Post wall. This prevents AP from considering
        # The Air Post (or anything later) a legal source for either blocker.
        regions["The Root"].connect(
            regions["The Air Post"],
            rule=lambda state, p=self.player: (
                state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                and state.has(ITEM_JAMGUT, p)
                and state.has(ITEM_PROGRESSIVE_BOARD, p, 2)
                and state.has(ITEM_CLIMBING_GLOVES, p)
            ),
        )
        regions["The Air Post"].connect(regions["Forgotten Island"])

        # Vanilla Wolfen City entrance requires 350 max magic. In AP, each of the
        # six Rune items contributes +50 on top of the 50 base gauge, so requiring
        # Receptacle + all six Runes models the confirmed 350-mana wall directly.
        # Physical entrance is the lift in The Quarry, not a bridge out of
        # Forgotten Island. Runes are randomized AP items but activate the
        # confirmed vanilla ScenarioVars and 350-mana threshold at runtime.
        city_gate = lambda state, p=self.player: (
            state.has("Receptacle", p)
            and all(state.has(rune, p) for rune in ITEM_RUNES)
            and (not bool(self.options.lock_wolfen_city.value)
                 or fast_travel_vanilla or state.has(ITEM_WOLFEN_CITY_ACCESS, p))
        )
        regions["The Quarry"].connect(regions["Wolfen City"], rule=city_gate)
        regions["Wolfen City"].connect(
            regions["The Fortress"],
            rule=lambda state, p=self.player:
                (not bool(self.options.lock_the_fortress.value)
                 or fast_travel_vanilla or state.has(ITEM_FORTRESS_ACCESS, p)),
        )

    def create_items(self) -> None:
        progression = [
            name
            for name, amount in ITEM_PROGRESSION_COUNTS.items()
            for _ in range(amount)
        ]

        pool_slots = len(self.location_name_to_id)

        # The story awards Basic Boomy after the opening Wolfen.
        # Never precollect or lock ANY Boomy item to that tutorial check.
        # AP Progressive Boomy contains only the later two upgrades.
        # 0.8.9: NO early_items overrides. The Archipelago restrictive filler
        # chooses reachable checks in the ACTUAL graph for this seed, including
        # alternate starting FT01 zones. Hard-forcing Board/Gloves to early
        # global spheres artificially biases one region's first checks.
        # Critical locations that can disappear (rune pickups), and unmodelled
        # shop affordability, retain their independent safety item rules.

        # Seven bracelet upgrades -> one in each principal adventure zone.
        for location_name in BRACELET_ZONE_LOCATIONS:
            location = self.multiworld.get_location(location_name, self.player)
            location.place_locked_item(self.create_item(ITEM_PROGRESSIVE_BRACELET))
            progression.remove(ITEM_PROGRESSIVE_BRACELET)
            pool_slots -= 1

        useful_rewards = [
            name
            for name, amount in ITEM_REWARD_COUNTS.items()
            for _ in range(amount)
        ]

        filler_count = pool_slots - len(progression) - len(useful_rewards)
        if filler_count < 0:
            raise ValueError(
                f"Kya 0.8.4 pool has {len(progression) + len(useful_rewards)} fixed random items "
                f"for only {pool_slots} random locations."
            )

        # Richer rewards than the broken 0.8.3 all-Nooties generator.
        # A good number of smaller Nooties rewards remains to fund shops;
        # the rest is legitimate HP/Magic restoration from the original items.
        nooties_count = (filler_count * 45) // 100
        recovery_count = filler_count - nooties_count
        hp_count = recovery_count // 2
        magic_count = recovery_count - hp_count
        money_names = list(ITEM_MONEY_VALUES)
        money_weights = (35, 30, 20, 10, 5)
        money_counts = [nooties_count * weight // 100 for weight in money_weights]
        money_counts[0] += nooties_count - sum(money_counts)
        pool = progression + useful_rewards
        for name, amount in zip(money_names, money_counts):
            pool.extend([name] * amount)
        hp_names = list(ITEM_HP_RESTORE_AMOUNTS)
        magic_names = list(ITEM_MAGIC_RESTORE_AMOUNTS)
        pool.extend(hp_names[i % len(hp_names)] for i in range(hp_count))
        pool.extend(magic_names[i % len(magic_names)] for i in range(magic_count))
        self.random.shuffle(pool)

        self.multiworld.itempool += [self.create_item(name) for name in pool]

    def set_rules(self) -> None:
        p = self.player
        fast_travel_vanilla = int(self._effective_ft_value()) == 1

        def loc(name: str):
            return self.multiworld.get_location(name, p)

        # Lava Worm detector is still an in-game beta hypothesis. Its check
        # must never hold progression, but useful rewards (e.g. +5% Protection)
        # are safe. Requiring filler ONLY can strand the restrictive fill when
        # its last unplaced reward is classified as useful.
        if 'Flying Forest - Lava Worm Defeated' in self.location_name_to_id:
            add_item_rule(
                loc('Flying Forest - Lava Worm Defeated'),
                lambda item: not item.advancement,
            )

        # 0.8.14 BETA FT SAFETY: no player's progression/key item may be
        # placed on any Fast Travel location until replay after a savestate or
        # reconnect has been causally validated.  A known FT native key or an
        # already-active pad at baseline is NOT a reliable purchase/check edge.
        # Safe pads remain optional checks with filler/useful rewards.
        for ft_name in sorted(FAST_TRAVEL_LOCATION_ZONES):
            if ft_name in self.location_name_to_id:
                add_item_rule(loc(ft_name), lambda item: not item.advancement)

        # The first Wolfen is the story Boomy tutorial: AP Boomy upgrades
        # must never fire during the whistle/cutscene.
        add_item_rule(
            loc(STARTER_LOCATION_NAME),
            lambda item, p=p: item.player != p or item.name != ITEM_PROGRESSIVE_BOOMY,
        )

        # 0.8.9: No zone whitelist for Board, Gloves, Jamgut or Receptacle.
        # Their placement must be determined by the reachable AP graph, not by
        # game-order/zone bans. An AP seed opening The Quarry from the start
        # may reward Gloves at its first Wolfen; a vanilla FT seed cannot.
        # Remaining placement restrictions below defend REAL runtime hazards.

        # TERRAIN 26-28 OCT: FF 01-16 without advanced gear; 17-23
        # after Magic Board; 24-25 after Climbing Gloves. The late FF
        # suffix is conservatively assigned Board + Gloves until individually
        # measured, without pretending these are exclusive requirements.
        for n in range(17, 24):
            set_rule(loc(WOLFEN_LOCATIONS_BY_ZONE["Flying Forest"][n - 1]),
                     lambda state, p=p: state.has(ITEM_PROGRESSIVE_BOARD, p, 1))
        for n in range(24, 38):
            set_rule(loc(WOLFEN_LOCATIONS_BY_ZONE["Flying Forest"][n - 1]),
                     lambda state, p=p:
                         state.has(ITEM_PROGRESSIVE_BOARD, p, 1)
                         and state.has(ITEM_CLIMBING_GLOVES, p))

        # Root 01-05 accessible with Basic Boomy; Magic Board made no
        # difference; Gloves released 06-07 (observed in the FT01 run).
        for n in (6, 7):
            set_rule(loc(WOLFEN_LOCATIONS_BY_ZONE["The Root"][n - 1]),
                     lambda state, p=p: state.has(ITEM_CLIMBING_GLOVES, p))

        # Conservative FT rules: the keys/numbers are now corrected; these
        # reachability rules avoid letting a late teleporter create a logic shortcut.
        for ft_name in ("Flying Forest - Fast Travel 02", "Flying Forest - Fast Travel 03"):
            if ft_name in self.location_name_to_id:
                set_rule(loc(ft_name), lambda state, p=p: state.has(ITEM_PROGRESSIVE_BOARD, p, 1))
        if "Flying Forest - Fast Travel 04" in self.location_name_to_id:
            set_rule(
                loc("Flying Forest - Fast Travel 04"),
                lambda state, p=p:
                    state.has(ITEM_PROGRESSIVE_BOARD, p, 1)
                    and state.has(ITEM_CLIMBING_GLOVES, p),
            )

        # Receptacle is physically required to pick up any Rune.
        set_rule(
            loc("Flying Forest - Flying Forest's Rune"),
            lambda state, p=p:
                state.has("Receptacle", p)
                and state.has(ITEM_PROGRESSIVE_BOARD, p, 1)
                and state.has(ITEM_CLIMBING_GLOVES, p),
        )
        set_rule(
            loc("Flying Forest - HP Upgrade"),
            lambda state, p=p:
                state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                and state.has(ITEM_CLIMBING_GLOVES, p),
        )

        # Hunters Domain: lateral winds allow an alternate path without Gloves
        # (player reconfirmed 29 October). Wolfen 03-25 tentatively require
        # only Birdcall; 26-46 retain Gloves conservatively until the exact
        # bypass end and each late section have been validated separately.
        # Silver/Bouncers requirements stay provisional for the late portion.
        for n in range(1, 47):
            def hd_rule(state, number=n, p=p):
                if not state.has(ITEM_JAMGUT, p):
                    return False
                if number >= 26 and not state.has(ITEM_CLIMBING_GLOVES, p):
                    return False
                if number >= 26 and not state.has(ITEM_PROGRESSIVE_BOOMY, p, 1):
                    return False
                if number >= 29 and not state.has(ITEM_MAGIC_BOUNCERS, p):
                    return False
                return True
            set_rule(loc(WOLFEN_LOCATIONS_BY_ZONE["Hunters Domain"][n - 1]), hd_rule)

        # Wind Tower Wolfen need Bouncers, not Silver. Entry route is
        # independently Bouncers-gated in create_regions().
        for wolfen_name in WOLFEN_LOCATIONS_BY_ZONE["Wind Tower"]:
            set_rule(loc(wolfen_name),
                     lambda state, p=p: state.has(ITEM_MAGIC_BOUNCERS, p))

        # FT01 is physically reachable at Hunters entrance before Jamgut.
        # FT02..05 are treated as Jamgut-section checks; FT06 is in the advanced section.
        for ft_name in (
            "Hunters Domain - Fast Travel 02",
            "Hunters Domain - Fast Travel 03",
            "Hunters Domain - Fast Travel 04",
            "Hunters Domain - Fast Travel 05",
        ):
            if ft_name in self.location_name_to_id:
                set_rule(loc(ft_name), lambda state, p=p: state.has(ITEM_JAMGUT, p))
        if "Hunters Domain - Fast Travel 06" in self.location_name_to_id:
            set_rule(
                loc("Hunters Domain - Fast Travel 06"),
                lambda state, p=p: state.has(ITEM_JAMGUT, p) and state.has(ITEM_CLIMBING_GLOVES, p) and state.has(ITEM_MAGIC_BOUNCERS, p),
            )

        set_rule(
            loc("Hunters Domain - Hunter's Domain's Rune"),
            lambda state, p=p:
                state.has("Receptacle", p)
                and state.has(ITEM_JAMGUT, p)
                and state.has(ITEM_CLIMBING_GLOVES, p)
                and state.has(ITEM_MAGIC_BOUNCERS, p),
        )
        if "Hunters Domain - Boss Defeated" in self.location_name_to_id:
            set_rule(
                loc("Hunters Domain - Boss Defeated"),
                lambda state, p=p: state.has(ITEM_JAMGUT, p) and state.has(ITEM_CLIMBING_GLOVES, p) and state.has(ITEM_MAGIC_BOUNCERS, p),
            )

        # TERRAIN CONFIRMED 2026-10-30: The Quarry Wolfen 01 is the ONLY
        # Wolfen reachable from the early FT01 area without Climbing Gloves.
        # Wolfen 02-10 require Gloves AT MINIMUM. Additional prerequisites for
        # individuals 02-10 have not been isolated; never claim Gloves alone
        # guarantee their physical reachability. Number is the user's route
        # progression numbering, NOT a count of previously rescued actors.
        for n in range(2, 11):
            set_rule(
                loc(WOLFEN_LOCATIONS_BY_ZONE["The Quarry"][n - 1]),
                lambda state, p=p: state.has(ITEM_CLIMBING_GLOVES, p),
            )

        # The Quarry terrain, FT01 run: 01-10 seen before session (do not
        # claim all are zero-item), 11-13 require Gloves + King Jamgut
        # event; 14-19 BEFORE Speed Board; 20-21 after Speed Board;
        # 22-31 after Magic Bouncers. Jamgut/Gloves are conservative
        # prerequisites for 11+; event cannot be asserted from AP item state.
        for n in range(11, 32):
            def quarry_rule(state, number=n, p=p):
                return (state.has(ITEM_JAMGUT, p)
                        and state.has(ITEM_CLIMBING_GLOVES, p)
                        and (number < 20 or state.has(ITEM_PROGRESSIVE_BOARD, p, 2))
                        and (number < 22 or state.has(ITEM_MAGIC_BOUNCERS, p)))
            set_rule(loc(WOLFEN_LOCATIONS_BY_ZONE["The Quarry"][n - 1]), quarry_rule)
        # Amber Quarry: entrance requires Speed+Gloves. No individual
        # 14-Wolfen sequence was captured (mapper failed), so hold their
        # checks conservatively until Bouncers too; no fabricated cutpoint.
        for name in WOLFEN_LOCATIONS_BY_ZONE["Amber Quarry"]:
            set_rule(loc(name), lambda state, p=p:
                     state.has(ITEM_PROGRESSIVE_BOARD, p, 2)
                     and state.has(ITEM_CLIMBING_GLOVES, p)
                     and state.has(ITEM_MAGIC_BOUNCERS, p))

        # The Air Post: known early samples only. A FT01 start must not
        # magically expose 61 checks when Golden/Gloves/Bouncers are absent.
        # Unmeasured Wolfen are conservatively gated to the late gear set.
        air_names = WOLFEN_LOCATIONS_BY_ZONE["The Air Post"]
        early_air = {3}  # actual Dark Island #03 before Golden
        golden_air = {1, 2, 28, 29}
        last_air = {30, 31, 32, 33}
        for n, name in enumerate(air_names, 1):
            if n in early_air:
                continue
            if n in golden_air:
                set_rule(loc(name), lambda state, p=p: state.has(ITEM_PROGRESSIVE_BOOMY, p, 2))
            elif n in last_air:
                set_rule(loc(name), lambda state, p=p:
                         state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                         and state.has(ITEM_CLIMBING_GLOVES, p)
                         and state.has(ITEM_MAGIC_BOUNCERS, p))
            else:
                set_rule(loc(name), lambda state, p=p:
                         state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                         and state.has(ITEM_CLIMBING_GLOVES, p)
                         and state.has(ITEM_MAGIC_BOUNCERS, p)
                         and state.has(ITEM_PROGRESSIVE_BOARD, p, 2)
                         and state.has(ITEM_JAMGUT, p))

        # Forgotten Island is not individually audited: apply conservative
        # late-mobility requirements instead of inventing an 'all free' zone.
        for name in WOLFEN_LOCATIONS_BY_ZONE["Forgotten Island"]:
            set_rule(loc(name), lambda state, p=p:
                     state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                     and state.has(ITEM_CLIMBING_GLOVES, p)
                     and state.has(ITEM_MAGIC_BOUNCERS, p)
                     and state.has(ITEM_PROGRESSIVE_BOARD, p, 2))

        # Non-Wolfen locations also require physical access. A selected
        # Nativ FT01 does not grant every other pad/map/event in the zone.
        for ft_name in ("The Root - Fast Travel 02", "The Root - Fast Travel 03"):
            if ft_name in self.location_name_to_id:
                set_rule(loc(ft_name), lambda state, p=p: state.has(ITEM_CLIMBING_GLOVES, p))
        for ft_name in ("The Quarry - Fast Travel 02", "The Quarry - Fast Travel 03"):
            if ft_name in self.location_name_to_id:
                set_rule(loc(ft_name), lambda state, p=p:
                         state.has(ITEM_CLIMBING_GLOVES, p)
                         and state.has(ITEM_PROGRESSIVE_BOARD, p, 2))
        for ft_name in ("The Air Post - Fast Travel 02", "The Air Post - Fast Travel 03", "The Air Post - Fast Travel 04", "The Air Post - Map Discovery"):
            if ft_name in self.location_name_to_id:
                set_rule(loc(ft_name), lambda state, p=p:
                         state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                         and state.has(ITEM_CLIMBING_GLOVES, p)
                         and state.has(ITEM_MAGIC_BOUNCERS, p)
                         and state.has(ITEM_PROGRESSIVE_BOARD, p, 2))
        for ft_name in ("Forgotten Island - Fast Travel 02", "Forgotten Island - Fast Travel 03", "Forgotten Island - Fast Travel 04", "Forgotten Island - Map Discovery", "Forgotten Island - Frank Exorcised"):
            if ft_name in self.location_name_to_id:
                set_rule(loc(ft_name), lambda state, p=p:
                         state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                         and state.has(ITEM_CLIMBING_GLOVES, p)
                         and state.has(ITEM_MAGIC_BOUNCERS, p)
                         and state.has(ITEM_PROGRESSIVE_BOARD, p, 2))
        # 0.8.12: the local Amber pad is a CHECK, not an AP-enabled route.
        # Physical Amber access follows the same terrain gates as its first
        # Brazul encounter; this does not introduce any additional graph edge.
        if "Amber Quarry - Fast Travel 01" in self.location_name_to_id:
            set_rule(loc("Amber Quarry - Fast Travel 01"),
                     lambda state, p=p: state.has(ITEM_PROGRESSIVE_BOARD, p, 2)
                     and state.has(ITEM_CLIMBING_GLOVES, p)
                     and state.has(ITEM_MAGIC_BOUNCERS, p))
        if "Amber Quarry - Brazul First Encounter" in self.location_name_to_id:
            set_rule(loc("Amber Quarry - Brazul First Encounter"),
                     lambda state, p=p: state.has(ITEM_PROGRESSIVE_BOARD, p, 2)
                     and state.has(ITEM_CLIMBING_GLOVES, p)
                     and state.has(ITEM_MAGIC_BOUNCERS, p))

        # The six VANILLA Rune pickup checks require Receptacle (pickup
        # condition) AND the documented physical route. AP Rune items remain
        # independently shuffled to different locations; the Launcher writes
        # the native ScenarioVars / max mana on receipt.
        rune_requirements = {
            "Flying Forest - Flying Forest's Rune": (1, 1, 0, 0),
            "The Root - Root's Rune": (0, 1, 0, 0),
            "Hunters Domain - Hunter's Domain's Rune": (0, 1, 1, 1),
            "The Quarry - Quarry's Rune": (2, 1, 1, 1),
            "The Air Post - Air Post's Rune": (2, 1, 1, 0),
            "Forgotten Island - Forgotten Island's Rune": (2, 1, 1, 0),
        }
        for rune_location, (board, gloves, bouncers, jamgut) in rune_requirements.items():
            def rune_rule(state, board=board, gloves=gloves,
                          bouncers=bouncers, jamgut=jamgut, p=p):
                return (state.has("Receptacle", p)
                        and (board == 0 or state.has(ITEM_PROGRESSIVE_BOARD, p, board))
                        and (not gloves or state.has(ITEM_CLIMBING_GLOVES, p))
                        and (not bouncers or state.has(ITEM_MAGIC_BOUNCERS, p))
                        and (not jamgut or state.has(ITEM_JAMGUT, p)))
            set_rule(loc(rune_location), rune_rule)

        # Rune item receipt writes the same persistent ScenarioVar used by the
        # physical pickup. Receiving a Rune early can therefore remove its pickup.
        # Until a source-distinct pickup trigger is found, Rune locations may hold
        # filler/useful items only, never progression for any player.
        for rune_location in (
            "Flying Forest - Flying Forest's Rune",
            "The Root - Root's Rune",
            "Hunters Domain - Hunter's Domain's Rune",
            "The Quarry - Quarry's Rune",
            "The Air Post - Air Post's Rune",
            "Forgotten Island - Forgotten Island's Rune",
        ):
            add_item_rule(loc(rune_location), lambda item: not item.advancement)

        # ------------------------------------------------------------------
        # Vanilla shop stock — exact BWITCH.INI MinWolfen thresholds.
        # We count how many Wolfen Locations are logically reachable with the
        # current CollectionState. This directly prevents circular shop placement.
        # ------------------------------------------------------------------
        all_wolfen_locations = tuple(
            name
            for zone in ZONE_ORDER
            for name in WOLFEN_LOCATIONS_BY_ZONE.get(zone, ())
        )

        def can_reach_wolfen_count(state, required: int, p=p) -> bool:
            reached = 0
            for wolfen_name in all_wolfen_locations:
                if state.can_reach(wolfen_name, "Location", p):
                    reached += 1
                    if reached >= required:
                        return True
            return False

        for required, shop_names in SHOP_UNLOCK_GROUPS.items():
            for shop_name in shop_names:
                set_rule(
                    loc(shop_name),
                    lambda state, required=required: can_reach_wolfen_count(state, required),
                )

        # EXPERIMENTAL BETA SAFETY: vanilla shop thresholds alone are NOT
        # sufficient to prove affordable AP progression. Never place any
        # advancement behind a Nooties-paid location until money logic is
        # modeled as real progression; shop checks still grant filler/useful.
        for _shop_group in SHOP_UNLOCK_GROUPS.values():
            for _shop_name in _shop_group:
                add_item_rule(loc(_shop_name), lambda item: not item.advancement)

        # Filler scaling retained from the previous balance pass.
        for zone in ("Nativs City", "Flying Forest"):
            for location_name in LOCATION_NAMES_BY_ZONE[zone]:
                add_item_rule(
                    loc(location_name),
                    lambda item, forbidden=EARLY_ZONE_FORBIDDEN_ITEMS, p=p:
                        item.player != p or item.name not in forbidden,
                )
        for zone in ("Hunters Domain", "Wind Tower", "The Quarry", "Amber Quarry", "The Root"):
            for location_name in LOCATION_NAMES_BY_ZONE[zone]:
                add_item_rule(
                    loc(location_name),
                    lambda item, forbidden=MID_ZONE_FORBIDDEN_ITEMS, p=p:
                        item.player != p or item.name not in forbidden,
                )

        # Runtime completion is sent only by the Launcher/client when the confirmed
        # credits condition fires. This remains generation's beatability proxy.
        self.multiworld.completion_condition[p] = (
            lambda state, p=p:
                (fast_travel_vanilla or not self.options.lock_wolfen_city.value or state.has(ITEM_WOLFEN_CITY_ACCESS, p))
                and (fast_travel_vanilla or not self.options.lock_the_fortress.value or state.has(ITEM_FORTRESS_ACCESS, p))
                and state.has(ITEM_PROGRESSIVE_BOOMY, p, 2)
                and state.has(ITEM_PROGRESSIVE_BOARD, p, 2)
                and state.has(ITEM_CLIMBING_GLOVES, p)
                and state.has(ITEM_JAMGUT, p)
                and state.has("Receptacle", p)
                and all(state.has(rune, p) for rune in ITEM_RUNES)
        )

    def write_spoiler_header(self, spoiler_handle) -> None:
        """Store the REAL selected FT01 entrances in the spoiler itself.

        No separate log, YAML inference or PCSX2 run is required to know
        which destinations were selected by this individual seed.
        """
        vanilla = int(self._effective_ft_value()) == 1
        routes = ([] if vanilla else [route["zone"] for route in
                                  getattr(self, "starting_fast_travel_routes", [])])
        name = self.multiworld.get_player_name(self.player)
        spoiler_handle.write(
            "KYA_LOGIC_089"
            f"|player={name}"
            f"|mode={'vanilla' if vanilla else 'archipelago'}"
            f"|routes={','.join(routes)}"
            f"|lock_flying={int(not vanilla)}"
            f"|lock_root={int(not vanilla)}"
            f"|lock_city={int(not vanilla and bool(self.options.lock_wolfen_city.value))}"
            f"|lock_fortress={int(not vanilla and bool(self.options.lock_the_fortress.value))}"
            "\n"
        )

    def fill_slot_data(self) -> dict:
        vanilla_ft = int(self._effective_ft_value()) == 1
        routes = [] if vanilla_ft else [dict(route) for route in getattr(self, "starting_fast_travel_routes", [])]
        return {
            "prototype_version": PROTOTYPE_VERSION,
            "fast_travel_progression": int(self._effective_ft_value()),
            "fast_travel_progression_name": "vanilla" if vanilla_ft else "archipelago",
            "starting_fast_travels": len(routes),
            "starting_fast_travel_routes": routes,
            # Other Launchers still consume these flags from slot_data.
            "lock_the_root": not vanilla_ft,
            "lock_flying_forest": not vanilla_ft,
            "automatic_entry_access_locks": True,
            "lock_wolfen_city": False if vanilla_ft else bool(self.options.lock_wolfen_city.value),
            "lock_the_fortress": False if vanilla_ft else bool(self.options.lock_the_fortress.value),
            "fast_travel_same_zone_limit": 1,
            "fast_travel_anti_softlock_mana": 3,
            "ap_nooties_modifier": int(self.options.ap_nooties_modifier.value),
            "shop_price_modifier": int(self.options.shop_price_modifier.value),
            "economy_step_percent": 10,
            "blue_egg_randomized": False,
            "mapped_wolfen_count": sum(len(v) for v in WOLFEN_ZONE_KEY_TO_LOCATION.values()),
            "special_location_count": len(SPECIAL_LOCATION_CONDITIONS),
            "shop_location_count": len(SHOP_LOCATION_CONDITIONS),
            "fast_travel_location_count": len(FAST_TRAVEL_LOCATION_ZONES),
            "mapped_wolfens_by_zone": {zone: len(WOLFEN_ZONE_KEY_TO_LOCATION[zone]) for zone in ZONE_ORDER},
            "zone_safe_detection": True,
            "starter_boomy": "Vanilla tutorial reward; never AP-precollected",
            "bracelet_distribution": "seven map-validated locked bracelet checks retained",
            "early_progression": "No forced early items: reachable AP graph decides placement",
            "logic_revision": "0.8.11: Quarry 01 only without Gloves; Quarry 02-10 require Gloves at minimum; FT-aware entrances retained; other uncertain terrain provisional",
            "runtime_goal": "Final Boss Brazul Defeated + real credits @ 0x0044982C 0->4",
            "target_build": "PAL SLES_514.73",
            "demo_note": "0.8.11 Quarry progression numbering fix; FT locks automatic. NEW seed required; Launcher 0.9.34 compatible.",
            "subzone_naming_revision": "2026-10-05 Flying Forest corrected; Quarry descriptive split remains provisional",
        }
