from collections.abc import Callable, Iterator, Sequence
from typing import Any, Dict, List
from mods_base import Mod
from mods_base.mod_list import get_ordered_mod_list
from mods_base.options import BaseOption, GroupedOption, HiddenOption, KeybindOption

from .controller_bind import ControllerBind
from . import game_states


class RebindMod(Mod):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.bindsOption = HiddenOption("ModBinds", {})
        self.bindsOption.mod = self
        self.options = [*self.options, self.bindsOption]
        self.allBindsByMod: Dict[str, List[ControllerBind]] = {}
    
    
    def refresh_binds(self):
        """
        Goes through all loaded mod keybinds and:
        + If no corresponding binds exist in the settings dict, stores placeholder ones.
        + If mod is enabled, creates the linked ControllerBinds.
        We should never remove from the save options list, in case mods are unloaded, just add to it.
        """

        settingBindsByMod:Dict[str, Dict[str, Dict[str, Any]]] = self.bindsOption.value
        allBindsByMod:Dict[str, List[ControllerBind]] = {}
        activeBindsByMod:Dict[str, List[ControllerBind]] = {}
        for mod in get_ordered_mod_list():
            if not mod.keybinds:
                continue
            allBindsByMod[mod.name] = []
            activeBindsByMod[mod.name] = []
            if mod.name not in settingBindsByMod:
                settingBindsByMod[mod.name] = {}

            for keybind in mod.keybinds:
                settingBinds = settingBindsByMod[mod.name]
                # Add any missing keybinds as blank settings
                if not any(keybind.identifier == bindID for bindID in settingBinds.keys()):
                    settingBinds[keybind.identifier] = {
                        "buttonHeld" : None,
                        "buttonCombo" : []
                    }
                # Load the ControllerBind for this Keybind
                bind = ControllerBind(keybind)
                bind.buttonHeld = settingBinds[keybind.identifier]["buttonHeld"]
                bind.buttonCombo = settingBinds[keybind.identifier]["buttonCombo"]
                allBindsByMod[mod.name].append(bind)
                if mod.is_enabled and bind.IsSet():
                    activeBindsByMod[mod.name].append(bind)
        game_states.controllerBindsByMod = activeBindsByMod

        self.bindsOption.value = settingBindsByMod
        self.bindsOption.save()
        self.allBindsByMod = allBindsByMod
        # for mod in get_ordered_mod_list():
        #     if mod.name in activeBindsByMod:
        #         misc(f"{mod.name}:{[str(x) for x in activeBindsByMod[mod.name]]}")
    
    
    def clear_all_binds(self) -> None:
        """Clears all of the controller binds, including any in the settings file that aren't loaded."""
        self.bindsOption.value = {}
        self.refresh_binds()
    
    
    def load_settings(self) -> None:
        super().load_settings()
        self.refresh_binds()
    
    
    def save_settings(self) -> None:
        """
        Update our bind option for any that have been updated in the keybind menu, before saving
        """
        settingBindsByMod = self.bindsOption.value
        for modName, modBinds in self.allBindsByMod.items():
            if not modName in settingBindsByMod:
                continue
            settingBinds = settingBindsByMod[modName]
            for bind in modBinds:
                settingBinds[bind.keybind.identifier] = {
                    "buttonHeld" : bind.buttonHeld,
                    "buttonCombo" : bind.buttonCombo
                }

        self.bindsOption.value = settingBindsByMod
        return super().save_settings()
    
    
    def iter_display_options(self) -> Iterator[BaseOption]:
        """
        Override the base Mod's method to provide all our ControllerBinds as KeybindOptions

        Yields:
            Options, in the order they should be displayed.
        """
        if any(not opt.is_hidden for opt in self.options):
            yield GroupedOption("Options", self.options)

        allModOptions: GroupedOption = GroupedOption("Controller Binds", [])
        for modName, modBinds in self.allBindsByMod.items():
            if any(not opt.keybind.is_hidden for opt in modBinds):
                yield GroupedOption(
                    modName,
                    [bind.ToKeybindOption() for bind in modBinds],
                )
        yield allModOptions
