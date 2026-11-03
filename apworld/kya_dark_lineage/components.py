from worlds.LauncherComponents import Component, Type, components, launch_subprocess

from .constants import GAME_NAME


def launch_client(*args: str) -> None:
    from .client import launch
    launch_subprocess(launch, name="KyaDarkLineageClient", args=args)


components.append(
    Component(
        "Kya: Dark Lineage Client",
        func=launch_client,
        component_type=Type.CLIENT,
        game_name=GAME_NAME,
        supports_uri=False,
        description="Connect Kya PAL SLES_514.73 to Archipelago through PCSX2/PINE.",
    )
)
