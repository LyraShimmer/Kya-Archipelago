"""0.9.61: read-only export of native Nativ shop identity and sold state.

Native sold bits are corroborated by before/after and 100% save dumps.
Export observed state separately from AP ACK; no checks are sent here.
"""
from __future__ import annotations
import csv
from datetime import datetime
from pathlib import Path

FIELDNAMES = (
    'location', 'ap_id', 'ap_status', 'native_id', 'actor_runtime',
    'native_price', 'group_runtime', 'group_slots', 'serialized_flag',
    'reward_raw', 'sold_flag_proven', 'native_state_raw', 'native_sold_candidate',
)


def build_native_shop_audit_rows(names, loc_by_name, checked, pending,
                                 current_shop, current_rewards, resolver, native_sold_states=None):
    """Pure transform; never calls PINE / writes emulator or AP state."""
    checked, pending = set(checked), set(pending)
    mapping = getattr(resolver, 'mapping', {}) or {}
    native_sold_states = native_sold_states or {}
    # Optional scan supplied by the one-owner PINE loop. Never infer sold from
    # serialized flags or from the reward inventory.
    from kya_shop_native import is_native_shop_sold_state
    tables = getattr(resolver, 'tables', ()) or ()
    context = {}
    for tab in tables:
        for slot, obj in tab.entries:
            context.setdefault(int(obj.obj), []).append((int(tab.base), int(slot)))
    rows = []
    for name in names:
        loc_id = loc_by_name.get(name)
        native = mapping.get(name)
        ctx = sorted(set(context.get(int(native.obj), []))) if native is not None else []
        observed = native_sold_states.get(name)
        observed_valid = (native is not None and observed is not None
                          and int(observed[0]) == int(native.obj))
        state = int(observed[1]) if observed_valid else None
        rows.append({
            'location': str(name),
            'ap_id': '' if loc_id is None else int(loc_id),
            'ap_status': ('ACK' if loc_id in checked else
                          'PENDING' if loc_id in pending else 'UNCHECKED'),
            'native_id': '' if native is None else int(native.native_id),
            'actor_runtime': '' if native is None else f'0x{int(native.obj):08X}',
            'native_price': '' if native is None else int(native.price),
            'group_runtime': ','.join(f'0x{b:08X}' for b, slot in ctx),
            'group_slots': ','.join(str(slot) for b, slot in ctx),
            'serialized_flag': ('1' if bool(current_shop.get(name)) else '0'),
            'reward_raw': '' if current_rewards.get(name) is None else current_rewards.get(name),
            'sold_flag_proven': ('OBSERVED' if state is not None and is_native_shop_sold_state(state) else 'NO'),
            'native_state_raw': '' if state is None else f'0x{state:08X}',
            'native_sold_candidate': ('YES' if state is not None and is_native_shop_sold_state(state)
                                      else 'NO' if state is not None else 'UNKNOWN'),
        })
    return rows


def export_native_shop_audit(folder, names, loc_by_name, checked, pending,
                             current_shop, current_rewards, resolver, native_sold_states=None):
    rows = build_native_shop_audit_rows(
        names, loc_by_name, checked, pending,
        current_shop, current_rewards, resolver, native_sold_states)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    filename = folder / ('Kya_Shops_Nativ_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.csv')
    with filename.open('w', encoding='utf-8-sig', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=FIELDNAMES, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)
    return filename, sum(bool(row['actor_runtime']) for row in rows)
