import unrealsdk
from Mods import ModMenu
from Mods.ModMenu import EnabledSaveType, ModTypes, Hook
   
class LessDOTScreams(ModMenu.SDKMod):
    Name: str = "Less DOT Screams"
    Author: str = "Siggles"
    Description: str = "Player DOT (status effect) screams don't play unless shield is broken."\
                        "\n\nTo fully disable for certain characters, use <font color='#00ffe8'>Customizable Player Audio Muter</font> BLCMM text mod instead."
    Version: str = "1.0.0"
    SupportedGames: ModMenu.Game = ModMenu.Game.BL2 | ModMenu.Game.TPS | ModMenu.Game.AoDK
    Types: ModTypes = ModTypes.Gameplay  # One of Utility, Content, Gameplay, Library; bitwise OR'd together
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu

    @Hook("GearboxFramework.Behavior_TriggerDialogEvent.TriggerDialogEvent")
    def TriggerDialogEvent(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        Fires when a TriggerDialogEvent is applied
        In particular, we want to check StatusEffectDefinition's OnApplication Behavior_TriggerDialogEvent
        """
        # Don't preventing slag (Status_Amp) and healing effects
        if caller.Outer.Class.Name == "StatusEffectDefinition" and caller.Outer.Name != "Status_Amp" and caller.Outer.Name != "Status_Healing":
            # Only affect PC dialog
            if params.ContextObject.Class.Name == "WillowPlayerPawn":
                pawn = params.ContextObject
                # Only return true to play the VO if the shield is empty
                return pawn.ShieldArmor == None or pawn.ShieldArmor.Data.GetCurrentValue() <= 0
        return True

    #@ModMenu.Hook("WillowGame.WillowPawn:OnShieldDepleted") # Doesn't fire?
    @Hook("WillowGame.StatusEffectsComponent.StartEffectSound")
    def StartEffectSound(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        Triggers repeatedly whilst a status effect is active on a Pawn
        We use this to start the status effect VO when the player's shield breaks, if one is still active
        """
        if caller.Owner.Class.Name == "WillowPlayerPawn":
            pawn = caller.Owner
            # Check if this is the current PC 
            if pawn.Controller == unrealsdk.GetEngine().GamePlayers[0].Actor:
                # Check if the shield is depleted - OnShieldDeplete doesn't fire for some reason? Maybe only for AIs?
                if pawn.ShieldArmor == None or pawn.ShieldArmor.Data.GetCurrentValue() <= 0:
                    
                    statusDefinition = caller.GetMostRecentStatusEffect()
                    if statusDefinition != None and statusDefinition.Name != "Status_Amp" and statusDefinition.Name != "Status_Healing":
                        # Play the status effect VO
                        dialogBehavior = statusDefinition.OnApplication[1]  # Assuming that the Behavior_TriggerDialogEvent is always this index
                        if dialogBehavior != None and dialogBehavior.Class.Name == "Behavior_TriggerDialogEvent":
                            dialogBehavior.TriggerDialogEvent(pawn,pawn,None,None,())
        return True
    
### End class NoDOTScreams


instance = LessDOTScreams()
#This section let's us reload the mod in-game using `pyexec LessDOTScreams/__init__.py`
if __name__ == "__main__":
    unrealsdk.Log(f"[{instance.Name}] Manually loaded")
    for mod in ModMenu.Mods:
        if mod.Name == instance.Name:
            if mod.IsEnabled:
                mod.Disable()
            ModMenu.Mods.remove(mod)
            unrealsdk.Log(f"[{instance.Name}] Removed last instance")

            # Fixes inspect.getfile()
            instance.__class__.__module__ = mod.__class__.__module__
            break
ModMenu.RegisterMod(instance)
