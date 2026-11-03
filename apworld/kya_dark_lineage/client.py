from __future__ import annotations

import asyncio
from collections import Counter
import logging
import struct
from typing import Optional

import Utils
from CommonClient import (
    ClientCommandProcessor,
    CommonContext,
    get_base_parser,
    gui_enabled,
    server_loop,
)

from .constants import (
    ACTOR_MANAGER_ACTIVE_COUNT_OFFSET, ACTOR_MANAGER_ACTIVE_LIST_OFFSET, ACTOR_MANAGER_MAX_ACTIVE,
    ADDR_ACTOR_MANAGER_GLOBAL, ADDR_BOOMY_TYPE, ADDR_MAGIC_GAUGE_CAP, ADDR_MAGIC_GAUGE_LEVEL, ADDR_MAGIC_GAUGE_STEP,
    ADDR_GOAL_BRAZUL_FINAL, GOAL_BRAZUL_FINAL_FROM, GOAL_BRAZUL_FINAL_VALUE, GOAL_ZONE,
    ADDR_GOAL_CREDITS, GOAL_CREDITS_FROM, GOAL_CREDITS_VALUE,
    EXPECTED_DISC_SERIAL_NORMALIZED, GAME_NAME,
    ITEM_BASIC_BOOMY, ITEM_PROGRESSIVE_BOOMY, ITEM_PROGRESSIVE_BRACELET, ITEM_PROGRESSIVE_BOARD, ITEM_PROGRESSIVE_MAGIC_GAUGE, ITEM_PROGRESSIVE_LIFE_GAUGE,
    ADDR_BRACELET_BITFIELD, ADDR_BOARD_LEVEL, ITEM_NAME_TO_ID, ITEM_RUNE_SCENARIO_VARS, ITEM_SCENARIO_FLAGS,
    LOCATION_NAME_TO_ID, PINE_HOST, PINE_PORT, PROTOTYPE_VERSION,
    SPECIAL_LOCATION_CONDITIONS, SPECIAL_LOCATION_ZONES,
    SHOP_LOCATION_CONDITIONS, SHOP_LOCATION_ZONES, SHOP_VANILLA_REWARD_STATE, SHOP_LIVE_REWARD_RULES, SHOP_UNLOCK_GROUPS, ADDR_GLOBAL_WOLFEN_COUNT, ADDR_MONEY,
    ADDR_PLAYER_POINTER, PLAYER_HP_OFFSET, PLAYER_MAX_HP_OFFSET, ADDR_LIFE_GAUGE,
    WOLFEN_DESCRIPTOR_OFFSET, WOLFEN_KEY_OFFSET, WOLFEN_KEY_TO_ZONES, WOLFEN_ZONE_KEY_TO_LOCATION,
    WOLFEN_STATE_FREED, WOLFEN_STATE_OFFSET, WOLFEN_STATE_PRESENT, WOLFEN_VTABLE,
    FAST_TRAVEL_VTABLE, FAST_TRAVEL_STATE_OFFSET, FAST_TRAVEL_STATE_OFF, FAST_TRAVEL_STATE_ON,
    FAST_TRAVEL_DESCRIPTOR_OFFSET, FAST_TRAVEL_KEY_OFFSET, FAST_TRAVEL_ZONE_KEY_TO_LOCATION,
    DEBUG_VALIDATION_PROBES, ITEM_TO_SPECIAL_LOCATION,
)
from .pine import PineClient, PineError


kya_logger = logging.getLogger("KyaClient")

# Vanilla Nativs City shop prices observed during our own playtests.  These are
# only an identity hint for purchases where the vanilla reward is already owned;
# money alone never overrides a contradictory live/serialized signal.
SHOP_PRICE_HINTS = {
    "Nativs City - Shop - Basic Boomy": 10,
    "Nativs City - Shop - Yellow Bracelet": 100,
    "Nativs City - Shop - Telescope": 30,
    "Nativs City - Shop - Magic Board": 50,
    "Nativs City - Shop - Green Bracelet": 150,
    "Nativs City - Shop - Climbing Gloves": 50,
    "Nativs City - Shop - Extra Energy Bar 1": 1000,
    "Nativs City - Shop - Blue Bracelet": 200,
    "Nativs City - Shop - Jamgut Birdcall": 70,
    "Nativs City - Shop - Speed Board": 50,
    "Nativs City - Shop - Golden Boomy": 100,
    "Nativs City - Shop - Silver Bracelet": 500,
    "Nativs City - Shop - Silver Boomy": 100,
    "Nativs City - Shop - Brown Bracelet": 250,
    "Nativs City - Shop - Magic Bouncers": 50,
    "Nativs City - Shop - Extra Energy Bar 2": 1000,
    "Nativs City - Shop - Black Bracelet": 400,
    "Nativs City - Shop - Gold Bracelet": 700,
}


def _valid_ee_pointer(value: int) -> bool:
    # Kya runtime objects observed in normal EE RAM.
    return 0x00100000 <= value < 0x02000000 and (value & 0x3) == 0


def _shop_authoritative_target(ctx: "KyaContext", name: str, reward_spec: dict) -> int:
    """Exact Kya inventory value allowed by received AP items after a shop buy."""
    counts = Counter(network_item.item for network_item in ctx.items_received)
    addr = int(reward_spec["address"])
    if str(reward_spec.get("kind", "u32")) == "life_gauge":
        life_count = counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_LIFE_GAUGE]]
        return min(250, 50 + max(0, int(life_count)) * 50)
    if addr == ADDR_BOOMY_TYPE:
        basic = 1 if counts[ITEM_NAME_TO_ID[ITEM_BASIC_BOOMY]] > 0 else 0
        progressive = min(3, counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_BOOMY]])
        return max(basic, progressive)
    if addr == ADDR_BRACELET_BITFIELD:
        progressive = min(7, counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_BRACELET]])
        return (1 << (progressive + 1)) - 1
    if addr == ADDR_BOARD_LEVEL:
        return min(2, counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_BOARD]])
    for item_name, item_addr in ITEM_SCENARIO_FLAGS.items():
        if int(item_addr) == addr:
            return 1 if counts[ITEM_NAME_TO_ID[item_name]] > 0 else 0
    return 0


async def _suppress_shop_inventory_mutation(ctx: "KyaContext", name: str) -> None:
    reward_spec = SHOP_VANILLA_REWARD_STATE.get(name)
    if reward_spec is None:
        return
    reward_addr = int(reward_spec["address"])
    target = int(_shop_authoritative_target(ctx, name, reward_spec))
    await ctx.pine.write32(reward_addr, target)
    verified = int(await ctx.pine.read32(reward_addr))
    if str(reward_spec.get("kind", "u32")) == "life_gauge":
        player = int(await ctx.pine.read32(ADDR_PLAYER_POINTER))
        if _valid_ee_pointer(player):
            max_addr = player + PLAYER_MAX_HP_OFFSET
            hp_addr = player + PLAYER_HP_OFFSET
            await ctx.pine.write32(max_addr, _float_to_u32(float(target)))
            hp = _u32_to_float(int(await ctx.pine.read32(hp_addr)))
            if hp == hp and 0.0 <= hp < 10000.0 and hp > float(target):
                await ctx.pine.write32(hp_addr, _float_to_u32(float(target)))
    kya_logger.info(
        "Vanilla shop inventory mutation suppressed under AP authority: %s (0x%08X -> %d).",
        name, reward_addr, verified,
    )


class KyaCommandProcessor(ClientCommandProcessor):
    def _cmd_kya(self) -> None:
        """Show current Kya/PINE demo status."""
        ctx: KyaContext = self.ctx
        self.output(
            f"Kya APWorld {PROTOTYPE_VERSION} | PINE: "
            + ("connected" if ctx.pine.connected else "disconnected")
            + f" | game ID: {ctx.pine_game_id or '?'}"
            + f" | safe writes: {'YES' if ctx.pine_game_verified else 'NO'}"
        )
        self.output(
            f"Mapped Wolfens: {sum(len(v) for v in WOLFEN_ZONE_KEY_TO_LOCATION.values())}"
            f" | active mapped Wolfens: {len(ctx.active_wolfen_states)}"
            f" | Actor Manager count: {ctx.actor_manager_count if ctx.actor_manager_count is not None else '?'}"
        )
        self.output(
            f"Boomy: {ctx.last_boomy_type if ctx.last_boomy_type is not None else '?'}"
            f" | Magic level: {ctx.last_magic_level if ctx.last_magic_level is not None else '?'}"
            f" | Magic max: {ctx.last_max_magic if ctx.last_max_magic is not None else '?'}"
            f" | pending checks: {len(ctx.pending_wolfen_events) + len(ctx.pending_special_events)}"
        )


class KyaContext(CommonContext):
    command_processor = KyaCommandProcessor
    game = GAME_NAME
    items_handling = 0b111
    want_slot_data = True

    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super().__init__(server_address, password)
        self.pine = PineClient(PINE_HOST, PINE_PORT)
        self.pine_game_id: Optional[str] = None
        self.pine_game_verified = False

        self.last_boomy_type: Optional[int] = None
        self.last_magic_level: Optional[int] = None
        self.last_magic_step: Optional[int] = None
        self.last_magic_cap: Optional[int] = None
        self.last_max_magic: Optional[int] = None

        # Generic Actor Manager watcher. Keyed by persistent WolfenKey, not actor address.
        self.active_wolfen_states: dict[int, int] = {}
        self.active_wolfen_actors: dict[int, int] = {}
        self.actor_manager_count: Optional[int] = None
        self.actor_manager_baselined = False
        self.pending_wolfen_events: dict[str, int] = {}

        self.active_fast_travel_states: dict[int, int] = {}
        self.active_fast_travel_keys: dict[int, int] = {}
        self.fast_travel_baselined = False

        self.validation_probe_states: dict[str, int] = {}
        self.validation_probes_baselined = False

        # Confirmed ScenarioVar checks. First read is a baseline; only live false->true
        # transitions are emitted in this demo build to keep advanced-save demos clean.
        self.special_states: dict[str, bool] = {}
        self.special_baselined = False
        self.pending_special_events: set[str] = set()

        self.current_zone: Optional[str] = None
        self.shop_states: dict[str, bool] = {}
        self.shop_reward_snapshots: dict[str, int] = {}
        self.shop_baselined = False
        self.shop_money_last: Optional[int] = None
        self.shop_purchase_tokens: list[tuple[float, int]] = []
        self.shop_ambiguous_token_warned: set[float] = set()
        self.shop_unconfirmed_stock: set[str] = set()
        self.goal_last_value: Optional[int] = None
        self.goal_credits_last_value: Optional[int] = None
        self.goal_sent = False

        self._pine_connection_announced = False
        self._bad_game_announced = False
        self._last_pine_error: Optional[str] = None

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def make_gui(self):
        from kvui import GameManager

        class KyaManager(GameManager):
            base_title = "Archipelago Kya: Dark Lineage Client"
            logging_pairs = [
                ("Client", "Archipelago"),
                ("KyaClient", "Kya / PINE"),
            ]

        return KyaManager

    async def shutdown(self):
        await self.pine.close()
        await super().shutdown()


async def _ensure_pine(ctx: KyaContext) -> bool:
    if ctx.pine.connected and ctx.pine_game_verified:
        return True

    if not ctx.pine.connected:
        try:
            await ctx.pine.connect()
            ctx.pine_game_id = await ctx.pine.game_id()
            normalized = ctx.pine.normalize_serial(ctx.pine_game_id)
            ctx.pine_game_verified = normalized == EXPECTED_DISC_SERIAL_NORMALIZED

            if not ctx._pine_connection_announced:
                kya_logger.info(
                    "PINE connected to %s:%d. Game ID: %s",
                    PINE_HOST,
                    PINE_PORT,
                    ctx.pine_game_id,
                )
                ctx._pine_connection_announced = True

            if ctx.pine_game_verified:
                kya_logger.info(
                    "PAL SLES_514.73 verified. APWorld %s; RAM writes enabled.",
                    PROTOTYPE_VERSION,
                )
                ctx._bad_game_announced = False
                ctx._last_pine_error = None
                return True

            if not ctx._bad_game_announced:
                kya_logger.error(
                    "Wrong game/build through PINE: %s. Expected SLES_514.73. "
                    "RAM WRITES ARE DISABLED.",
                    ctx.pine_game_id,
                )
                ctx._bad_game_announced = True
            return False

        except (OSError, PineError) as exc:
            await ctx.pine.close()
            ctx.pine_game_verified = False
            ctx._pine_connection_announced = False
            message = str(exc)
            if message != ctx._last_pine_error:
                kya_logger.warning(
                    "Waiting for PCSX2/PINE on %s:%d (%s)",
                    PINE_HOST,
                    PINE_PORT,
                    message,
                )
                ctx._last_pine_error = message
            return False

    return ctx.pine_game_verified


async def _read_player_state(ctx: KyaContext) -> None:
    boomy, level, step, cap = await ctx.pine.read32_many([
        ADDR_BOOMY_TYPE,
        ADDR_MAGIC_GAUGE_LEVEL,
        ADDR_MAGIC_GAUGE_STEP,
        ADDR_MAGIC_GAUGE_CAP,
    ])
    computed = min(level * step, cap)

    if boomy != ctx.last_boomy_type:
        kya_logger.info("Boomy type ScenarioVar: %d", boomy)
    if (
        level != ctx.last_magic_level
        or step != ctx.last_magic_step
        or cap != ctx.last_magic_cap
        or computed != ctx.last_max_magic
    ):
        kya_logger.info(
            "Magic ScenarioVars: level=%d step=%d cap=%d -> max=%d",
            level, step, cap, computed,
        )

    ctx.last_boomy_type = boomy
    ctx.last_magic_level = level
    ctx.last_magic_step = step
    ctx.last_magic_cap = cap
    ctx.last_max_magic = computed


def _infer_zone_from_keys(keys: list[int], current_zone: Optional[str]) -> Optional[str]:
    votes: Counter[str] = Counter()
    for key in keys:
        for zone in WOLFEN_KEY_TO_ZONES.get(key, ()):  # duplicate keys may vote for multiple zones
            votes[zone] += 1
    if not votes:
        return current_zone
    ranked = votes.most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return current_zone
    return ranked[0][0]


async def _read_actor_manager_wolfens(ctx: KyaContext) -> None:
    manager = await ctx.pine.read32(ADDR_ACTOR_MANAGER_GLOBAL)
    if not _valid_ee_pointer(manager):
        ctx.actor_manager_count = None
        return  # keep last stable zone through streaming/cinematics

    active_list, count = await ctx.pine.read32_many([
        manager + ACTOR_MANAGER_ACTIVE_LIST_OFFSET,
        manager + ACTOR_MANAGER_ACTIVE_COUNT_OFFSET,
    ])
    if not _valid_ee_pointer(active_list) or count > ACTOR_MANAGER_MAX_ACTIVE:
        ctx.actor_manager_count = None
        return

    ctx.actor_manager_count = count
    actor_values = await ctx.pine.read32_many([active_list + i * 4 for i in range(count)]) if count else []
    actors, seen = [], set()
    for actor in actor_values:
        if _valid_ee_pointer(actor) and actor not in seen:
            seen.add(actor); actors.append(actor)

    vtables = await ctx.pine.read32_many(actors) if actors else []
    wolfen_actors = [actor for actor, vt in zip(actors, vtables) if vt == WOLFEN_VTABLE]
    rows = []
    if wolfen_actors:
        states = await ctx.pine.read32_many([actor + WOLFEN_STATE_OFFSET for actor in wolfen_actors])
        descs = await ctx.pine.read32_many([actor + WOLFEN_DESCRIPTOR_OFFSET for actor in wolfen_actors])
        valid = [(a,s,d) for a,s,d in zip(wolfen_actors,states,descs) if _valid_ee_pointer(d)]
        keys = await ctx.pine.read32_many([d + WOLFEN_KEY_OFFSET for _,_,d in valid]) if valid else []
        rows = [(a,s,k) for (a,s,_),k in zip(valid,keys) if 0 < k < 0x10000]

    inferred = _infer_zone_from_keys([k for _,_,k in rows], ctx.current_zone)
    if inferred != ctx.current_zone and inferred is not None:
        kya_logger.info("AP zone detected: %s", inferred)
        ctx.current_zone = inferred
        ctx.actor_manager_baselined = False
        ctx.special_baselined = False
        ctx.fast_travel_baselined = False
        ctx.active_fast_travel_states.clear()
        ctx.active_fast_travel_keys.clear()
        if inferred != "Nativs City":
            ctx.shop_baselined = False
            ctx.shop_states.clear()
            ctx.shop_reward_snapshots.clear()
            ctx.shop_money_last = None
            ctx.shop_purchase_tokens.clear()
            ctx.shop_ambiguous_token_warned.clear()
            ctx.shop_unconfirmed_stock.clear()

    zone = ctx.current_zone
    zone_map = WOLFEN_ZONE_KEY_TO_LOCATION.get(zone, {}) if zone else {}
    current_states: dict[str, int] = {}
    current_actors: dict[str, int] = {}
    for actor, state, key in rows:
        name = zone_map.get(key)
        if name is not None:
            current_states[name] = state
            current_actors[name] = actor

    if not ctx.actor_manager_baselined:
        ctx.active_wolfen_states = current_states
        ctx.active_wolfen_actors = current_actors
        ctx.actor_manager_baselined = True
        kya_logger.info("Zone-safe Wolfen baseline: zone=%s mapped-active=%d", zone or '?', len(current_states))
        return

    for name, new_state in current_states.items():
        old_state = ctx.active_wolfen_states.get(name)
        if old_state == WOLFEN_STATE_PRESENT and new_state == WOLFEN_STATE_FREED:
            ctx.pending_wolfen_events[name] = current_actors[name]
            kya_logger.info("LIVE Wolfen release [%s]: %s | 1->2", zone, name)

    ctx.active_wolfen_states = current_states
    ctx.active_wolfen_actors = current_actors


async def _read_special_flags(ctx: KyaContext) -> None:
    zone = ctx.current_zone
    eligible = {name: cond for name,cond in SPECIAL_LOCATION_CONDITIONS.items() if SPECIAL_LOCATION_ZONES[name] == zone}
    if not eligible:
        return
    addresses = sorted({a for conditions in eligible.values() for a,_ in conditions})
    values = await ctx.pine.read32_many(addresses)
    by_addr = dict(zip(addresses,values))
    current = {
        location: all(by_addr[a] == expected for a,expected in conditions)
        for location,conditions in eligible.items()
    }
    if not ctx.special_baselined:
        ctx.special_states.update(current)
        ctx.special_baselined = True
        kya_logger.info("Special checks armed for zone %s (%d checks; live transitions only).", zone or '?', len(current))
        return
    for location,active in current.items():
        old = ctx.special_states.get(location, active)
        if (not old) and active and LOCATION_NAME_TO_ID[location] in ctx.missing_locations:
            ctx.pending_special_events.add(location)
            kya_logger.info("LIVE special trigger [%s]: %s", zone, location)
        ctx.special_states[location] = active


async def _read_actor_manager_fast_travels(ctx: KyaContext) -> None:
    manager = await ctx.pine.read32(ADDR_ACTOR_MANAGER_GLOBAL)
    if not _valid_ee_pointer(manager):
        return
    active_list, count = await ctx.pine.read32_many([
        manager + ACTOR_MANAGER_ACTIVE_LIST_OFFSET,
        manager + ACTOR_MANAGER_ACTIVE_COUNT_OFFSET,
    ])
    if not _valid_ee_pointer(active_list) or count > ACTOR_MANAGER_MAX_ACTIVE:
        return
    actor_values = await ctx.pine.read32_many([active_list + i * 4 for i in range(count)]) if count else []
    actors, seen = [], set()
    for actor in actor_values:
        if _valid_ee_pointer(actor) and actor not in seen:
            seen.add(actor); actors.append(actor)
    vtables = await ctx.pine.read32_many(actors) if actors else []
    ft_actors = [actor for actor,vt in zip(actors,vtables) if vt == FAST_TRAVEL_VTABLE]
    current_states: dict[int, int] = {}
    current_keys: dict[int, int] = {}
    if ft_actors:
        states = await ctx.pine.read32_many([a + FAST_TRAVEL_STATE_OFFSET for a in ft_actors])
        descs = await ctx.pine.read32_many([a + FAST_TRAVEL_DESCRIPTOR_OFFSET for a in ft_actors])
        valid = [(a,s,d) for a,s,d in zip(ft_actors,states,descs) if _valid_ee_pointer(d)]
        keys = await ctx.pine.read32_many([d + FAST_TRAVEL_KEY_OFFSET for _,_,d in valid]) if valid else []
        for (actor,state,_desc),key in zip(valid,keys):
            if 0 < key < 0x10000:
                current_states[actor] = state
                current_keys[actor] = key

    if not ctx.fast_travel_baselined:
        ctx.active_fast_travel_states = current_states
        ctx.active_fast_travel_keys = current_keys
        ctx.fast_travel_baselined = True
        kya_logger.info("Fast Travel checks armed: zone=%s active=%d", ctx.current_zone or '?', len(current_states))
        if current_keys:
            diagnostic = ", ".join(
                f"0x{current_keys[a]:04X}={current_states.get(a, -1)}"
                for a in sorted(current_keys)
            )
            kya_logger.info("Fast Travel baseline candidates [%s]: %s", ctx.current_zone or '?', diagnostic)
        return

    zone_map = FAST_TRAVEL_ZONE_KEY_TO_LOCATION.get(ctx.current_zone or '', {})
    for actor,new_state in current_states.items():
        old_state = ctx.active_fast_travel_states.get(actor, new_state)
        key = current_keys.get(actor)
        if old_state == FAST_TRAVEL_STATE_OFF and new_state == FAST_TRAVEL_STATE_ON and key is not None:
            name = zone_map.get(key)
            if name is not None:
                if LOCATION_NAME_TO_ID[name] in ctx.missing_locations:
                    ctx.pending_special_events.add(name)
                kya_logger.info("LIVE Fast Travel [%s] key=0x%04X: %s | 0->1", ctx.current_zone, key, name)
            else:
                kya_logger.warning("UNMAPPED Fast Travel activation [%s]: candidate key=0x%04X actor=0x%08X", ctx.current_zone or '?', key, actor)
    ctx.active_fast_travel_states = current_states
    ctx.active_fast_travel_keys = current_keys


async def _read_validation_probes(ctx: KyaContext) -> None:
    addresses = sorted({int(spec["address"]) for spec in DEBUG_VALIDATION_PROBES.values()})
    values = await ctx.pine.read32_many(addresses) if addresses else []
    by_addr = dict(zip(addresses, values))
    current = {name: by_addr[int(spec["address"])] for name,spec in DEBUG_VALIDATION_PROBES.items()}
    if not ctx.validation_probes_baselined:
        ctx.validation_probe_states = current
        ctx.validation_probes_baselined = True
        kya_logger.info("Validation monitor armed (%d key-item/progression probes).", len(current))
        return
    for name,value in current.items():
        old = ctx.validation_probe_states.get(name, value)
        if value != old:
            spec = DEBUG_VALIDATION_PROBES[name]
            target = spec.get("target")
            suffix = " TARGET" if target is not None and value == int(target) else ""
            kya_logger.info("VALIDATION state: %s %d -> %d%s (game/AP source not distinguished)", name, old, value, suffix)
        ctx.validation_probe_states[name] = value


def _u32_to_float(raw: int) -> float:
    return struct.unpack("<f", struct.pack("<I", raw & 0xFFFFFFFF))[0]


def _float_to_u32(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", float(value)))[0]


async def _read_shop_checks(ctx: KyaContext) -> None:
    """Nooties-gated shop purchase recovery.

    The serialized shop bitfields are useful identity/stock confirmation but can
    transiently rebuild during loads. A 1->0 stock transition is therefore only
    committed as a LocationCheck when it can be paired with a recent natural
    Nooties spend. Crucially, player inventory does NOT need to change: an item
    already received from Archipelago may remain 1->1 while its shop stock still
    goes 1->0.
    """
    if not ctx.slot:
        return

    now = asyncio.get_running_loop().time()
    money_now = (await ctx.pine.read32_many([ADDR_MONEY]))[0]
    if ctx.shop_money_last is None:
        ctx.shop_money_last = money_now
    else:
        old_money = ctx.shop_money_last
        if money_now < old_money:
            spent = old_money - money_now
            # Ignore obvious save-state/large rollback noise; ordinary purchases
            # are well below this ceiling in the validated shop table.
            if 0 < spent <= 10000:
                ctx.shop_purchase_tokens.append((now, spent))
                kya_logger.info("Shop purchase token: Nooties %d->%d (-%d).", old_money, money_now, spent)
        ctx.shop_money_last = money_now
    ctx.shop_purchase_tokens = [
        token for token in ctx.shop_purchase_tokens if now - token[0] <= 180.0
    ]
    ctx.shop_ambiguous_token_warned.intersection_update({t[0] for t in ctx.shop_purchase_tokens})

    addresses = sorted({addr for addr, _mask in SHOP_LOCATION_CONDITIONS.values()})
    values = await ctx.pine.read32_many(addresses)
    by_addr = dict(zip(addresses, values))
    current = {
        name: bool(by_addr[addr] & mask)
        for name, (addr, mask) in SHOP_LOCATION_CONDITIONS.items()
    }

    reward_addresses = sorted({int(spec["address"]) for spec in SHOP_VANILLA_REWARD_STATE.values()})
    reward_values = await ctx.pine.read32_many(reward_addresses) if reward_addresses else []
    reward_by_addr = dict(zip(reward_addresses, reward_values))
    current_rewards = {
        name: reward_by_addr.get(int(spec["address"]))
        for name, spec in SHOP_VANILLA_REWARD_STATE.items()
    }

    if not ctx.shop_baselined:
        ctx.shop_states = current
        ctx.shop_reward_snapshots = {
            name: int(current_rewards[name])
            for name, available in current.items()
            if available and current_rewards.get(name) is not None
        }
        ctx.shop_baselined = True
        kya_logger.info(
            "Global shop checks armed (%d mapped purchases; Nooties-gated stock confirmation).",
            len(current),
        )
        return

    # Do NOT consume an unpaired serialized 1->0. Keeping the logical state at
    # True lets a later genuine Nooties spend recover the purchase even if the
    # serialized buffer flickered earlier during a load.
    next_states = dict(ctx.shop_states)
    stock_candidates: list[str] = []
    for name, available in current.items():
        old = ctx.shop_states.get(name, available)
        location_id = LOCATION_NAME_TO_ID[name]
        if location_id not in ctx.missing_locations:
            next_states[name] = available
            ctx.shop_unconfirmed_stock.discard(name)
            continue
        if available:
            next_states[name] = True
            ctx.shop_unconfirmed_stock.discard(name)
            if current_rewards.get(name) is not None:
                ctx.shop_reward_snapshots[name] = int(current_rewards[name])
        elif old:
            stock_candidates.append(name)

    if stock_candidates and ctx.shop_purchase_tokens:
        # A single candidate is unambiguous. If several changed together, require
        # at least as many purchase tokens so a load cannot check a whole shop page.
        if len(stock_candidates) == 1 or len(ctx.shop_purchase_tokens) >= len(stock_candidates):
            for name in stock_candidates:
                token = ctx.shop_purchase_tokens.pop(0)
                await _suppress_shop_inventory_mutation(ctx, name)

                ctx.pending_special_events.add(name)
                next_states[name] = False
                ctx.shop_unconfirmed_stock.discard(name)
                kya_logger.info(
                    "LIVE shop stock purchase: %s (spend=%d; inventory transition not required)",
                    name, token[1],
                )
        else:
            pending = [n for n in stock_candidates if n not in ctx.shop_unconfirmed_stock]
            if pending:
                kya_logger.warning(
                    "Ambiguous serialized shop changes waiting for purchase tokens: %s",
                    ", ".join(pending),
                )
                ctx.shop_unconfirmed_stock.update(pending)
    elif stock_candidates:
        pending = [n for n in stock_candidates if n not in ctx.shop_unconfirmed_stock]
        if pending:
            kya_logger.info(
                "Serialized shop stock waiting for Nooties purchase token: %s",
                ", ".join(pending),
            )
            ctx.shop_unconfirmed_stock.update(pending)

    ctx.shop_states = next_states

    # Runtime hotfix for duplicate purchases. If AP already granted the vanilla
    # item, Kya can still charge Nooties while leaving both the reward field and
    # serialized stock unchanged. Wait briefly so the normal stock path has first
    # chance, then infer only when ONE currently unlocked/unchecked shop entry is
    # already owned. Never guess from the Nooties amount alone.
    if ctx.shop_purchase_tokens and (ctx.current_zone or "") == "Nativs City":
        oldest_at, oldest_spent = ctx.shop_purchase_tokens[0]
        token_age = now - oldest_at
        if token_age >= 1.0:
            try:
                wolfen_count = int(await ctx.pine.read32(ADDR_GLOBAL_WOLFEN_COUNT))
            except Exception:
                wolfen_count = -1
            unlocked_names = set()
            for threshold, names in SHOP_UNLOCK_GROUPS.items():
                try:
                    required = int(threshold)
                except Exception:
                    continue
                if wolfen_count >= required:
                    unlocked_names.update(str(n) for n in names)

            def _reward_already_owned(name: str) -> bool:
                spec = SHOP_LIVE_REWARD_RULES.get(name)
                value = current_rewards.get(name)
                if spec is None or value is None:
                    return False
                mode = str(spec.get("mode", "bool_gain"))
                value = int(value)
                if mode == "bool_gain":
                    return value != 0
                if mode == "bit_gain":
                    return (value & int(spec["mask"])) != 0
                if mode == "level_gain_to":
                    return value >= int(spec["threshold"])
                if mode == "life_gain":
                    return value >= int(spec.get("threshold", 100))
                return False

            duplicate_candidates = []
            for name in sorted(unlocked_names):
                location_id = LOCATION_NAME_TO_ID.get(name)
                if location_id is None or location_id not in ctx.missing_locations:
                    continue
                if _reward_already_owned(name):
                    duplicate_candidates.append(name)

            priced_candidates = [
                name for name in duplicate_candidates
                if SHOP_PRICE_HINTS.get(name) == int(oldest_spent)
            ]
            if len(priced_candidates) == 1:
                name = priced_candidates[0]
                token = ctx.shop_purchase_tokens.pop(0)
                ctx.shop_ambiguous_token_warned.discard(token[0])
                await _suppress_shop_inventory_mutation(ctx, name)
                ctx.pending_special_events.add(name)
                kya_logger.info(
                    "LIVE duplicate shop purchase: %s (spend=%d; already owned)",
                    name, token[1],
                )
            elif token_age >= 3.0 and oldest_at not in ctx.shop_ambiguous_token_warned:
                ctx.shop_ambiguous_token_warned.add(oldest_at)
                kya_logger.warning(
                    "Duplicate shop spend remains queued for stock confirmation. spend=%d candidates=%s wolfens=%d",
                    oldest_spent, ", ".join(priced_candidates or duplicate_candidates) or "none", wolfen_count,
                )


async def _read_goal(ctx: KyaContext) -> None:
    brazul, credits = await ctx.pine.read32_many([ADDR_GOAL_BRAZUL_FINAL, ADDR_GOAL_CREDITS])
    old_brazul = ctx.goal_last_value
    old_credits = ctx.goal_credits_last_value

    if old_brazul is None or old_credits is None:
        kya_logger.info(
            "Final goal watcher armed: Brazul Var61=%d | Credits @ 0x%08X=%d",
            brazul, ADDR_GOAL_CREDITS, credits,
        )

    # Safety fix 2026-10-30: 0x0044982C was observed as 4 during
    # ordinary gameplay, including when Brazul Var61=0.  It must NOT
    # authorize an Archipelago GOAL until an independent true credits
    # transition/scene flag has been researched and verified in real PCSX2.
    # Boss AP location detection is handled separately.  No StatusUpdate
    # from this legacy heuristic (even on a value transition).

    ctx.goal_last_value = brazul
    ctx.goal_credits_last_value = credits


async def _send_pending_checks(ctx: KyaContext) -> None:
    if not ctx.slot:
        return
    for location_name, actor in list(ctx.pending_wolfen_events.items()):
        location_id = LOCATION_NAME_TO_ID[location_name]
        if location_id not in ctx.missing_locations:
            ctx.pending_wolfen_events.pop(location_name,None); continue
        sent = await ctx.check_locations([location_id])
        if sent:
            kya_logger.info("CHECK -> Archipelago: %s (actor 0x%08X)", location_name, actor)
            ctx.pending_wolfen_events.pop(location_name,None)
    for location_name in list(ctx.pending_special_events):
        location_id = LOCATION_NAME_TO_ID[location_name]
        if location_id not in ctx.missing_locations:
            ctx.pending_special_events.discard(location_name); continue
        sent = await ctx.check_locations([location_id])
        if sent:
            kya_logger.info("CHECK -> Archipelago: %s", location_name)
            ctx.pending_special_events.discard(location_name)


async def _apply_received_items(ctx: KyaContext) -> None:
    # Writes are blocked unless the exact PAL target is verified through PINE.
    if not ctx.pine_game_verified or not ctx.slot:
        return

    counts = Counter(network_item.item for network_item in ctx.items_received)

    # Backward-compatible Basic Boomy from older seeds.
    boomy_received = counts[ITEM_NAME_TO_ID[ITEM_BASIC_BOOMY]]
    if boomy_received > 0 and ctx.last_boomy_type is not None and ctx.last_boomy_type < 1:
        await ctx.pine.write32(ADDR_BOOMY_TYPE, 1)
        ctx.last_boomy_type = await ctx.pine.read32(ADDR_BOOMY_TYPE)

    progressive_boomy = counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_BOOMY]]
    if progressive_boomy > 0:
        current = await ctx.pine.read32(ADDR_BOOMY_TYPE)
        target = max(current, min(3, progressive_boomy))
        if target != current:
            await ctx.pine.write32(ADDR_BOOMY_TYPE, target)
            kya_logger.info("ITEM <- Archipelago: Progressive Boomy x%d -> level %d", progressive_boomy, target)

    bracelet_count = counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_BRACELET]]
    if bracelet_count > 0:
        current = await ctx.pine.read32(ADDR_BRACELET_BITFIELD)
        effective_count = min(7, bracelet_count)
        target_bits = (1 << (effective_count + 1)) - 1
        target = current | target_bits
        if target != current:
            await ctx.pine.write32(ADDR_BRACELET_BITFIELD, target)
            kya_logger.info("ITEM <- Archipelago: Progressive Bracelet x%d -> 0x%02X", bracelet_count, target)

    board_count = counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_BOARD]]
    if board_count > 0:
        current = await ctx.pine.read32(ADDR_BOARD_LEVEL)
        target = max(current, min(2, board_count))
        if target != current:
            await ctx.pine.write32(ADDR_BOARD_LEVEL, target)
            kya_logger.info("ITEM <- Archipelago: Progressive Board x%d -> level %d", board_count, target)

    rune_count = sum(counts[ITEM_NAME_TO_ID[name]] for name in ITEM_RUNE_SCENARIO_VARS)
    gauge_count = counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_MAGIC_GAUGE]]
    if (rune_count > 0 or gauge_count > 0) and ctx.last_magic_level is not None:
        # AP Rune authority: each of the six Runes is exactly +50 mana.  Bonus
        # Progressive Magic Gauge upgrades are banked until all six Runes are
        # owned so they cannot bypass the confirmed 350-mana Wolfen City wall.
        rune_total = len(ITEM_RUNE_SCENARIO_VARS)
        active_gauge_bonus = gauge_count if rune_count >= rune_total else 0
        target_level = min(10, 1 + rune_count + active_gauge_bonus)
        if ctx.last_magic_level != target_level:
            await ctx.pine.write32(ADDR_MAGIC_GAUGE_LEVEL, target_level)
            ctx.last_magic_level = await ctx.pine.read32(ADDR_MAGIC_GAUGE_LEVEL)
        kya_logger.info(
            "AP magic authority: runes=%d/%d, banked_gauge=%d, active_gauge=%d -> level %d (%d mana)",
            rune_count, rune_total, gauge_count, active_gauge_bonus, ctx.last_magic_level, ctx.last_magic_level * 50,
        )

    # AP Progressive Life Gauge is the sole authority for max HP. Vanilla HP
    # Ups / Energy Bars are locations only and are reconciled back to this target.
    life_count = counts[ITEM_NAME_TO_ID[ITEM_PROGRESSIVE_LIFE_GAUGE]]
    life_base, life_step, life_cap = 50, 50, 250
    life_target = min(life_cap, life_base + max(0, int(life_count)) * life_step)
    life_current = int(await ctx.pine.read32(ADDR_LIFE_GAUGE))
    valid_life_values = {50, 100, 150, 200, 250}
    if life_current in valid_life_values and life_current != life_target:
        await ctx.pine.write32(ADDR_LIFE_GAUGE, life_target)
        verified_life = int(await ctx.pine.read32(ADDR_LIFE_GAUGE))
        player = int(await ctx.pine.read32(ADDR_PLAYER_POINTER))
        if _valid_ee_pointer(player):
            max_addr = player + PLAYER_MAX_HP_OFFSET
            hp_addr = player + PLAYER_HP_OFFSET
            await ctx.pine.write32(max_addr, _float_to_u32(float(life_target)))
            hp = _u32_to_float(int(await ctx.pine.read32(hp_addr)))
            if hp == hp and 0.0 <= hp < 10000.0 and hp > float(life_target):
                await ctx.pine.write32(hp_addr, _float_to_u32(float(life_target)))
        kya_logger.info(
            "AP Life Gauge authority: vanilla/current %d -> AP target %d (Progressive Life Gauge x%d)",
            life_current, verified_life, life_count,
        )

    # Confirmed inventory/key-item possession flags. Do not downgrade items already earned.
    for item_name, address in ITEM_SCENARIO_FLAGS.items():
        item_id = ITEM_NAME_TO_ID[item_name]
        if counts[item_id] > 0:
            current = await ctx.pine.read32(address)
            if current < 1:
                await ctx.pine.write32(address, 1)
                verified = await ctx.pine.read32(address)
                kya_logger.info(
                    "ITEM <- Archipelago: %s -> ScenarioVar 0x%08X = 1 (readback=%d)",
                    item_name, address, verified,
                )

    # Rune flags are progression ScenarioVars. Keep received runes applied
    # after a game reload without downgrading a rune already earned in-game.
    for rune_name, address in ITEM_RUNE_SCENARIO_VARS.items():
        item_id = ITEM_NAME_TO_ID[rune_name]
        if counts[item_id] > 0:
            current = await ctx.pine.read32(address)
            if current < 2:
                await ctx.pine.write32(address, 2)
                verified = await ctx.pine.read32(address)
                kya_logger.info(
                    "ITEM <- Archipelago: %s -> ScenarioVar 0x%08X = 2 (readback=%d)",
                    rune_name, address, verified,
                )
            linked_location = ITEM_TO_SPECIAL_LOCATION.get(rune_name)
            if linked_location:
                ctx.special_states[linked_location] = True


async def game_watcher(ctx: KyaContext) -> None:
    while not ctx.exit_event.is_set():
        try:
            if await _ensure_pine(ctx):
                await _read_player_state(ctx)
                await _read_actor_manager_wolfens(ctx)
                await _read_actor_manager_fast_travels(ctx)
                await _read_special_flags(ctx)
                await _read_validation_probes(ctx)
                await _read_shop_checks(ctx)
                await _read_goal(ctx)
                await _send_pending_checks(ctx)
                await _apply_received_items(ctx)
        except (PineError, OSError, ConnectionError) as exc:
            await ctx.pine.close()
            ctx.pine_game_verified = False
            ctx._pine_connection_announced = False
            ctx.actor_manager_baselined = False
            ctx.special_baselined = False
            ctx.fast_travel_baselined = False
            ctx.active_fast_travel_states.clear()
            ctx.active_fast_travel_keys.clear()
            ctx.validation_probes_baselined = False
            ctx.shop_baselined = False
            ctx.shop_states.clear()
            ctx.shop_reward_snapshots.clear()
            ctx.shop_money_last = None
            ctx.shop_purchase_tokens.clear()
            ctx.shop_ambiguous_token_warned.clear()
            ctx.shop_unconfirmed_stock.clear()
            message = str(exc)
            if message != ctx._last_pine_error:
                kya_logger.warning("PINE error: %s", message)
                ctx._last_pine_error = message

        await asyncio.sleep(0.40)


async def _async_main(args) -> None:
    ctx = KyaContext(args.connect, args.password)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    watcher = asyncio.create_task(game_watcher(ctx), name="KyaPINEWatcher")

    await ctx.exit_event.wait()
    ctx.server_address = None
    watcher.cancel()
    try:
        await watcher
    except asyncio.CancelledError:
        pass
    await ctx.shutdown()


def launch(*launch_args: str) -> None:
    import colorama

    Utils.init_logging("KyaClient", exception_logger="Client")
    parser = get_base_parser(
        description="Kya: Dark Lineage Archipelago demo client (PCSX2/PINE)."
    )
    args, _rest = parser.parse_known_args(list(launch_args))

    colorama.init()
    try:
        asyncio.run(_async_main(args))
    finally:
        colorama.deinit()
