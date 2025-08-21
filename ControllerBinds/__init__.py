from typing import Any, Dict, List
from mods_base import build_mod, get_pc, hook, keybind, mod_list, EInputEvent, ENGINE
from unrealsdk.hooks import Type, Block
from unrealsdk.logging import misc
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

from .controller_bind import ControllerBind
from .menu_mods import *
from .rebind_mod import RebindMod
from .menu_mod_options import *


@hook("WillowGame.FrontendGFxMovie:Start", Type.POST_UNCONDITIONAL)
def MainMenu(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    #mod.load_settings() # Not all mods may be loaded when we build initially
    mod.refresh_binds()  # TODO also call this whenever a mod's keybinds change (???? really if they are still the same object, should be OK)
    if not get_pc().WorldInfo.bIsMenuLevel:
        return
    # TODO this needs to happen on main menu or something - currently this only gets mods that are enabled right on bootup!

mod = build_mod(cls=RebindMod)
