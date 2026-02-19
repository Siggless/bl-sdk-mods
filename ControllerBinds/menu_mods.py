from typing import Any
from mods_base import EInputEvent, hook
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
from willow2_mod_menu.outer_menu import DLC_MENU_CONTROLLER_TO_KB_KEY_MAP, base_mod, drawn_mod_list, is_favourite, open_mods_menu


"""
Add controller bind and change tooltip on the main menu
"""

@hook("WillowGame.FrontendGFxMovie:UpdateTooltips", Type.POST_UNCONDITIONAL, immediately_enable=True)
def frontend_update_tooltips(
    obj: UObject,
    _2: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> None:
    if obj.WPCOwner.PlayerInput.bUsingGamepad and obj.MyFrontendDefinition:
        tooltip:str = obj.GetVariableString(obj.MyFrontendDefinition.TooltipPath)
        tooltip = tooltip.replace("[M]", "<StringAliasMap:XboxTypeS_X>")
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


"""
Change to controller tooltips in the mod menu
"""

def ButtonTooltip(key: str) -> str:
    '''
    Returns the tooltip string for this key
    If a controller is enabled and there is a mapped controller button, then this icon is used instead of the keyboard key
    '''
    for k, v in DLC_MENU_CONTROLLER_TO_KB_KEY_MAP.items():
        if v == key:
            # Controller key
            if k == "XboxTypes_X":
                k = "XboxTypeS_X"    # In BL2 the input name is lower case, but the icon name is upper case
            return f"<StringAliasMap:{k}>"
    # Keyboard key
    return f"[{key}]"


# Called on switching entries in the DLC menu. We use it just to update the favourite tooltip
@hook("WillowGame.MarketplaceGFxMovie:extOnOfferingChanged", Type.POST_UNCONDITIONAL, immediately_enable=True)
def marketplace_offering_changed(
    obj: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> None:
    if not obj.WPCOwner.PlayerInput.bUsingGamepad:
        return
    if (data := args.Data) is None:
        return

    try:
        mod = drawn_mod_list[int(data.GetString(obj.Prop_offeringId))]
    except (ValueError, KeyError):
        return

    tipQ = obj.ResolveDataStoreMarkup(ButtonTooltip('Q'))
    tipSpace = obj.ResolveDataStoreMarkup(ButtonTooltip('Space'))
    tipEnter = obj.ResolveDataStoreMarkup(ButtonTooltip('Enter'))
    favourite_tooltip = (
        "" if mod == base_mod else tipQ + (" Unfavourite" if is_favourite(mod) else " Favourite")
    )
    enable_tooltip = tipSpace + (" Disable" if mod.is_enabled else " Enable")

    obj.SetTooltips(
        f"{tipEnter} Details\n{favourite_tooltip}",
        enable_tooltip,
    )
    return
