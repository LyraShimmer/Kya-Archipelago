from __future__ import annotations

import json
from pathlib import Path


class DataConfigError(RuntimeError):
    pass


def load_game_data(data_dir: Path) -> dict:
    """Load and merge the external Kya data modules.

    Data is intentionally kept outside the executable so reverse-engineered
    mappings/chains can be corrected without recompiling the launcher.
    Duplicate keys are rejected: one subsystem must own each definition.
    """
    data_dir = Path(data_dir)
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        raise DataConfigError(f"Missing data manifest: {manifest_path}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise DataConfigError(f"Invalid data manifest: {exc}") from exc

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise DataConfigError("data/manifest.json has no valid 'files' list.")

    merged: dict = {}
    owners: dict[str, str] = {}
    for filename in files:
        path = data_dir / str(filename)
        if not path.exists():
            raise DataConfigError(f"Missing data module: {path}")
        try:
            block = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise DataConfigError(f"Invalid JSON in {path.name}: {exc}") from exc
        if not isinstance(block, dict):
            raise DataConfigError(f"{path.name} must contain a JSON object.")
        for key, value in block.items():
            if key in merged:
                raise DataConfigError(
                    f"Duplicate data key '{key}' in {path.name}; already owned by {owners[key]}."
                )
            merged[key] = value
            owners[key] = path.name

    required = (
        "AP_BUILD_VERSION",
        "ADDR_ACTOR_MANAGER_GLOBAL",
        "WOLFEN_KEY_TO_LOCATION",
        "FAST_TRAVEL_ALLOWED_ROUTES",
        "SHOP_LOCATION_CONDITIONS",
        "ITEM_NAME_TO_ID",
    )
    missing = [key for key in required if key not in merged]
    if missing:
        raise DataConfigError("Missing required data keys: " + ", ".join(missing))

    return merged
