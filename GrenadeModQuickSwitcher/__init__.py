from mods_base import EInputEvent, build_mod, get_pc, keybind

@keybind("Switch Grenade Mod")
def SwitchGrenadeMod():
    PC = get_pc()
    InvManager = PC.GetPawnInventoryManager()
    
    # Since the readied item gets added to the end of the backpack list,
    # the backpack acts as a queue, so we don't have to mess with cycling order. Yay!
    for inv in InvManager.Backpack:
        if inv is not None:
            if not inv.bReadied and inv.GetCategoryKey() == "mod" and inv.Mark == 2:
                InvManager.ReadyBackpackInventory(inv)
                PC.PlaySpecialHUDSound('RewardToken')
                break

    return

build_mod()
