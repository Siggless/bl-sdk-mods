from typing import Any, List
from mods_base import EInputEvent, hook, Game
from mods_base.hook import add_hook, remove_hook
from mods_base.options import KeybindOption, KeybindType
from unrealsdk.hooks import Type, Block
from unrealsdk.logging import error
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
from willow2_mod_menu.data_providers.mod_options import ModOptionsDataProvider, KB_TAG_HEADER, KB_TAG_KEYBIND, KB_TAG_UNREBINDABLE
from willow2_mod_menu.options_menu import data_provider_stack

from .controller_bind import ControllerBind
from .game_commands import MODIFIER_BUTTONS
from .rebind_mod import RebindMod

"""
AFAIK I can't provide a subclass of ModOptionsDataProvider to the options_menu,
 so the plan is to edit the keybind options using POST hooks, so they are ignored
 by the mod menu, but we can catch them with our own hooks.
 
This is mostly copied from options_menu.py and mod_options.py's ModOptionsDataProvider.
"""


KB_TAG_C_KEYBIND = "controllerBinds:keybind"
KB_TAG_C_UNREBINDABLE = "controllerBinds:unrebindable"
KB_TAG_C_HEADER = "controllerBinds:header"

# Called when filling in the kb/m options menu with it's keybinds. We need to use this to set the
# This POST hook will occur after the willow2_mod_menu has done its thing,
#  and added the controller binds list (from our overidden iter_mod_options).
@hook(
    "WillowGame.WillowScrollingListDataProviderKeyboardMouseOptions:extOnPopulateKeys",
    Type.POST_UNCONDITIONAL,
    immediately_enable=True,
)
def dataprovider_kbm_populate_keys(
    obj: UObject,
    _2: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> None:
    if not data_provider_stack:
        return None
    if not isinstance(data_provider_stack[-1], ModOptionsDataProvider):
        return None
    
    # Change the tags on all the populated keybinds to ours
    for keyBindInfo in obj.KeyBinds:
        tag: str = keyBindInfo.Tag
        if tag.startswith(KB_TAG_HEADER):
            keyBindInfo.Tag = tag.replace(KB_TAG_HEADER, KB_TAG_C_HEADER)
        elif tag.startswith(KB_TAG_KEYBIND):
            keyBindInfo.Tag = tag.replace(KB_TAG_KEYBIND, KB_TAG_C_KEYBIND)
        elif tag.startswith(KB_TAG_UNREBINDABLE):
            keyBindInfo.Tag = tag.replace(KB_TAG_UNREBINDABLE, KB_TAG_C_UNREBINDABLE)
    # We also need to update the ControllerMappingClip's tag data
    data_provider_stack[-1].populate_keybind_keys(obj)


# Called when starting a rebind. We use it to block rebinding some entries in our custom menus.
# The default mod menu hook shouldn't 
@hook(
    "WillowGame.WillowScrollingListDataProviderKeyboardMouseOptions:DoBind",
    immediately_enable=True,
)
def dataprovider_kbm_do_bind(
    obj: UObject,
    _2: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> type[Block] | None:
    if not data_provider_stack:
        return None
    if not isinstance(data_provider_stack[-1], ModOptionsDataProvider):
        return None
    if not type(data_provider_stack[-1].mod) is RebindMod:
        return None
    
    tag: str = obj.KeyBinds[obj.CurrentKeyBindSelection].Tag
    if tag.startswith((KB_TAG_C_HEADER, KB_TAG_C_UNREBINDABLE)):
        return Block

    GamepadRebind(obj, _2, _3, _4)
    
    return Block


# This section handles the actual custom rebind popups
NO_MODIFIER_BUTTON = "XboxTypes_X" if Game.get_current() is not Game.TPS else "XboxTypeS_X"
CLEAR_BIND_BUTTON = "XboxTypeS_Y"


def GamepadRebind(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction) -> type[Block] | None:
    """
    Shows the rebind dialogs and processes the key rebinds from those.
    """
    menu_data_provider = obj
    controllerClip = obj.ControllerMappingClip
    gfxManager = obj.WPCOwner.GFxUIManager
    
    data_provider = data_provider_stack[-1]
    if not isinstance(data_provider, ModOptionsDataProvider):
        return
    
    # From ModOptionsDataProvider.handle_key_rebind 
    idx: int = obj.CurrentKeyBindSelection
    key_entry: WrappedStruct
    option: KeybindOption
    # Yeeaaaah should've made a proper ControllerBindOption but I'm just encoding to string here, to pass through KeybindOption
    bind = ControllerBind(KeybindType("None", None))

    try:
        key_entry = obj.KeyBinds[idx]
        option = data_provider.drawn_keybinds[idx]
    except (IndexError, KeyError):
        error(f"Can't find key for CurrentKeyBindSelection {idx}")
        return
    
    # First, bind a modifier key
    dialog: UObject = gfxManager.ShowDialog()
    dialog.AutoLocEnable("WillowMenu", "dlgKeyBind")
    title = dialog.Localize("dlgKeyBind", "Caption", "WillowMenu")
    msg = f"Press a <font color=\"#A1E4EF\">MODIFIER</font> button, which will activate this bind when held:\n"
    for b in MODIFIER_BUTTONS:
        msg += f"<StringAliasMap:{b}> {ControllerBind.button_string(b)}\n"
    msg += f"<StringAliasMap:{NO_MODIFIER_BUTTON}> None (no modifier button required)\n"
    msg += f"\nPress <StringAliasMap:{CLEAR_BIND_BUTTON}> to clear the keybind.\n"
    msg += f"\nPress any other button to cancel.\n"
    dialog.SetText(title, msg)
    dialog.SetVariableString("tooltips.text", f"Press any other button to cancel")
    dialog.ApplyLayout()

    def GamepadHandleInputKeyOne(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction) -> type[Block] | None:
        """
        This function handles input for the first step dialog for the controller modifier key rebind
        """
        nonlocal bind, option
        if obj != dialog:
            return None
        
        if args.uevent == EInputEvent.IE_Released:
            dialog.Close()
            remove_hook("WillowGame.WillowGFxDialogBox:HandleInputKey", Type.PRE, "ControllerBinds.InputOne")
            
            if args.ukey == CLEAR_BIND_BUTTON:
                bind.Clear()
                option.value = bind.to_string()

                
            elif args.ukey == NO_MODIFIER_BUTTON or args.ukey in MODIFIER_BUTTONS:
                if args.ukey != NO_MODIFIER_BUTTON:
                    bind.buttonHeld = args.ukey
                option.value = bind.to_string()
                buttonIcon = f"<StringAliasMap:{bind.buttonHeld}>"
                
                # Then, bind a normal key
                dialogSecond = gfxManager.ShowDialog()
                title = dialogSecond.Localize("dlgKeyBind", "Caption", "WillowMenu")
                if bind.buttonHeld == None:
                    msg = f"Now press the button you wish to bind \"{option.display_name}\" to."
                    dialogSecond.SetVariableString("tooltips.text", f"Press Escape to cancel")
                else:
                    msg = f"Now input the button sequence you wish to bind \"{option.display_name}\" to."
                    msg += f"\nPress the <font color=\"#A1E4EF\">MODIFIER</font> button {buttonIcon} to end the sequence.\n\n"
                    dialogSecond.SetVariableString("tooltips.text", f"Press {ControllerBind.button_string(bind.buttonHeld)} or Escape to finish")
                dialogSecond.SetText(title, msg)
                dialogSecond.ApplyLayout()

                def GamepadHandleInputKeyTwo(obj: UObject, args: WrappedStruct, _3: Any, _4: BoundFunction) -> type[Block] | None:
                    """
                    This function handles input for the second step dialog for the contoller key rebind
                    """
                    nonlocal bind
                    if obj != dialogSecond:
                        return None
                    if args.ukey and args.uevent == EInputEvent.IE_Released:
                        if bind.IsNormalBind() or args.ukey in ("Escape", bind.buttonHeld):
                            if bind.IsNormalBind() and args.ukey:
                                bind.buttonCombo = [args.ukey]
                            option.value = bind.to_string()
                            
                            dialogSecond.Close()
                            remove_hook("WillowGame.WillowGFxDialogBox:HandleInputKey", Type.PRE, "ControllerBinds.InputTwo")
                            
                        else:
                            bind.buttonCombo.append(args.ukey)
                            obj.SetText(title, obj.DlgTextMarkup + f"<StringAliasMap:{args.ukey}>")
                            dialogSecond.ApplyLayout()
                        
                    key_entry.Object.SetString(
                        "value",
                        bind.bind_string(),
                        None
                    )
                    controllerClip.InvalidateKeyData()
                    return Block
                
                add_hook("WillowGame.WillowGFxDialogBox:HandleInputKey", Type.PRE, "ControllerBinds.InputTwo", GamepadHandleInputKeyTwo)

            key_entry.Object.SetString(
                "value",
                bind.bind_string(),
                None
            ) 
            controllerClip.InvalidateKeyData()
        return Block
    
    add_hook("WillowGame.WillowGFxDialogBox:HandleInputKey", Type.PRE, "ControllerBinds.InputOne", GamepadHandleInputKeyOne)
    return Block
