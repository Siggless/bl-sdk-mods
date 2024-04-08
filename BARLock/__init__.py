import unrealsdk
from typing import Any, Dict
from Mods import ModMenu, OptionManager
from Mods.ModMenu import EnabledSaveType, Game, ModTypes, Hook, SDKMod


class BARLock(SDKMod):
    Name: str = "Badass Rank Lock"
    Author: str = "Siggles"
    Description: str = "Prevents badass rank increasing, and non-level-specific challenge reward pop-ups from showing.\n\nSetting to prevent enabling badass bonus stats (in this menu)."
    Version: str = "1.0.0"
    SupportedGames: Game = Game.BL2 | Game.TPS | Game.AoDK
    Types: ModTypes = ModTypes.Utility
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu
    
    SettingsInputs: Dict[str, str] = {
        "Enter": "Enable",
        "B": "Bonus Stats: Locked"
    }
    
    def __init__(self) -> None:
        self.LockBonusStats = ModMenu.Options.Hidden(
            Caption="Lock Bonus Stats",
            Description="Whether BAR bonus stats can be enabled in the in-game menu.",
            StartingValue=True,
        )
        self.Options = [
            self.LockBonusStats,
        ]
        
    def ModOptionChanged(self, option: OptionManager.Options.Base, new_value: Any) -> None:
        if option is self.LockBonusStats:
            if new_value:
                self.SettingsInputs["B"] = "Bonus Stats: Locked"
            else:
                self.SettingsInputs["B"] = "Bonus Stats: Available"
        else:
            super.ModOptionChanged()
        return
    
    def SettingsInputPressed(self, action: str) -> None:
        if action == "Bonus Stats: Locked":
            self.ModOptionChanged(self.LockBonusStats, False)
            self.LockBonusStats.CurrentValue = False
        elif action == "Bonus Stats: Available":
            self.ModOptionChanged(self.LockBonusStats, True)
            self.LockBonusStats.CurrentValue = True
        else:
            super().SettingsInputPressed(action)


    @Hook("WillowGame.WillowPlayerController.AdjustBadassPoints")
    def AdjustBadassPoints(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        ''' Don't add ranks for challenge completion '''
        return False
    
    @Hook("WillowGame.WillowPlayerController.ApplyAwesomeSkillSaveGameData")
    def ApplyAwesomeSkillSaveGameData(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        ''' Don't enable badass rank on load and unregister non-level-specific challenges '''
        if self.LockBonusStats.CurrentValue == True:
            caller.bAwesomeSkillDisabled = True
        # This is my last resort to prevent the pop-ups - Stops the progress update notifications but also stops customisation rewards.
        caller.ClearActivePlayerChallenges()
        return False
    
    @Hook("WillowGame.BadassPanelGFxObject.ToggleBadassSkill")
    def ToggleBadassSkill(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        ''' Prevent enabling BAR '''
        if self.LockBonusStats.CurrentValue == False:
            return True
        if caller.OwningMovie.WPCOwner.IsBadassSkillDisabled():
            caller.ParentPanel.ParentMovie.PlayUISound('ResultFailure')
            return False
        return True
    
    @Hook("WillowGame.BadassPanelGFxObject.SetInitialButtonStates")
    def SetInitialButtonStates(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        ''' Change the title of the badass menu '''
        caller.GetObject("badassRankTitle").SetString("text", caller.BA_RankString + " [LOCKED]");
        return True
    
    @Hook("WillowGame.BadassPanelGFxObject.UpdateRedeemTokensFocusedTooltips")
    def UpdateRedeemTokensFocusedTooltips(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        ''' Change the tooltip in the badass menu '''
        if self.LockBonusStats.CurrentValue == False:
            return True

        unrealsdk.DoInjectedCallNext()
        caller.UpdateRedeemTokensFocusedTooltips(caller, function, params)

        currentTip = str(caller.OwningMovie.GetVariableString("tooltips.tooltips.htmlText"))
        splitty = str(caller.TooltipsText_ActivateBonusStats).split("> ")
        tipCaption = splitty[-1]
        if len(splitty) <= 2:
            # This is the original string (no UCP enabled shenanigans)
            caller.OwningMovie.SetVariableString("tooltips.tooltips.htmlText", currentTip.replace(tipCaption,"<font color='#666666'>[LOCKED]</font>"));
        # else this is not the original string (changed by UCP to add the enabled message), and setting this again causes problems, so naaah

        return False
    
### End class BARLock


instance = BARLock()
ModMenu.RegisterMod(instance)
