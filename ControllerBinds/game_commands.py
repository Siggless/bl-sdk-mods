from typing import Any
from mods_base import hook
from unrealsdk import find_object
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

InputActionDefinition = UObject

"""
This file handles preventing the normal InputActionDefinition from firing when a modded bind is used instead.
I basically rewrite the game's controller presets and custom bindings.
I build a dict of all commands/behaviours for all buttons so that I can hook in and prevent these from firing when the alternate bind is pressed.
I also remove some existing Hold actions in GD_Input.Devices.InputDevice_Controller, to facilitate our modifierKeys being held without firing those.
"""

MODIFIER_BUTTONS = ["XboxTypeS_Start", "XboxTypeS_Back"]
""" Hard-coded modifier keys. These get their existing Hold actions removed and must be combined with a normal button to activate the modded keybind."""
controller_commands = {}
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
    global controller_commands, _removed_actions
    controller_commands = {}
    
    def AddInputAction(a: InputActionDefinition, key_name):
        """
        Adds an InputActionDefinition to the controller bind dictionary
        """
        if len(a.OnBegin) > 0:
            beginBehavior = a.OnBegin[0]
            if beginBehavior.Class.Name == "Behavior_ClientConsoleCommand":
                controller_commands[key_name][beginBehavior.Command] = str.split(str(beginBehavior.Class),"\'")[1]
            else:
                # This is a special behaviour so store the class name for lookup instead of the command
                controller_commands[key_name][beginBehavior.Name] = str.split(str(beginBehavior.Class),"\'")[1]
        
        if len(a.OnEnd) > 0:
            endBehavior = a.OnEnd[0]
            if endBehavior.Class.Name == "Behavior_ClientConsoleCommand":
                controller_commands[key_name][endBehavior.Command] = str.split(str(endBehavior.Class),"\'")[1]

    def SwapButtons(default, remapped) -> None:
        """
        Swaps two keys' actions in the dictionary
        """
        if b.DefaultKeyName not in alreadySwapped:
            defaultItem = controller_commands[default]
            remappedItem = controller_commands[remapped]
            controller_commands[default] = remappedItem
            controller_commands[remapped] = defaultItem
            alreadySwapped.append(default)
            alreadySwapped.append(remapped)
        return
        
    # This is the default input mappings - the current preset is a InputRemappingDefinition which just contains the CHANGES from this default mapping
    controllerInput = find_object("InputDeviceDefinition", "GD_Input.Devices.InputDevice_Controller")
    for b in controllerInput.Buttons:
        controller_commands[b.KeyName] = {}
        for a in b.PressActions:
            AddInputAction(a, b.keyName)
        for a in b.TapActions:
            AddInputAction(a, b.keyName)
        for a in b.HoldActions:
            AddInputAction(a, b.keyName)
            
        if b.KeyName in MODIFIER_BUTTONS:
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
            controller_commands[b.DefaultKeyName] = {}
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


@hook("WillowGame.WillowPlayerController:ApplyControllerPreset", Type.POST_UNCONDITIONAL, immediately_enable=True)
def ApplyControllerPreset(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction,) -> None:
    """
    This function is called when player settings are loaded, and whenever the controller bindings change.
    We use this to update our button mapping dictionary if the player changes options in-game.
    This is a POST hook, to get the updated preset index amd rebindings.
    """
    #print("Recreating inputs!")
    RecreateControllerInputDict(obj)
