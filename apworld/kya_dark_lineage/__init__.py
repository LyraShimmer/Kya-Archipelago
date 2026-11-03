# Register the Launcher component when Archipelago imports this APWorld.
from . import components as _components  # noqa: F401

# Importing the World subclass registers the game with Archipelago.
from .world import KyaDarkLineageWorld

__all__ = ["KyaDarkLineageWorld"]
