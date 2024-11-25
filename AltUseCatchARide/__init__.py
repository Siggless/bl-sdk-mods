from __future__ import annotations

import unrealsdk

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

WillowPlayerController: TypeAlias = unrealsdk.UObject
InteractionIconDefinition: TypeAlias = unrealsdk.UObject
VehicleSpawnStationTerminal: TypeAlias = unrealsdk.UObject
VehicleFamilyDefinition: TypeAlias = unrealsdk.UObject
VSSUIDefinition: TypeAlias = unrealsdk.UObject

from Mods.ModMenu import (EnabledSaveType, Game, Hook, Mods, ModTypes, Options, RegisterMod, SDKMod)

try:
    from Mods.Enums import (EInteractionIcons, ENetRole, EUsabilityType, EVehicleSpawnStationSlot)
except ImportError:
    raise ImportError("Alt Use Catch-a-Ride requires at least Enums version 1.0")


FAMILY_DICT: Dict[str, (VehicleFamilyDefinition, str, Dict[str, VSSUIDefinition])] = {
    Game.BL2: {
        "Technical": ("GD_Globals.VehicleSpawnStation.VehicleFamily_BanditTechnical","VehicleFamily_BanditTechnical",{
            "Saw Blade": "GD_Globals.VehicleSpawnStation.VSSUI_SawBladeTechnical",
            "Catapult": "GD_Globals.VehicleSpawnStation.VSSUI_CatapultTechnical"
        }),
        "Runner": ("GD_Globals.VehicleSpawnStation.VehicleFamily_Runner","VehicleFamily_Runner",{
            "Machine Gun": "GD_Globals.VehicleSpawnStation.VSSUI_MGRunner",
            "Rocket Launcher": "GD_Globals.VehicleSpawnStation.VSSUI_RocketRunner"
        }),
        "Sandskiff": ("GD_OrchidPackageDef.Vehicles.VehicleFamily_Hovercraft","VehicleFamily_Hovercraft",{
            "Harpoon": "GD_OrchidPackageDef.Vehicles.VSSUI_HarpoonHovercraft",
            "Rocket Launcher": "GD_OrchidPackageDef.Vehicles.VSSUI_RocketHovercraft",
            "Saw Blade": "GD_OrchidPackageDef.Vehicles.VSSUI_SawBladeHovercraft"
        }),
        "Fanboat": ("GD_SagePackageDef.Vehicles.VehicleFamily_FanBoat","VehicleFamily_FanBoat",{
            "Corrosive": "GD_SagePackageDef.Vehicles.VSSUI_CorrosiveFanBoat",
            "Incendiary": "GD_SagePackageDef.Vehicles.VSSUI_IncendiaryFanBoat",
            "Shock": "GD_SagePackageDef.Vehicles.VSSUI_ShockFanBoat"
        }),
    },
    Game.TPS: {
        "Moon Buggy": ("GD_Globals.VehicleSpawnStation.VehicleFamily_MoonBuggy","VehicleFamily_MoonBuggy",{
            "Laser": "GD_Globals.VehicleSpawnStation.VSSUI_LaserBuggy",
            "Missile": "GD_Globals.VehicleSpawnStation.VSSUI_MissileBuggy"
        }),
        "Stingray": ("GD_Globals.VehicleSpawnStation.VehicleFamily_StingRay","VehicleFamily_StingRay",{
            "Cryo": "GD_Globals.VehicleSpawnStation.VSSUI_StingRay_CryoRocket",
            "Flak": "GD_Globals.VehicleSpawnStation.VSSUI_StingRay_FlakBurst"
        }),
    }
}[Game.GetCurrent()]
DEFAULTS_DICT = {
    "Game.BL2": "Runner",
    "Game.TPS": "Moon Buggy",
    # DLC codes override the game defaults
    "Orchid": "Sandskiff",
    "Sage": "Fanboat",
}


class AltUseCatchARide(SDKMod):
    Name: str = "Alt Use Catch-a-Ride"
    Author: str = "Siggles" # But based on Alt Use Vendors mod, check that out
    Description: str = (
        "Adds alt use binds to Catch-a-Ride stations, to instantly deploy a vehicle.\n\n"
        "Options to teleport to vehicle on spawn, choose a vehicle family (including DLC vehicles), and choose the vehicle weapon to use for each family."
    )
    Version: str = "1.1.0"

    Types: ModTypes = ModTypes.Utility
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadWithSettings
    SupportedGames: Game = Game.BL2 | Game.TPS  # NOT AoDK

    customIcon: InteractionIconDefinition
    MAX_SLOTS: int = 2  # Stringray has 4 but whatevs

    def __init__(self) -> None:
        super().__init__()
        
        self.BoolAutoTeleport = Options.Boolean(
            Caption="Auto Teleport",
            Description="If YES, teleports you to the driver seat on spawn.",
            StartingValue=False,
            Choices=["No", "Yes"]  # False, True
        )
        
        familyChoices = list(FAMILY_DICT.keys())
        familyChoices.append("Default")
        self.SpinnerVehicleFamily = Options.Spinner(
            Caption="Vehicle Family",
            Description="The family of vehicle to spawn. Default is the last chosen vehicle.",
            StartingValue="Default",
            Choices=familyChoices
        )
        
        self.familyLoadoutDict: Dict[str, Options.Nested] = {}
        for family in FAMILY_DICT:
            familyTypes = list(FAMILY_DICT[family][2].keys())
            spinner = Options.Spinner(
                Caption=f"{family} Type",
                Description=f"The type of {family} to spawn.",
                StartingValue=familyTypes[0],
                Choices=familyTypes
            )
            self.familyLoadoutDict[family] = spinner

        self.NestedVehicleTypes = Options.Nested(
            Caption="Vehicle Types",
            Description="Options menu for which type of vehicle is spawned, for each vehicle family.",
            Children=list(self.familyLoadoutDict.values()),
            IsHidden=False
        )
        
        self.Options = [
            self.BoolAutoTeleport,
            self.SpinnerVehicleFamily,
            self.NestedVehicleTypes
        ]

    def Enable(self) -> None:
        super().Enable()
        #unrealsdk.GetEngine().GamePlayers[0].Actor.StopUsingVehicleSpawnStationTerminal()
        self.CreateIcon()

    def CreateIcon(self) -> None:
        """
        Creates the icon objects we're using.

        If an object of the same name already exists, uses that instead.
        """

        baseIcon = unrealsdk.FindObject("InteractionIconDefinition", "GD_InteractionIcons.Default.Icon_DefaultUse")
        customIconName = "Mod_Icon_Driver"
        # Check if the icon already exists (mod re-enabled) and don't recreate if so
        icon = unrealsdk.FindObject("InteractionIconDefinition", f"GD_InteractionIcons.Default.{customIconName}")
        if icon is None:
            icon = unrealsdk.ConstructObject(
                Class=baseIcon.Class,
                Outer=baseIcon.Outer,
                Name=customIconName,
                Template=baseIcon,
            )
            unrealsdk.KeepAlive(icon)

            icon.Icon = EInteractionIcons.INTERACTION_ICON_Driver
            # Setting values directly on the object causes a crash on quitting the game
            # Everything still works fine, not super necessary to fix, but people get paranoid
            # https://github.com/bl-sdk/PythonSDK/issues/45
            PC = unrealsdk.GetEngine().GamePlayers[0].Actor
            PC.ServerRCon(f"set {PC.PathName(icon)} Action UseSecondary")
            PC.ServerRCon(f"set {PC.PathName(icon)} Text QUICK DEPLOY")

        self.customIcon = icon

    @Hook("WillowGame.WillowInteractiveObject.InitializeFromDefinition")
    def InitializeFromDefinition(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        Called when any interactive object is created. Use it to enable alt use and add the icons.
        """
        if caller.Class.Name != "VehicleSpawnStationTerminal":
            return True

        params.Definition.HUDIconDefSecondary = self.customIcon
        caller.SetUsability(True, EUsabilityType.UT_Secondary)

        return True

    @Hook("WillowGame.WillowPlayerController.PerformedSecondaryUseAction")
    def PerformedSecondaryUseAction(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        Called whenever someone secondary uses an interactive object.
        """
        if caller.Role < ENetRole.ROLE_Authority:
            return True
        if caller.CurrentUsableObject is None:
            return True
        if caller.CurrentInteractionIcon[1].IconDef is None:
            return True

        vss = caller.CurrentUsableObject.ObjectPointer
        if vss.Class.Name != "VehicleSpawnStationTerminal":
            return True
        if not vss.ActivatedForPlayerUse():
            return True

        # Choose a free vehicle slot
        slot = self.GetAvailableVehicleSlot(caller)
        # If both vehicles are deployed and occupied, then we can't redeploy either
        if slot >= self.MAX_SLOTS:
            caller.NotifyUnableToAffordUsableObject(EUsabilityType.UT_Secondary)
            return False

        vss.LockOutOtherUsers(caller.Pawn)  # I haven't tested multiplayer at all, but am locking during this secondary use function as a precaution
        caller.StartUsingVehicleSpawnStationTerminal(vss)

        # Get the vehicle family
        familyDef = self.GetVehicleFamily(caller)
        caller.RouteCallToSetVehicleFamily(familyDef)   # Update the family stored in the game, as we aren't going through the UI.
        
        # Get the vehicle loadout
        vuiDef:VSSUIDefinition = self.GetVehicleLoadout(familyDef)
        if vuiDef is None:
            unrealsdk.Log("["+self.Name+"] No loadout for vehicle family " + str(familyDef.Name))
            caller.StopUsingVehicleSpawnStationTerminal()
            return False

        # Get the customisation for the given slot
        customizationDef = caller.GetVehicleCustomizationForModule(familyDef, slot)
        
        # Need to handle despawning existing vehicles too
        caller.DespawnVehicleFromConnectedVehicleSpawnStationTerminal(slot, vuiDef)
        caller.SpawnVehicleFromConnectedVehicleSpawnStationTerminal(slot, vuiDef, customizationDef)

        # Optional teleport to this vehicle
        if self.BoolAutoTeleport.CurrentValue:
            #caller.ServerTryToTeleportToVehicle(slot)
            # Dunno why they use a delay but best be safe an do the same
            caller.VSSSlotIndexForDelayedTeleport = slot
            caller.TheVSSUIMovie = None
            #caller.SetTimer(0.25, False, 'DelayedTeleportToVehicle')   # Doesn't work
            caller.DelayedTeleportToVehicle()
            
        caller.StopUsingVehicleSpawnStationTerminal()
        
        return False
    
    def GetAvailableVehicleSlot(self, PC: WillowPlayerController) -> int:
        """
        Returns the first un-deployed vehicle slot.
        Or if there is none, then the slot of the first unoccupied vehicle.
        Or if there is neither, then the MAX_SLOTS.
        """
        popMaster = PC.GetWillowGlobals().GetPopulationMaster()
        # If a slot is not deployed then use that
        for s in range(self.MAX_SLOTS):
            vehicleFromSlot = popMaster.GetVehicleFromVehicleSpawnStation(s)
            if vehicleFromSlot is None:
                return s
            
        # If all vehicles are deployed then we look for the first unoccupied vehicle to redeploy
        for s in range(self.MAX_SLOTS):
            vehicleFromSlot = popMaster.GetVehicleFromVehicleSpawnStation(s)
            if not vehicleFromSlot.Occupied():
                return s
            
        # Flag as MAX for no slot found
        return self.MAX_SLOTS
    
    def GetVehicleFamily(self, PC: WillowPlayerController) -> VehicleFamilyDefinition:
        """
        Returns the VehicleFamilyDefition set in the mod options.
        Or if "Default" is set, then the current family given by the game.
        Or if no family has been chosen in-game yet, then a default family for the current DLC.
        """
        familyDef:VehicleFamilyDefinition
        if self.SpinnerVehicleFamily.CurrentValue == "Default" or self.SpinnerVehicleFamily.CurrentValue not in FAMILY_DICT:
            # Default to the family given by the game
            familyDef = PC.GetWillowGlobals().GetVehicleLifetimeManager().CurrentVehicleFamily
        else:
            familyDef = unrealsdk.FindObject("VehicleFamilyDefinition", FAMILY_DICT[self.SpinnerVehicleFamily.CurrentValue][0])
            
        if familyDef is None:
            # No vehicle family has been chosen yet in-game, so we need to set a default
            chosenDefaultFamily:str=DEFAULTS_DICT[str(Game.GetCurrent())]
            # If this is a DLC level then replace with default DLC family
            for i in DEFAULTS_DICT:
                if i in str(PC.CurrentUsableObject.ObjectPointer.Outer):
                    chosenDefaultFamily = DEFAULTS_DICT[i]
                    break
            #unrealsdk.Log(f"[{self.Name}] Vehicle family {str(familyDef)} not found! Defaulting to {chosenDefaultFamily}.")
            familyDef = unrealsdk.FindObject("VehicleFamilyDefinition", FAMILY_DICT[chosenDefaultFamily][0])
            
        return familyDef
    
    def GetVehicleLoadout(self, familyDef: VehicleFamilyDefinition) -> VSSUIDefinition:
        """
        Returns the VSSUIDefinition set in the mod options for the given family.
        This must be defined in the mod options, since I can't easily get the GfxMovie from the InteractiveObject,
         to get the VSSUIDefinition from the ChoiceModule in that, if the family matches.
        """
        for family in FAMILY_DICT:
            if FAMILY_DICT[family][1] == familyDef.Name:
                familyTypes = FAMILY_DICT[family][2]
                familySpinner = self.familyLoadoutDict[family]
                if familySpinner.CurrentValue in familyTypes:
                    return unrealsdk.FindObject("VSSUIDefinition", familyTypes[familySpinner.CurrentValue])
            
        unrealsdk.Log("["+self.Name+"] No mod options spinner found for vehicle family " + str(familyDef.Name))
        return None

# END CLASS AltUseCatchARide


instance = AltUseCatchARide()
if __name__ == "__main__":
    unrealsdk.Log(f"[{instance.Name}] Manually loaded")
    for mod in Mods:
        if mod.Name == instance.Name:
            if mod.IsEnabled:
                mod.Disable()
            Mods.remove(mod)
            unrealsdk.Log(f"[{instance.Name}] Removed last instance")

            # Fixes inspect.getfile()
            instance.__class__.__module__ = mod.__class__.__module__
            break
RegisterMod(instance)
