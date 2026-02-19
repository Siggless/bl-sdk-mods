from typing import Any
from mods_base import build_mod, hook
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

from .menu_mods import *
from .menu_mod_options import *
from .rebind_mod import RebindMod

# Only assuming AoDK has the same issue as BL2
if Game.get_current() == Game.BL2 or Game.get_current() == Game.AoDK:
    from .menu_controller import *


"""
We need to refresh our binds to match the Keybinds for any enabled mods.
A) When the game starts, after all other mods are loaded.
B) Whenever a mod is enabled/disabled, as we only store binds for enabled mods.
"""

@hook("WillowGame.FrontendGFxMovie:Start", Type.POST_UNCONDITIONAL)
@hook("WillowGame.WillowPlayerController:ApplyControllerPreset")
def MainMenu(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    #print("Refreshing binds!")
    mod.refresh_binds()


mod = build_mod(cls=RebindMod)
