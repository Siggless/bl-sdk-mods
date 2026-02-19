from typing import Any
from mods_base import hook
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct

"""
There is a Gearbox bug in BL2 (and I'm assuming AoDK) that assumed the Controller Presets list item is always
    index 7 in the list (hard-coded), when it was actually index 8. TPS has index 9 hard-coded too.
This caused the selected list item to change when entering Custom mapping mode.
We prevent the 7th item from being added and add it afterwards instead to fix that.
"""

"""
This function is called to populate the GamepadOptions list.
We only enable the AddProfileSettingListItem hook whilst this function is on the stack.
"""
@hook("WillowGame.WillowScrollingListDataProviderGamepadOptions:Populate")
def PopulatePre(*_: Any) -> type[Block] | None:
    AddProfileSettingListItem.enable()
    AddControllerPresets.enable()

@hook("WillowGame.WillowScrollingListDataProviderGamepadOptions:Populate", Type.POST_UNCONDITIONAL)
def PopulatePost(*_: Any) -> None:
    AddProfileSettingListItem.disable()
    AddControllerPresets.disable()
    
    
@hook("WillowGame.WillowScrollingListDataProviderOptionsBase:AddProfileSettingListItem")
def AddProfileSettingListItem(
    obj: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> type[Block] | None:
    """
    This function is called to add each regular item to the GamepadOptions menu
    We need to replace the 7th index (id 128) with the ControllerPreset item
    """
    if args.ProfileSettingId == 128:
        return Block
    

@hook("WillowGame.WillowScrollingListDataProviderGamepadOptions:AddControllerPresets", Type.POST_UNCONDITIONAL)
def AddControllerPresets(
    obj: UObject,
    args: WrappedStruct,
    _3: Any,
    _4: BoundFunction,
) -> None:
    AddProfileSettingListItem.disable()
    obj.AddProfileSettingListItem(args.TheList, 128, "$WillowMenu.MenuOptionDisplayNames.PerShotForceFeedback", "$WillowMenu.MenuOptionDisplayNames.PerShotForceFeedbackDesc")
