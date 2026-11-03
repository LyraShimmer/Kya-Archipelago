from __future__ import annotations

from dataclasses import dataclass
import time

from kya_pine_raw import PineClient

# Kya: Dark Lineage PAL SLES_514.73
# Proven from our own Ghidra/runtime work:
#   shop item virtual getter: vtable + 0xE8 -> 0x003BA710
#   FUN_003BA710 returns object + 0x160
#   item_struct + 0x20 = native item ID
#   item_struct + 0x30 = current Nootie price
SHOP_GETTER = 0x003BA710
VTABLE_GETTER_OFFSET = 0xE8
ITEM_STRUCT_OFFSET = 0x160
ITEM_NATIVE_ID_OFFSET = 0x20
ITEM_PRICE_OFFSET = 0x30

SCAN_WINDOWS = (
    (0x01E00000, 0x02000000),
    (0x01800000, 0x02000000),
)
OBJECT_ALIGNMENT = 0x10
CODE_PTR_MIN = 0x00400000
CODE_PTR_MAX = 0x00480000
MAX_SELECTED_INDEX = 31
MAX_CONTEXT_SLOTS = 16
RECENT_SELECTION_SECONDS = 4.0
# Reconstructed from paired 0% -> purchased live captures and independently
# confirmed on all 18 sold objects in a 100% save (2026-11-03).
# This is an actor STATE word, not a serialized shop-stock bit. It contains
# transient display bits, so compare only the two sold bits and the common
# 0x00080000 class signature. It MUST be read by native-ID-resolved object,
# never through an absolute heap address.
SHOP_ACTOR_STATE_OFFSET = 0x08
SHOP_ACTOR_SOLD_BITS = 0x21
SHOP_ACTOR_CLASS_MASK = 0x00FF0000
SHOP_ACTOR_CLASS_VALUE = 0x00080000
SHOP_SOLD_STABLE_SECONDS = 0.40


def is_native_shop_sold_state(raw: int) -> bool:
    raw = int(raw) & 0xFFFFFFFF
    return bool(
        (raw & SHOP_ACTOR_CLASS_MASK) == SHOP_ACTOR_CLASS_VALUE
        and (raw & SHOP_ACTOR_SOLD_BITS) == SHOP_ACTOR_SOLD_BITS
    )


class NativeSoldStateObserver:
    """Require a stable native sold signature before reconnect recovery.

    It tracks only runtime object identity, native sold bits and monotonic
    time; it never reads/writes game memory or sends an AP check itself.
    """

    def __init__(self, min_stable_seconds: float = SHOP_SOLD_STABLE_SECONDS):
        self.min_stable_seconds = float(min_stable_seconds)
        self.reset()

    def reset(self) -> None:
        self._first_seen: dict[str, tuple[int, float]] = {}

    def observe(self, states: dict[str, tuple[int, int]], now: float) -> list[str]:
        ready: list[str] = []
        new_seen: dict[str, tuple[int, float]] = {}
        for name, (obj, raw) in states.items():
            obj = int(obj)
            if not is_native_shop_sold_state(raw):
                continue
            previous = self._first_seen.get(name)
            since = previous[1] if previous is not None and previous[0] == obj else float(now)
            new_seen[name] = (obj, since)
            if now - since >= self.min_stable_seconds:
                ready.append(name)
        self._first_seen = new_seen
        return ready

PREFIX = "Nativs City - Shop - "

# Native IDs validated by the completed V4 mapping + V6 live 18/18 purchase test.
# ID 16 is intentionally excluded here because both Extra Energy Bars share it;
# those two are separated by their native shop-group context.
NATIVE_ID_TO_NAME = {
    0: PREFIX + "Magic Bouncers",
    1: PREFIX + "Climbing Gloves",
    2: PREFIX + "Basic Boomy",
    3: PREFIX + "Silver Boomy",
    4: PREFIX + "Golden Boomy",
    6: PREFIX + "Yellow Bracelet",
    7: PREFIX + "Green Bracelet",
    8: PREFIX + "Blue Bracelet",
    9: PREFIX + "Brown Bracelet",
    10: PREFIX + "Black Bracelet",
    11: PREFIX + "Silver Bracelet",
    12: PREFIX + "Gold Bracelet",
    15: PREFIX + "Jamgut Birdcall",
    18: PREFIX + "Magic Board",
    19: PREFIX + "Speed Board",
    20: PREFIX + "Telescope",
}
ENERGY_1 = PREFIX + "Extra Energy Bar 1"
ENERGY_2 = PREFIX + "Extra Energy Bar 2"
EXPECTED_NAMES = tuple(list(NATIVE_ID_TO_NAME.values()) + [ENERGY_1, ENERGY_2])

# Vanilla prices for the 18 one-time AP Shop checks. These are used only to
# calculate the YAML-configured target price; native IDs/context remain the
# authoritative identity.
VANILLA_PRICE_BY_NAME = {
    PREFIX + "Basic Boomy": 10,
    PREFIX + "Yellow Bracelet": 100,
    PREFIX + "Telescope": 30,
    PREFIX + "Magic Board": 50,
    PREFIX + "Green Bracelet": 150,
    PREFIX + "Climbing Gloves": 50,
    ENERGY_1: 1000,
    PREFIX + "Blue Bracelet": 200,
    PREFIX + "Jamgut Birdcall": 70,
    PREFIX + "Speed Board": 50,
    PREFIX + "Golden Boomy": 100,
    PREFIX + "Silver Bracelet": 500,
    PREFIX + "Silver Boomy": 100,
    PREFIX + "Brown Bracelet": 250,
    PREFIX + "Magic Bouncers": 50,
    ENERGY_2: 1000,
    PREFIX + "Black Bracelet": 400,
    PREFIX + "Gold Bracelet": 700,
}


def scale_percent(base: int, modifier_percent: int) -> int:
    """Apply AP-style +/- percentage with half-up integer rounding."""
    modifier_percent = max(-100, min(1000, int(modifier_percent)))
    if modifier_percent >= 0:
        modifier_percent = min(1000, ((modifier_percent + 5) // 10) * 10)
    else:
        modifier_percent = max(-100, -(((-modifier_percent + 5) // 10) * 10))
    multiplier = 100 + modifier_percent
    return max(0, (int(base) * multiplier + 50) // 100)


@dataclass(frozen=True)
class ShopObject:
    obj: int
    vtable: int
    native_id: int
    price: int

    @property
    def item_struct(self) -> int:
        return self.obj + ITEM_STRUCT_OFFSET

    @property
    def price_addr(self) -> int:
        return self.item_struct + ITEM_PRICE_OFFSET


@dataclass(frozen=True)
class ShopTable:
    base: int
    selected_index: int
    selected_obj: int
    entries: tuple[tuple[int, ShopObject], ...]


def _scan_window(pine: PineClient, start: int, end: int) -> list[ShopObject]:
    addresses = list(range((start + OBJECT_ALIGNMENT - 1) & ~(OBJECT_ALIGNMENT - 1), end, OBJECT_ALIGNMENT))
    first_words = pine.read32_many(addresses, batch_size=4096)

    possible: list[tuple[int, int]] = []
    vtables: set[int] = set()
    for addr, value in zip(addresses, first_words):
        value = int(value)
        if CODE_PTR_MIN <= value < CODE_PTR_MAX and value % 4 == 0:
            possible.append((addr, value))
            vtables.add(value)
    if not possible:
        return []

    vt_list = sorted(vtables)
    getters = pine.read32_many([vt + VTABLE_GETTER_OFFSET for vt in vt_list], batch_size=4096)
    good_vtables = {vt for vt, getter in zip(vt_list, getters) if int(getter) == SHOP_GETTER}
    if not good_vtables:
        return []

    objects = [(addr, vt) for addr, vt in possible if vt in good_vtables]
    ids = pine.read32_many(
        [obj + ITEM_STRUCT_OFFSET + ITEM_NATIVE_ID_OFFSET for obj, _ in objects],
        batch_size=4096,
    )
    prices = pine.read32_many(
        [obj + ITEM_STRUCT_OFFSET + ITEM_PRICE_OFFSET for obj, _ in objects],
        batch_size=4096,
    )

    out: list[ShopObject] = []
    for (obj, vt), native_id, price in zip(objects, ids, prices):
        native_id = int(native_id)
        price = int(price)
        if not (0 <= native_id <= 0x1000):
            continue
        if not (0 <= price <= 1_000_000):
            continue
        out.append(ShopObject(obj=obj, vtable=vt, native_id=native_id, price=price))
    return out


def scan_shop_objects(pine: PineClient) -> list[ShopObject]:
    best: list[ShopObject] = []
    for start, end in SCAN_WINDOWS:
        rows = _scan_window(pine, start, end)
        rows = sorted({r.obj: r for r in rows}.values(), key=lambda r: (r.native_id, r.price, r.obj))
        if rows:
            best = rows
            if len(rows) >= 10:
                break
    return best


def _scan_ui_region(rows: list[ShopObject]) -> tuple[int, int]:
    lo = min(r.obj for r in rows)
    hi = max(r.obj for r in rows)
    start = max(0x01800000, (lo - 0x100000) & ~0xF)
    end = min(0x02000000, (hi + 0x40000 + 0xF) & ~0xF)
    return start, end


def scan_shop_tables(pine: PineClient, rows: list[ShopObject]) -> list[ShopTable]:
    if not rows:
        return []
    by_obj = {r.obj: r for r in rows}
    object_set = set(by_obj)
    start, end = _scan_ui_region(rows)
    bases = list(range(start, end, OBJECT_ALIGNMENT))

    indices = pine.read32_many([b + 0x94 for b in bases], batch_size=4096)
    prelim = [(b, int(idx)) for b, idx in zip(bases, indices) if 0 <= int(idx) <= MAX_SELECTED_INDEX]
    if not prelim:
        return []

    selected_addrs = [b + idx * 0x18 + 0x04 for b, idx in prelim]
    selected_ptrs = pine.read32_many(selected_addrs, batch_size=4096)
    prelim = [
        (b, idx, int(ptr))
        for (b, idx), ptr in zip(prelim, selected_ptrs)
        if int(ptr) in object_set
    ]
    if not prelim:
        return []

    slot_addrs: list[int] = []
    for b, _, _ in prelim:
        slot_addrs.extend(b + slot * 0x18 + 0x04 for slot in range(MAX_CONTEXT_SLOTS))
    slot_ptrs = pine.read32_many(slot_addrs, batch_size=4096)

    tables: list[ShopTable] = []
    cursor = 0
    seen_signatures: set[tuple[tuple[int, int, int], ...]] = set()
    for b, idx, selected_obj in prelim:
        entries: list[tuple[int, ShopObject]] = []
        seen_obj: set[int] = set()
        for slot in range(MAX_CONTEXT_SLOTS):
            ptr = int(slot_ptrs[cursor])
            cursor += 1
            row = by_obj.get(ptr)
            if row is None or ptr in seen_obj:
                continue
            seen_obj.add(ptr)
            entries.append((slot, row))
        if not entries:
            continue
        sig = tuple((slot, row.obj, row.native_id) for slot, row in entries)
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)
        tables.append(ShopTable(base=b, selected_index=idx, selected_obj=selected_obj, entries=tuple(entries)))
    tables.sort(key=lambda t: (-len(t.entries), t.base))
    return tables


def _table_has_ids(table: ShopTable, ids: set[int]) -> bool:
    present = {row.native_id for _, row in table.entries}
    return ids.issubset(present)


def resolve_mapping(rows: list[ShopObject], tables: list[ShopTable]) -> dict[str, ShopObject]:
    """Resolve the 18 AP one-time Shop locations without using prices as identity."""
    mapping: dict[str, ShopObject] = {}
    by_id: dict[int, list[ShopObject]] = {}
    for row in rows:
        by_id.setdefault(row.native_id, []).append(row)

    for native_id, name in NATIVE_ID_TO_NAME.items():
        hits = by_id.get(native_id, [])
        if len(hits) == 1:
            mapping[name] = hits[0]

    # Both Energy Bars are ID16. Their neighboring native IDs distinguish the
    # two shop groups even if prices are customized later.
    e1: dict[int, ShopObject] = {}
    e2: dict[int, ShopObject] = {}
    for table in tables:
        if _table_has_ids(table, {8, 15, 16}):
            for _, row in table.entries:
                if row.native_id == 16:
                    e1[row.obj] = row
        if _table_has_ids(table, {12, 16}):
            for _, row in table.entries:
                if row.native_id == 16:
                    e2[row.obj] = row
    if len(e1) == 1:
        mapping[ENERGY_1] = next(iter(e1.values()))
    if len(e2) == 1:
        mapping[ENERGY_2] = next(iter(e2.values()))
    return mapping


def snapshot_tables(pine: PineClient, tables: list[ShopTable]) -> dict[int, dict[str, int]]:
    bases = [t.base for t in tables]
    if not bases:
        return {}
    idxs = [int(x) for x in pine.read32_many([b + 0x94 for b in bases], batch_size=512)]
    ptr_addrs: list[int] = []
    valid: list[tuple[int, int]] = []
    for b, idx in zip(bases, idxs):
        if 0 <= idx <= MAX_SELECTED_INDEX:
            ptr_addrs.append(b + idx * 0x18 + 0x04)
            valid.append((b, idx))
    ptrs = pine.read32_many(ptr_addrs, batch_size=512) if ptr_addrs else []
    return {b: {"index": idx, "selected_obj": int(ptr)} for (b, idx), ptr in zip(valid, ptrs)}


class NativeShopResolver:
    """Session-safe Shop resolver used by the launcher.

    Absolute heap addresses are never persisted. A scan reconstructs runtime
    objects/tables from the proven getter chain, then live cursor state identifies
    which one-time AP Shop item produced a Nootie debit.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.rows: list[ShopObject] = []
        self.tables: list[ShopTable] = []
        self.mapping: dict[str, ShopObject] = {}
        self.by_obj: dict[int, tuple[str, ShopObject]] = {}
        self.prev_snapshot: dict[int, dict[str, int]] = {}
        self.prev_indices: dict[int, int] = {}
        self.last_changed: dict[int, float] = {}
        self.last_scan = 0.0
        self.scan_failures = 0
        self.price_modifier_percent = getattr(self, "price_modifier_percent", 0)
        self.target_prices: dict[str, int] = {}

    @property
    def resolved_count(self) -> int:
        return len(self.mapping)

    @property
    def ready(self) -> bool:
        return self.resolved_count == 18 and bool(self.tables)

    def set_price_modifier(self, modifier_percent: int) -> None:
        self.price_modifier_percent = max(-100, min(1000, int(modifier_percent)))

    def read_native_sold_states(self, pine: PineClient) -> dict[str, tuple[int, int]]:
        """Read the sale-state of each uniquely identified live shop actor.

        Validate the original vtable in the same poll so stale heap pointers
        after an actor-generation change cannot masquerade as sold inventory.
        """
        if not self.ready:
            return {}
        names = [name for name in EXPECTED_NAMES if name in self.mapping]
        actors = [self.mapping[name] for name in names]
        vtables = pine.read32_many([row.obj for row in actors], batch_size=128)
        raw_states = pine.read32_many(
            [row.obj + SHOP_ACTOR_STATE_OFFSET for row in actors], batch_size=128
        )
        return {
            name: (row.obj, int(raw))
            for name, row, vt, raw in zip(names, actors, vtables, raw_states)
            if int(vt) == row.vtable
        }

    def current_price(self, name: str) -> int | None:
        if name in self.target_prices:
            return int(self.target_prices[name])
        row = self.mapping.get(name)
        return int(row.price) if row is not None else None

    def enforce_prices(self, pine: PineClient) -> list[tuple[str, int, int]]:
        """Keep the 18 AP Shop prices at their YAML-configured runtime values."""
        if not self.ready:
            return []
        names = [name for name in EXPECTED_NAMES if name in self.mapping]
        addrs = [self.mapping[name].price_addr for name in names]
        current = [int(v) for v in pine.read32_many(addrs, batch_size=128)] if addrs else []
        changes: list[tuple[str, int, int]] = []
        self.target_prices = {}
        for name, old in zip(names, current):
            target = scale_percent(VANILLA_PRICE_BY_NAME[name], self.price_modifier_percent)
            self.target_prices[name] = target
            if old != target:
                pine.write32(self.mapping[name].price_addr, target)
                changes.append((name, old, target))
        return changes

    def scan(self, pine: PineClient, now: float | None = None) -> tuple[int, int, int]:
        if now is None:
            now = time.monotonic()
        rows = scan_shop_objects(pine)
        tables = scan_shop_tables(pine, rows) if rows else []
        mapping = resolve_mapping(rows, tables)
        self.rows = rows
        self.tables = tables
        self.mapping = mapping
        self.by_obj = {row.obj: (name, row) for name, row in mapping.items()}
        self.last_scan = float(now)
        if self.ready:
            self.enforce_prices(pine)
            snap = snapshot_tables(pine, tables)
            self.prev_snapshot = snap
            self.prev_indices = {b: s["index"] for b, s in snap.items()}
            self.last_changed = {b: -1e30 for b in snap}
            self.scan_failures = 0
        else:
            self.prev_snapshot = {}
            self.prev_indices = {}
            self.last_changed = {}
            self.scan_failures += 1
        return len(rows), len(tables), len(mapping)

    def prepare_poll(self, pine: PineClient, now: float) -> tuple[dict[int, dict[str, int]], dict[int, dict[str, int]]]:
        """Return (snapshot_before_this_poll, current_snapshot)."""
        if not self.ready:
            return {}, {}
        before = self.prev_snapshot
        current = snapshot_tables(pine, self.tables)
        for base, state in current.items():
            old_idx = self.prev_indices.get(base)
            if old_idx is not None and state["index"] != old_idx:
                self.last_changed[base] = now
            self.prev_indices[base] = state["index"]
        return before, current

    def commit_poll(self, current_snapshot: dict[int, dict[str, int]]) -> None:
        if current_snapshot:
            self.prev_snapshot = current_snapshot

    def identify_purchase(
        self,
        delta: int,
        before_snapshot: dict[int, dict[str, int]],
        now: float,
        consumed_names: set[str],
    ) -> tuple[str | None, str, list[str]]:
        candidates: list[tuple[int, str, ShopObject, float]] = []
        for base, state in before_snapshot.items():
            pair = self.by_obj.get(int(state["selected_obj"]))
            if pair is None:
                continue
            name, row = pair
            # Use the runtime price field, not a hard-coded vanilla table. This
            # already makes the identity path compatible with future price mods.
            expected_price = self.current_price(name)
            # The game's debit can remain at the vanilla price even when the
            # modded price field has been written (observed at -30%, 2026-10-28).
            # Accept that debit only as a candidate for a *native-selected*
            # article; never infer the article merely from its Nooties price.
            vanilla_price = VANILLA_PRICE_BY_NAME.get(name)
            if int(delta) not in {p for p in (expected_price, vanilla_price) if p is not None}:
                continue
            candidates.append((base, name, row, self.last_changed.get(base, -1e30)))

        recent = [c for c in candidates if now - c[3] <= RECENT_SELECTION_SECONDS]
        if recent:
            recent.sort(key=lambda x: x[3], reverse=True)
            if len(recent) == 1 or recent[0][3] > recent[1][3] + 0.05:
                return recent[0][1], "native recent active shop", sorted({x[1] for x in candidates})

        unique = {name for _, name, _, _ in candidates}
        if len(unique) == 1:
            return next(iter(unique)), "native unique selected item", sorted(unique)

        remaining = {name for _, name, _, _ in candidates if name not in consumed_names}
        if len(remaining) == 1:
            return next(iter(remaining)), "native only unchecked one-time item", sorted(unique)

        return None, "native ambiguous", sorted(unique)

    def identify_selected(
        self,
        before_snapshot: dict[int, dict[str, int]],
        now: float,
        consumed_names: set[str],
    ) -> tuple[str | None, str, list[str]]:
        """Identify the currently selected AP Shop item without using a Nootie debit.

        Used for experimental 0-Nootie/free purchases, where the normal causal
        money token does not exist. Recent cursor movement remains the preferred
        disambiguation signal.
        """
        candidates: list[tuple[int, str, float]] = []
        for base, state in before_snapshot.items():
            pair = self.by_obj.get(int(state["selected_obj"]))
            if pair is None:
                continue
            name, _row = pair
            if name in consumed_names:
                continue
            candidates.append((base, name, self.last_changed.get(base, -1e30)))

        recent = [c for c in candidates if now - c[2] <= RECENT_SELECTION_SECONDS]
        if recent:
            recent.sort(key=lambda x: x[2], reverse=True)
            if len(recent) == 1 or recent[0][2] > recent[1][2] + 0.05:
                return recent[0][1], "native recent active shop (free)", sorted({x[1] for x in candidates})

        unique = {name for _, name, _ in candidates}
        if len(unique) == 1:
            return next(iter(unique)), "native unique selected item (free)", sorted(unique)
        return None, "native free selection ambiguous", sorted(unique)
