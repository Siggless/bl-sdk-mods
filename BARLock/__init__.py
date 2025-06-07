from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
from mods_base import build_mod, hook
from mods_base.options import BoolOption
from typing import Any

optionLockBonusStats = BoolOption(
    "Lock Bonus Stats", False,
    description="Whether BAR bonus stats can be enabled in the in-game menu."
)


@hook("WillowGame.WillowPlayerController:AdjustBadassPoints")
def AdjustBadassPoints(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction) -> Block | None:
    ''' Don't add ranks for challenge completion '''
    return Block


@hook("WillowGame.WillowPlayerController:ApplyAwesomeSkillSaveGameData")
def ApplyAwesomeSkillSaveGameData(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction) -> Block | None:
    ''' Don't enable badass rank on load and unregister non-level-specific challenges '''
    if optionLockBonusStats.value:
        obj.bAwesomeSkillDisabled = True
    # This is my last resort to prevent the pop-ups - Stops the progress update notifications but also stops customisation rewards.
    obj.ClearActivePlayerChallenges()
    return Block


@hook("WillowGame.BadassPanelGFxObject:ToggleBadassSkill")
def ToggleBadassSkill(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction) -> Block | None:
    ''' Prevent enabling BAR '''
    if optionLockBonusStats.value and obj.OwningMovie.WPCOwner.IsBadassSkillDisabled():
        obj.ParentPanel.ParentMovie.PlayUISound('ResultFailure')
        return Block
    return True


@hook("WillowGame.BadassPanelGFxObject:SetInitialButtonStates", Type.POST)
def SetInitialButtonStates(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction):
    ''' Change the title of the badass menu '''
    obj.GetObject("badassRankTitle").SetString("text", obj.BA_RankString + " [LOCKED]")


@hook("WillowGame.BadassPanelGFxObject:UpdateRedeemTokensFocusedTooltips", Type.POST)
def UpdateRedeemTokensFocusedTooltips(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction):
    ''' Change the tooltip in the badass menu '''
    if not optionLockBonusStats.value:
        return

    currentTip = str(obj.OwningMovie.GetVariableString("tooltips.tooltips.htmlText"))
    splitty = str(obj.TooltipsText_ActivateBonusStats).split("> ")
    tipCaption = splitty[-1]
    obj.OwningMovie.SetVariableString("tooltips.tooltips.htmlText", currentTip.replace(tipCaption,"<font color='#666666'>[LOCKED]</font>"));
   

build_mod()
