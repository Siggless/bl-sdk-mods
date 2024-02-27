import unrealsdk
from Mods import ModMenu
from Mods.ModMenu import EnabledSaveType, ModTypes, Hook, Game, InputEvent
try:
    from Mods.Enums import ETextListMoveDir
except ImportError:
    import webbrowser
    webbrowser.open("https://bl-sdk.github.io/requirements/?mod=JumpToLevelChallenges&all")
    raise ImportError("JumpToLevelChallenges requires at least Enums version 1.0")
   

class JumpToLevelChallenges(ModMenu.SDKMod):
    Name: str = "Jump To Level Challenges"
    Author: str = "Siggles"
    Description: str = "Adds a keybind to the Challenges menu to jump to the current level's challenges."
    Version: str = "1.0.0"
    SupportedGames: Game = Game.BL2 | Game.TPS | Game.AoDK
    Types: ModTypes = ModTypes.Utility  # One of Utility, Content, Gameplay, Library; bitwise OR'd together
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu

    keys = ("E", "XboxTypeS_Start")     # X button is actually used for prestige (who new that existed?), and Right's tooltip icon is naff, so Start
    moveDir = ETextListMoveDir.TLMD_MAX # Using enum MAX to flag our special move
    currentLevelName = None


    @Hook("WillowGame.ChallengesPanelGFxObject.PanelOnInputKey")
    def PanelOnInputKey(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        Handles input to the challenges menu.
        We check for our new keybind and scroll the menu if used.
        """
        if params.ukey in self.keys and params.uevent==InputEvent.Released:
            mapName = caller.myWPC.WorldInfo.GetStreamingPersistentMapName()
            # Get the in-game LevelName for this MapName (e.g. Ice_P -> Three Horns Divide)
            self.currentLevelName=None
            for m in caller.myWPC.GetWillowGlobals().GetLevelDependencyList().LevelList:
                if m.PersistentMap == mapName:
                    #unrealsdk.Log(f"[{self.Name}] Current map {mapName} has level name {m.LevelName}")
                    self.currentLevelName = m.LevelName
                    break
            if self.currentLevelName == None:
                unrealsdk.Log(f"[{self.Name}] Can't find map name {self.currentLevelName}")
                return False
            
            caller.ScrollLog(self.moveDir)
            caller.UpdateChallengeDescription()
            return False
        return True
        

    @Hook("WillowGame.GFxTextListContainer.Move")
    def Move(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        Called to move to a new item in a TextList.
        params.Dir is the move type from ETextListMoveDir.
        We add in our option for moving to a certain map separator.
        """
        if params.Dir == self.moveDir and caller.ParentMovie.Name == "StatusMenuExGFxMovie":
            
            # Get the index of the current map name in CategoryLabelsArray
            try:
                categoryIndex = list(caller.CategoryLabelsArray).index(self.currentLevelName)
            except ValueError:
                caller.ParentMovie.PlayUISound('ResultFailure')
                unrealsdk.Log(f"[{self.Name}] Can't find level name {self.currentLevelName} in challenge list")
                return
            
            # Loop through the TextEntries list and get the index of the item matching CategoryLabelsArray
            lastIndex = len(list(caller.TextEntries))-1
            newStartIndex = -1
            newEndIndex = lastIndex
            i=0
            for entry in caller.TextEntries:
                if entry.Kind == 1:
                    if entry.ArrayIdx == categoryIndex:
                        # Might need to filter out undiscovered challenges too
                        newStartIndex = i + 1
                    elif entry.ArrayIdx == categoryIndex + 1:
                        newEndIndex = i - 1
                        break
                i = i+1
            newStartIndex = min(max(newStartIndex, 0),lastIndex) # Clamp to top and bottom of list
            newEndIndex = min(max(newEndIndex, 0),lastIndex)
            
            movingUp = newStartIndex<caller.HighlightedEntry
            caller.HighlightedEntry = newStartIndex
            caller.RepositionToFitIndex(newStartIndex - 1 if movingUp else newEndIndex)   # Make sure that we show the full category regardless of move direction
            caller.PositionHighlightBar()
            return False
        
        return True
    

    @Hook("WillowGame.ChallengesPanelGFxObject.UpdateTooltips")
    def UpdateTooltips(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        We use this to append the tooltip for our keybind
        """
        # Do the hooked function first to get the new tooltip
        unrealsdk.DoInjectedCallNext()
        caller.UpdateTooltips(caller, function, params)
        
        # Now append our button string
        tooltipString = caller.OwningMovie.GetVariableString("tooltips.tooltips.htmlText")
        if caller.MyWPC.PlayerInput.bUsingGamepad:
            tooltipString = tooltipString + f"    <StringAliasMap:{self.keys[1]}> Current Map"
        else:
            tooltipString = tooltipString + f"    [{self.keys[0]}] Current Map"  
        caller.OwningMovie.SetVariableString("tooltips.tooltips.htmlText", caller.Outer.ResolveDataStoreMarkup(tooltipString))
        
        return False

### End class JumpToLevelChallenges


instance = JumpToLevelChallenges()

ModMenu.RegisterMod(instance)
