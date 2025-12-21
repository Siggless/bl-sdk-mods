from unrealsdk import find_enum, logging
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
from mods_base import EInputEvent, build_mod, hook
from mods_base.options import BoolOption
from typing import Any
   
_KEYS: set = ("L", "XboxTypeS_Start")   # E / X button is actually used for prestige (who new that existed?), and Right's tooltip icon is naff, so Start
ETextListMoveDir = find_enum("ETextListMoveDir")
_MOVE_DIR = ETextListMoveDir.TLMD_MAX   # Using enum MAX to flag our special move
_currentLevelName = None


@hook("WillowGame.ChallengesPanelGFxObject:PanelOnInputKey")
def PanelOnInputKey(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    """
    Handles input to the challenges menu.
    We check for our new keybind and scroll the menu if used.
    """
    if args.ukey in _KEYS and args.uevent == EInputEvent.IE_Released:
        mapName = obj.myWPC.WorldInfo.GetStreamingPersistentMapName()
        # Get the in-game LevelName for this MapName (e.g. Ice_P -> Three Horns Divide)
        global _currentLevelName
        _currentLevelName = None
        for m in obj.myWPC.GetWillowGlobals().GetLevelDependencyList().LevelList:
            if m.PersistentMap == mapName:
                #logging.info(f"[Jump To Level Challenges] Current map {mapName} has level name {m.LevelName}")
                _currentLevelName = m.LevelName
                break
        if _currentLevelName == None:
            logging.info(f"[Jump To Level Challenges] Can't find map name {_currentLevelName}")
            return Block
        
        obj.ScrollLog(_MOVE_DIR)
        obj.UpdateChallengeDescription()
        return Block
    return
    

@hook("WillowGame.GFxTextListContainer:Move")
def Move(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    """
    Called to move to a new item in a TextList.
    __args.Dir is the move type from ETextListMoveDir.
    We add in our option for moving to a certain map separator.
    """
    if not (args.Dir == _MOVE_DIR and obj.ParentMovie.Class.Name == "StatusMenuExGFxMovie"):
        return

    # Get the index of the current map name in CategoryLabelsArray
    try:
        categoryIndex = list(obj.CategoryLabelsArray).index(_currentLevelName)
    except ValueError:
        obj.ParentMovie.PlayUISound('ResultFailure')
        logging.info(f"[Jump To Level Challenges] Can't find level name {_currentLevelName} in challenge list")
        return
    
    # Loop through the TextEntries list and get the index of the item matching CategoryLabelsArray
    lastIndex = len(list(obj.TextEntries)) - 1
    newStartIndex = -1
    newEndIndex = lastIndex
    i = 0
    for entry in obj.TextEntries:
        if entry.Kind == 1:
            if entry.ArrayIdx == categoryIndex:
                # Might need to filter out undiscovered challenges too
                newStartIndex = i + 1
            elif entry.ArrayIdx == categoryIndex + 1:
                newEndIndex = i - 1
                break
        i = i + 1
    newStartIndex = min(max(newStartIndex, 0), lastIndex)   # Clamp to top and bottom of list
    newEndIndex = min(max(newEndIndex, 0), lastIndex)
    
    movingUp = newStartIndex < obj.HighlightedEntry
    obj.HighlightedEntry = newStartIndex
    obj.RepositionToFitIndex(newStartIndex - 1 if movingUp else newEndIndex)   # Make sure that we show the full category regardless of move direction
    obj.PositionHighlightBar()
    return Block
    

@hook("WillowGame.ChallengesPanelGFxObject:UpdateTooltips", Type.POST)
def UpdateTooltips(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    """
    We use this to append the tooltip for our keybind
    POST hook so after it's been updated with the actual args.
    """
    tooltipString = obj.OwningMovie.GetVariableString("tooltips.tooltips.htmlText")
    if obj.MyWPC.PlayerInput.bUsingGamepad:
        tooltipString = tooltipString + f"    <StringAliasMap:{_KEYS[1]}> Current Level"
    else:
        tooltipString = tooltipString + f"    [{_KEYS[0]}] Current Level"  
    obj.OwningMovie.SetVariableString("tooltips.tooltips.htmlText", obj.Outer.ResolveDataStoreMarkup(tooltipString))
    
    return



@BoolOption("Hide Completed Challenges", False, description="Whether completed challenges are hidden in the challenges list.")
def RemoveOption(option, newValue):
    if newValue:
        UpdateListOfChallenges.enable()
    else:
        UpdateListOfChallenges.disable()


#@hook("WillowGame.ChallengesPanelGFxObject:UpdateListOfChallenges", Type.POST)
@hook("WillowGame.ChallengesPanelGFxObject:UpdateChallengeTextList", Type.PRE)
def UpdateListOfChallenges(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    """
    The hooked function is only called after the list has its entries added. Remove any completed challenges.
    """
    textList = obj.ChallengeLogTextList
    for x in reversed(textList.OneTimeArray):
        challengeDef = x.Data
        _ = 0
        ret = obj.MyWPC.GetChallengeCurrentLevelProgress(challengeDef, _, _, _)
        if ret[0]:
            textList.RemoveObject(x.Data)


build_mod(hooks=[PanelOnInputKey, Move, UpdateTooltips])
