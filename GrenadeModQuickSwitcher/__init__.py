import unrealsdk
from Mods.ModMenu import EnabledSaveType, Game, ModTypes, SDKMod, RegisterMod, Keybind


class GrenadeModQuickSwitcher(SDKMod):
    Name: str = "Grenade Mod Quick Switcher"
    Author: str = "Siggles"
    Description: str = "Adds a keybind that cycles through grenade mods marked as favourite.\n" \
        "Cycles in the order that items were added to the backpack, or unequipped."
    Version: str = "1.0.0"
    SupportedGames: Game = Game.BL2 | Game.TPS | Game.AoDK
    Types: ModTypes = ModTypes.Utility
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu
    

    def SwitchGrenade():
        """ Called from modded keybind """
        PC = unrealsdk.GetEngine().GamePlayers[0].Actor
        InvManager = PC.GetPawnInventoryManager()
        
        # Since the readied item gets added to the end of the backpack list, the backpack acts as a queue, so we don't have to mess with cycling order. Yay!
        for inv in InvManager.Backpack:
            if inv is not None:
                if not inv.bReadied and inv.GetCategoryKey()=="mod" and inv.Mark == 2:
                    InvManager.ReadyBackpackInventory(inv)
                    PC.PlaySpecialHUDSound('RewardToken')
                    break

        return
    
    Keybinds = [Keybind("Switch Grenade Mod", "V", OnPress=SwitchGrenade)]    

### End class GrenadeModQuickSwitcher


instance = GrenadeModQuickSwitcher()
RegisterMod(instance)
