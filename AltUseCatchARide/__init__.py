from __future__ import annotations
from unrealsdk import construct_object, find_class, find_enum, find_object, logging
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import notify_changes, BoundFunction, UObject, WeakPointer, WrappedStruct
from mods_base import build_mod, get_pc, hook, Game
from mods_base.options import BoolOption, NestedOption, SpinnerOption
from typing import Any, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
WillowPlayerController: TypeAlias = UObject
InteractionIconDefinition: TypeAlias = UObject
VehicleFamilyDefinition: TypeAlias = UObject
VSSUIDefinition: TypeAlias = UObject

VehicleSpawnStationTerminal = find_class("VehicleSpawnStationTerminal")

EInteractionIcons = find_enum("EInteractionIcons")
ENetRole = find_enum("ENetRole")
EUsabilityType = find_enum("EUsabilityType")

# Dict[str, (VehicleFamilyDefinition, str, Dict[str, VSSUIDefinition])]
FAMILY_DICT: Dict[str, Tuple[str, str, Dict[str, str]]] = {
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
}[Game.get_current()]

DEFAULTS_DICT: Dict[str, str] = {
    "Game.BL2": "Runner",
    "Game.TPS": "Moon Buggy",
    # DLC codes override the game defaults
    "Orchid": "Sandskiff",
    "Sage": "Fanboat",
}


optBoolAutoTeleport = BoolOption(
    "Auto Teleport",
    False,
    "Yes", "No",
    description="If YES, teleports you to the driver seat on spawn."
)

familyChoices = list(FAMILY_DICT.keys())
familyChoices.append("Default")
optSpinnerVehicleFamily = SpinnerOption(
    "Vehicle Family",
    "Default",
    familyChoices,
    description="The family of vehicle to spawn. Default is the last chosen vehicle."
)

familyLoadoutDict: Dict[str, SpinnerOption] = {}
for family in FAMILY_DICT:
    familyTypes = list(FAMILY_DICT[family][2].keys())
    spinner = SpinnerOption(
        f"{family} Type",
        familyTypes[0],
        familyTypes,
        description=f"The type of {family} to spawn."
    )
    familyLoadoutDict[family] = spinner

optNestedVehicleTypes = NestedOption(
    "Vehicle Types",
    list(familyLoadoutDict.values()),
    description="Options menu for which type of vehicle is spawned, for each vehicle family."
)

optionsTopLevel = [
    optBoolAutoTeleport,
    optSpinnerVehicleFamily,
    optNestedVehicleTypes
]


# This is all based on Alt Use Vendors mod, check that out
MAX_SLOTS: int = 2  # Stringray has 4 but whatevs
customIcon: WeakPointer = WeakPointer(None)

def CreateIcon() -> None:
    """
    Creates the icon objects we're using, if it doesn't already exist.
    """
    global customIcon
    if customIcon():
        return
    
    baseIcon = find_object("InteractionIconDefinition", "GD_InteractionIcons.Default.Icon_DefaultUse")
    icon = construct_object(
        baseIcon.Class,
        baseIcon.Outer,
        "Mod_Icon_Driver",
        baseIcon.ObjectFlags | 0x4000,  # KeepAlive
    )

    icon.Icon = EInteractionIcons.INTERACTION_ICON_Driver
    with notify_changes():
        icon.Action = "UseSecondary"
        icon.Text = "QUICK DEPLOY"
    customIcon = WeakPointer(icon)


@hook("WillowGame.WillowInteractiveObject:InitializeFromDefinition")
def InitializeFromDefinition(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    """
    Called when any interactive object is created. Use it to enable alt use and add the icons.
    """
    if obj.Class is not VehicleSpawnStationTerminal:
        return

    args.Definition.HUDIconDefSecondary = customIcon()
    obj.SetUsability(True, EUsabilityType.UT_Secondary)


@hook("WillowGame.WillowPlayerController:PerformedSecondaryUseAction")
def PerformedSecondaryUseAction(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    """
    Called whenever someone secondary uses an interactive object.
    """
    if obj.Role < ENetRole.ROLE_Authority:
        return
    if obj.CurrentUsableObject is None:
        return
    if obj.CurrentInteractionIcon[1].IconDef is None:
        return

    vss = obj.CurrentUsableObject
    if vss.Class is not VehicleSpawnStationTerminal:
        return
    if not vss.ActivatedForPlayerUse():
        return

    # Choose a free vehicle slot
    slot = GetAvailableVehicleSlot(obj)
    # If both vehicles are deployed and occupied, then we can't redeploy either
    if slot >= MAX_SLOTS:
        obj.NotifyUnableToAffordUsableObject(EUsabilityType.UT_Secondary)
        return Block

    vss.LockOutOtherUsers(obj.Pawn)  # I haven't tested coop at all, but am locking during this secondary use function as a precaution
    obj.StartUsingVehicleSpawnStationTerminal(vss)

    # Get the vehicle family
    familyDef = GetVehicleFamily(obj)
    obj.RouteCallToSetVehicleFamily(familyDef)   # Update the family stored in the game, as we aren't going through the UI.
    
    # Get the vehicle loadout
    vuiDef: VSSUIDefinition | None = GetVehicleLoadout(familyDef)
    if vuiDef is None:
        logging.dev_warning("[Alt Use Catch-a-Ride] No loadout for vehicle family " + str(familyDef.Name))
        obj.StopUsingVehicleSpawnStationTerminal()
        return Block

    # Get the customisation for the given slot
    customizationDef = obj.GetVehicleCustomizationForModule(familyDef, slot)
    
    # Need to handle despawning existing vehicles too
    obj.DespawnVehicleFromConnectedVehicleSpawnStationTerminal(slot, vuiDef)
    obj.SpawnVehicleFromConnectedVehicleSpawnStationTerminal(slot, vuiDef, customizationDef)

    # Optional teleport to this vehicle
    if optBoolAutoTeleport.value:
        #obj.ServerTryToTeleportToVehicle(slot)
        # Dunno why Gearbox use a delay but best be safe an do the same
        obj.VSSSlotIndexForDelayedTeleport = slot
        obj.TheVSSUIMovie = None
        #obj.SetTimer(0.25, False, 'DelayedTeleportToVehicle')   # Doesn't work
        obj.DelayedTeleportToVehicle()
        
    obj.StopUsingVehicleSpawnStationTerminal()
    
    return Block


def GetAvailableVehicleSlot(PC: WillowPlayerController) -> int:
    """
    Returns the first un-deployed vehicle slot.
    Or if there is none, then the slot of the first unoccupied vehicle.
    Or if there is neither, then the MAX_SLOTS.
    """
    popMaster = PC.GetWillowGlobals().GetPopulationMaster()
    # If a slot is not deployed then use that
    for s in range(MAX_SLOTS):
        vehicleFromSlot = popMaster.GetVehicleFromVehicleSpawnStation(s)
        if vehicleFromSlot is None:
            return s
        
    # If all vehicles are deployed then we look for the first unoccupied vehicle to redeploy
    for s in range(MAX_SLOTS):
        vehicleFromSlot = popMaster.GetVehicleFromVehicleSpawnStation(s)
        if not vehicleFromSlot.Occupied():
            return s
        
    # Flag as MAX for no slot found
    return MAX_SLOTS


def GetVehicleFamily(PC: WillowPlayerController) -> VehicleFamilyDefinition:
    """
    Returns the VehicleFamilyDefition set in the mod options.
    Or if "Default" is set, then the current family given by the game.
    Or if no family has been chosen in-game yet, then a default family for the current DLC.
    """
    familyDef: VehicleFamilyDefinition
    family: str = optSpinnerVehicleFamily.value
    if family == "Default" or family not in FAMILY_DICT:
        # Default to the family given by the game
        familyDef = PC.GetWillowGlobals().GetVehicleLifetimeManager().CurrentVehicleFamily
    else:
        familyDef = find_object("VehicleFamilyDefinition", FAMILY_DICT[family][0])
        
    if familyDef is None:
        # No vehicle family has been chosen yet in-game, so we need to set a default
        chosenDefaultFamily: str = DEFAULTS_DICT[str(Game.get_current())]
        # If this is a DLC level then replace with default DLC family
        for i in DEFAULTS_DICT:
            if i in str(PC.CurrentUsableObject.Outer):
                chosenDefaultFamily = DEFAULTS_DICT[i]
                break
        logging.dev_warning(f"[Alt Use Catch-a-Ride] Vehicle family {str(familyDef)} not found! Defaulting to {chosenDefaultFamily}.")
        familyDef = find_object("VehicleFamilyDefinition", FAMILY_DICT[chosenDefaultFamily][0])
        
    return familyDef


def GetVehicleLoadout(familyDef: VehicleFamilyDefinition) -> VSSUIDefinition | None:
    """
    Returns the VSSUIDefinition set in the mod options for the given family.
    This must be defined in the mod options, since I can't easily get the GfxMovie from the InteractiveObject,
        to get the VSSUIDefinition from the ChoiceModule in that, if the family matches.
    """
    for family in FAMILY_DICT:
        if FAMILY_DICT[family][1] == familyDef.Name:
            familyTypes = FAMILY_DICT[family][2]
            familySpinner = familyLoadoutDict[family]
            if familySpinner.value in familyTypes:
                return find_object("VSSUIDefinition", familyTypes[familySpinner.value])
    logging.info("[Alt Use Catch-a-Ride] No mod options spinner found for vehicle family " + str(familyDef.Name))
   

build_mod(options=optionsTopLevel, on_enable=CreateIcon)
