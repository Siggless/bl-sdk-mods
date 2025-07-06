from typing import Any, Dict, List
from mods_base import build_mod, get_pc, hook, keybind, mod_list, EInputEvent
from mods_base.hook import add_hook, remove_hook
from mods_base.keybinds import KeybindBlockSignal, KeybindCallback_NoArgs, KeybindCallback_Event, KeybindType
from mods_base.mod import Mod
from mods_base.mod_list import get_ordered_mod_list
from unrealsdk import find_object
from unrealsdk.hooks import Type, Block
from unrealsdk.logging import misc
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
#from .controllerBind import ControllerBind


class ControllerBind():
    def __init__(self, keybind:KeybindType):
        self.keybind = keybind
        self.callback = keybind.callback
        self.buttonHeld: str = "None"
        self.buttonCombo: List[str] = []
        
    def GetCallback(self) -> KeybindCallback_Event | KeybindCallback_NoArgs | None:
        return self.keybind.callback
        
    def __str__(self) -> str:
        return f"{self.buttonHeld} + {self.buttonCombo}"
        
controllerBindsByMod: Dict[str, List[ControllerBind]]


def RefreshBinds():
    global controllerBindsByMod
    controllerBindsByMod = {}
    for mod in get_ordered_mod_list():
        #if mod.keybinds:
        if mod.name not in controllerBindsByMod:
            controllerBindsByMod[mod.name] = []
            # TODO store in mod settings really, so saved and loaded!!!!!!!!!!!!!
        for keybind in mod.keybinds:
            controllerBindsByMod[mod.name].append(ControllerBind(keybind))
        # TESTING WITH THIS MOD ONLY
        if mod.name == "Ambient Spawns":
            controllerBindsByMod[mod.name][0].buttonHeld = "XboxTypeS_Back"
            controllerBindsByMod[mod.name][0].buttonCombo = ["XboxTypeS_A"]
        misc(f"{mod.name}:{[str(x) for x in controllerBindsByMod[mod.name]]}")

RefreshBinds()  # TODO also call this whenever a mod's keybinds change (???? really if they are still the same object, should be OK)
# TODO this needs to happen on main menu or something - currently this only gets mods that are enabled right on bootup!


class InputState():
    def Enter(self, heldKey:str):
        pass
    def Exit(self):
        pass
    def ReceiveInput(self, key: str, event: EInputEvent) -> bool:
        """return True to Block this input, else False"""
        raise NotImplementedError
    def GFxMovieOpened(self):
        raise NotImplementedError
    def BlockBehavior(self, command_key:str) -> type[Block] | None:
        return None
    

class Idle(InputState):
    def Enter(self, heldKey:str):
        # Upon returning to this state from Held, we still need to Block the consumed heldKey
        # This is a bit bodgey - Held state could only change back to this state after blocking that key in BlockBehavior
        self.blockKey = heldKey
    
    def ReceiveInput(self, key: str, event: EInputEvent) -> bool:
        if event is not EInputEvent.IE_Pressed:
            return False
        misc(f"Idle pressed {key}")
        for mod in get_ordered_mod_list():
            if not mod.is_enabled:
                continue
            for bind in controllerBindsByMod[mod.name]:
                if bind.buttonHeld == key:
                    ChangeToState(Held, key)
                    return True
        return False
    
    def GFxMovieOpened(self):
        raise NotImplementedError
    
    def BlockBehavior(self, command_key: str) -> type[Block] | None:
        if self.blockKey not in _controller_commands:
            return
        if command_key in _controller_commands[self.blockKey]:
            # This should be the command thata consumed modifier key would trigger upon release
            self.blockKey = None
            return Block
    
    
class Held(InputState):
    def Enter(self, heldKey:str):
        self.heldButton = heldKey
        self.heldButtonConsumed = False
        self.lastComboButton = "None"
        self.validBindsByMod: Dict[str, Dict[ControllerBind, List[str]]] = {}
        # Make a list of all mod keybinds with that held button here
        for mod in get_ordered_mod_list():
            validBinds = [k for k in controllerBindsByMod[mod.name] if k.buttonHeld == self.heldButton]
            if not validBinds:
                continue
            # Add this mod's valid bind to the dict, with a mod identifier
            thisModBinds = self.validBindsByMod[mod.name] = {}
            for bind in validBinds:
                thisModBinds[bind] = [*bind.buttonCombo]
            # Then each time we recieve a new input, pop any non-matching keybind from that list
            misc(self.validBindsByMod)
    
    def ReceiveInput(self, key: str, event: EInputEvent) -> bool:
        if key == self.heldButton and event == EInputEvent.IE_Released:
            misc(f"Released held key {key}")
            ChangeToState(Idle, self.heldButton if self.heldButtonConsumed else "")
            return True
        
        if event == EInputEvent.IE_Repeat:
            return True
        
        self.lastComboButton = key
        invalidModNames:List[str] = []  # Since we can't pop from the dict whilst iterating over it
        for modName, modBinds in self.validBindsByMod.items():
            invalidBinds = []
            for bind, combo in modBinds.items():
                if not combo or combo[0] != key:
                    # This bind is no longer valid for the input combo
                    invalidBinds.append(bind)
                    continue
                misc(f"Still valid bind {bind.buttonHeld} + {bind.buttonCombo}")
                combo.pop(0)
                if not combo:
                    # This bind combo has been completed! Fire it
                    misc("Firing this bind!")
                    callback: KeybindCallback_NoArgs = bind.callback
                    callback()
                    self.heldButtonConsumed = True
                    return True
            
            for bind in invalidBinds:
                modBinds.pop(bind)
                if len(modBinds) == 0:
                    invalidModNames.append(modName)
        
        for modName in invalidModNames:
            self.validBindsByMod.pop(modName)
        
        return True
                
    def GFxMovieOpened(self):
        raise NotImplementedError
    
    def BlockBehavior(self, command_key: str) -> type[Block] | None:
        if command_key in _controller_commands[self.lastComboButton]:
        # This is a command that the modded controller key would trigger (there might be multiple that have to be skipped here)
            return Block

        if command_key in _controller_commands[self.heldButton]:
            # This should be the command that the modifier key would trigger
            return Block
    
    
currentState: InputState = Idle()
def ChangeToState(newState:type[InputState], key:str = ""):
    global currentState
    currentState.Exit()
    currentState = newState()
    currentState.Enter(key)
    misc(f"Changed to state {str(newState)}") 
    
    
@hook("WillowGame.WillowUIInteraction:InputKey")
def ui_interaction_input_key(
    _1: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> type[Block] | None:
    if not args.bGamepad:
        return
    
    block = currentState.ReceiveInput(args.Key, args.Event)
    if block:
        return Block


@hook("WillowGame.WillowGFxUIManager:PlayMovie")
def gfx_movie_opened(
    _1: UObject,
    _2: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> type[Block] | None:
    misc("PlayMovie")
    currentState.GFxMovieOpened()


####################################
## Disable existing game hold binds
####################################
"""
This section handles processing the modded binds and preventing the normal InputActionDefinition from firing when a modded bind is used instead.
I hook into WillowUIInteraction.InputKey just like the KeybindManager, but check for controller keys.
Note there is an issue, where if a mod bind opens a GFxMovie (e.g. Skill Saver mod), this breaks the sequence and still fires the normal behavior,
 and prevents the next action from that key. I've bodged a fix for the behavior firing in this case.

I basically rewrite the game's controller presets and custom bindings.
I build a dict of all commands/behaviours for all buttons so that I can hook in and prevent these from firing when the alterate bind is pressed.
I also remove some existing Hold actions in GD_Input.Devices.InputDevice_Controller, to facilitate our modifierKeys being held without firing those.
"""

_MODIFIER_BUTTONS = ["XboxTypeS_Start", "XboxTypeS_Back"]
""" Hard-coded modifier keys. These get their existing Hold actions removed and must be combined with a normal button to activate the modded keybind."""
_controller_commands = {}
"""
Dictionary of Commands to check for override later - note Melee, Reload, ThrowGrenade and SkipCinematic are different Behavior classes, so I store the class name for those instead of the command.
{Key, {Behaviour Command or Class Name, Behaviour Class} }
"""
_removed_actions = {}
"""Removed actions to prevent clashing with holding a modifier key down (Back bound to InputActionDefinition'GD_Input.Actions.InputAction_ShowMap')"""
def RecreateControllerInputDict(PC) -> None:
    """
    This method recreates our controller mapping dictionary `_controller_commands`
     It first takes the default mappings from `GD_Input.Devices.InputDevice_Controller`
     Then it applies Preset remappings to that e.g. `GD_Input.Remapping.InputRemapping_Xbox_Angelic`
     Then it applies Custom swapped buttons from that Preset, defined in `WillowPlayerInput.ControllerRebindings`
    """
    global _controller_commands, _removed_actions
    
    def AddInputAction(a, key_name):
        """
        Adds an InputActionDefinition to the controller bind dictionary
        """
        if len(a.OnBegin) > 0:
            beginBehavior = a.OnBegin[0]
            if beginBehavior.Class.Name == "Behavior_ClientConsoleCommand":
                _controller_commands[key_name][beginBehavior.Command] = str(beginBehavior.Class)
            else:
                # This is a special behaviour so store the class name for lookup instead of the command
                _controller_commands[key_name][beginBehavior.Name] = str(beginBehavior.Class)
        
        if len(a.OnEnd) > 0:
            endBehavior = a.OnEnd[0]
            if endBehavior.Class.Name == "Behavior_ClientConsoleCommand":
                _controller_commands[key_name][endBehavior.Command] = str(endBehavior.Class)

    def SwapButtons(default, remapped) -> None:
        """
        Swaps two keys' actions in the dictionary
        """
        if b.DefaultKeyName not in alreadySwapped:
            defaultItem = _controller_commands[default]
            remappedItem = _controller_commands[remapped]
            _controller_commands[default] = remappedItem
            _controller_commands[remapped] = defaultItem
            alreadySwapped.append(default)
            alreadySwapped.append(remapped)
        return
        
    # This is the default input mappings - the current preset is a InputRemappingDefinition which just contains the CHANGES from this default mapping
    controllerInput = find_object("InputDeviceDefinition", "GD_Input.Devices.InputDevice_Controller")
    for b in controllerInput.Buttons:
        _controller_commands[b.KeyName] = {}
        for a in b.PressActions:
            AddInputAction(a, b.keyName)
        for a in b.TapActions:
            AddInputAction(a, b.keyName)
        for a in b.HoldActions:
            AddInputAction(a, b.keyName)
            
        if b.KeyName in _MODIFIER_BUTTONS:
            # Remove this hold action from the button - we want to use this hold instead!
            _removed_actions[b.keyName] = b.HoldActions
            b.HoldActions = ()
    
    # Now we apply the controller preset
    presetIndex = PC.PlayerInput.ControllerPresetIndex
    PCGlobals = PC.GetWillowGlobals()
    if PCGlobals.GetPlatform() == 2:
        # Don't know if PS3 uses same index; Not tested
        preset = PCGlobals.GetGlobalsDefinition().ControllerPresetsPS3[presetIndex]
    else:
        preset = PCGlobals.GetGlobalsDefinition().ControllerPresetsXbox360[presetIndex]
        
    alreadySwapped = []
    for b in preset.RemappedButtons:
        # If a RemappedKeyName is given and different than the DefaultKeyName, then just swap these buttons
        if b.DefaultKeyName != b.RemappedKeyName:
            SwapButtons(b.DefaultKeyName, b.RemappedKeyName)
        else:
            # Otherwise, need to replace the specific actions
            _controller_commands[b.DefaultKeyName] = {}
            for a in b.RemappedPressActions:
                AddInputAction(a, b.DefaultKeyName)
            for a in b.RemappedTapActions:
                AddInputAction(a, b.DefaultKeyName)
            for a in b.RemappedHoldActions:
                AddInputAction(a, b.DefaultKeyName)
        
    # Now we apply any player custom rebindings
    for b in PC.PlayerInput.ControllerRebindings:
        SwapButtons(b.DefaultKeyName, b.RemappedKeyName)
        
    return


@hook("WillowGame.WillowPlayerController:SetControllerPreset", Type.POST_UNCONDITIONAL)
def SetControllerPreset(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction,) -> None:
    """
    This function is called when player settings are loaded, and whenever the controller bindings change.
    We use this to update our button mapping dictionary if the player changes options in-game.
    This is a POST hook, to get the updated preset index amd rebindings.
    """
    RecreateControllerInputDict(obj)


@hook("Engine.Behavior_ClientConsoleCommand:ApplyBehaviorToContext")
def InputCommand(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction,) -> type[Block] | None:
    """
    This function fires whenever a Behavior_ClientConsoleCommand is called (from an InputAction)
    I use this to prevent input button actions from firing when a modded bind has been used for this button e.g. InputActionDefinition GD_Input.Actions.InputAction_Jump
    Note for some reason calling unrealsdk.Log here causes other mod hooks like PickupAsTrash's NextWeapon() to break.
    """
    return currentState.BlockBehavior(obj.Command)


def InputPlayerBehavior(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction,) -> type[Block] | None:
    """
    This function fires whenever a BehaviorBase class that is hooked from out dictionary is called (from an InputAction)
    I use this to prevent input button actions from firing when a modded bind has been used for this button e.g. InputActionDefinition GD_Input.Actions.InputAction_ThrowGrenade
    """
    return currentState.BlockBehavior(obj.Name)

# Create the action dictionary so we know which actions to skip later
RecreateControllerInputDict(get_pc())
# Create the hooks for each of the special Behavior classes in the dictionary
for k in _controller_commands:
    for behaviourClass in _controller_commands[k].values():
        if behaviourClass != "Engine.Behavior_ClientConsoleCommand":
            add_hook(behaviourClass + ".ApplyBehaviorToContext", Type.PRE, "ControllerBinds.GamepadBindManager", InputPlayerBehavior)


####################################
## Fix the controller remapping menu
####################################

####################################
## Add mods bind to main menu
####################################
from willow2_mod_menu.outer_menu import open_mods_menu

_CONTROLLER_KEY_MAP = {
    # Normal Navigation
    "Gamepad_LeftStick_Up": "Up",
    "Gamepad_LeftStick_Down": "Down",
    "XboxTypeS_A": "Enter",
    "XboxTypeS_B": "Escape",
    "XboxTypeS_LeftTrigger": "PageUp",
    "XboxTypeS_RightTrigger": "PageDown",
    # ModMenu Custom Binds
    "XboxTypes_X": "M",     # Lower-case s, typo I guess
    "XboxTypeS_X": "M",     # It's right in TPS
    "XboxTypeS_Y": "Q",
    # Spares
    "XboxTypeS_LeftShoulder": None,
    "XboxTypeS_RightShoulder": None,
    "XboxTypeS_Back": None,
    "XboxTypeS_Start": "E"  # Stops this controller button passing through to open the store link
}
_CONTROLLER_SPARE_KEYS = [  # Spare buttons that can be rebound to mod SettingInputs
    "XboxTypeS_A",
    "XboxTypeS_LeftShoulder",
    "XboxTypeS_RightShoulder",
    "XboxTypeS_Back",
    "XboxTypeS_Start",
]

def GetTooltipString(key: str, GFxMovie:UObject) -> str:
    '''
    Returns the tooltip string for this key
    If a controller is enabled and there is a mapped controller button, then this icon is used instead of the keyboard key
    '''
    if GFxMovie.WPCOwner.PlayerInput.bUsingGamepad:
        for k in _CONTROLLER_KEY_MAP:
            if _CONTROLLER_KEY_MAP[k] == key:
                # Controller key
                if k == "XboxTypes_X":
                    k = "XboxTypeS_X"    # Fuck that typo - The input name is lower case, but the icon name is upper case
                return "<StringAliasMap:" + k + ">"
    # Keyboard key
    return f"[{key}]"


@hook("WillowGame.FrontendGFxMovie:UpdateTooltips", Type.POST_UNCONDITIONAL, immediately_enable=True)
def frontend_update_tooltips(
    obj: UObject,
    _2: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> None:
    if obj.WPCOwner.PlayerInput.bUsingGamepad and obj.MyFrontendDefinition:
        tooltip:str = obj.GetVariableString(obj.MyFrontendDefinition.TooltipPath)
        tooltip = tooltip.replace("[M]", GetTooltipString("M", obj))
        obj.SetVariableString(obj.MyFrontendDefinition.TooltipPath, obj.ResolveDataStoreMarkup(tooltip))
        
    
# Called on pressing keys in the menus, we use it to add a key shortcut.
# Since pause menu inherits frontend, one hook is enough
@hook("WillowGame.FrontendGFxMovie:SharedHandleInputKey", immediately_enable=True)
def frontend_input_key(
    obj: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> tuple[type[Block], bool] | None:
    if args.ukey.upper() == "XBOXTYPES_X" and args.uevent == EInputEvent.IE_Released and not obj.IsOverlayMenuOpen():
        open_mods_menu(obj)
        return Block, True

    return None


build_mod()
