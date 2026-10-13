try:
    assert __import__("package_loader").__version_info__ >= (1, 0), "The package_loader mod is required."
    assert __import__("ue_timers").__version_info__ >= (1, 0), "The ue_timers mod is required."
except (AssertionError, ImportError) as ex:
    import webbrowser
    webbrowser.open(f"https://bl-sdk.github.io/willow2-mod-db/requirements?mod={__name__}")
    raise ex

import enum, math, random

from ue_timers import UnrealTimer
from ui_utils import show_second_wind_notification, TrainingBox
from unrealsdk import find_all
from unrealsdk.hooks import Type, Block
from unrealsdk.logging import dev_warning, info, misc
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
from mods_base import build_mod, get_pc, hook, keybind, ENGINE, Game, EInputEvent
from mods_base import BaseOption, BoolOption, NestedOption, SliderOption, SpinnerOption

from typing import Any, Dict, List, Tuple
PopulationFactoryBalancedAIPawn = PopulationOpportunityDen = WillowPopulationPoint = WillowPlayerController = UObject
SpawnItem = Tuple[PopulationFactoryBalancedAIPawn, WillowPopulationPoint, float] # Factory, Point, Delay

from .custom_spawns import CacheMegaMixPools, CustomSpawnFromPopDef, Tag, Spawn, CustomSpawn
from .level_packages import GetCurrentDLC, LoadLevelSpawnObjects, UnloadLevelSpawnObjects, DLC, combat_packages_by_DLC, loaded_DLCs
from .spawner import GetGameStage, Spawner

if Game.get_current() == Game.TPS:
    from .TPS.blacklists import BLACKLIST_ALLEGIANCES, BLACKLIST_MAPS, BLACKLIST_GAME_STAGES, BLACKLIST_POPDEFS, POPDEF_PREFIX_EXCLUDED_FROM_FOV_CHECKS
    from .TPS.customs import CUSTOM_SPAWNS
else:
    from .BL2.blacklists import BLACKLIST_ALLEGIANCES, BLACKLIST_MAPS, BLACKLIST_GAME_STAGES, BLACKLIST_POPDEFS, POPDEF_PREFIX_EXCLUDED_FROM_FOV_CHECKS
    from .BL2.customs import  CUSTOM_SPAWNS


import package_loader
package_loads = []
def on_load_packages(package_loads):
    for package_load in package_loads:
        dlcs = [key for key,val in combat_packages_by_DLC.items() if any(package in package_load for package in val)]
        dlc = level_packages.BaseDLC if not dlcs else dlcs[0]
        LoadLevelSpawnObjects(package_load, dlc)
        yield
    CacheMegaMixPools()


class SpawnPool(enum.IntEnum):
    DEN = enum.auto()
    LEVEL = enum.auto()
    DLC = enum.auto()
    GAME = enum.auto()


class DenSpawnInfo:
    """Stores the info and spawns that we use from a den"""
    def __init__(self) -> None:
        self.denObject: PopulationOpportunityDen
        self.needsFOVCheck: bool = True
        self.baseSpawn: Spawn | None
        """The default spawns from this den's own PopDef"""
        self.levelSpawns: List[Spawn] = []
        """All valid spawns from this level"""
        self.customSpawns: List[Spawn] = []
        """All valid spawns from our custom spawn list"""
        self.fovCustomSpawns: List[Spawn] = []
        """All valid custom spawns that can spawn from a blank point in view"""
        self.blankPoints: List[WillowPopulationPoint] = []
        """List of all blank spawn points for this den"""
    
    def FindFOVSpawns(self):
        if len(self.blankPoints) == 0:
            self.needsFOVCheck = False
            return
        self.needsFOVCheck = True
        for spawn in self.levelSpawns + self.customSpawns:
            if isinstance(spawn, CustomSpawn):
                if spawn.popDef:
                    path = spawn.popDef
                else:
                    path = spawn.factory
                if any(x in path for x in POPDEF_PREFIX_EXCLUDED_FROM_FOV_CHECKS): # type: ignore
                    self.fovCustomSpawns.append(spawn)
                    self.needsFOVCheck = False


SPAWNER = Spawner()

_initialMaxActorCost = None
"""To reset PopulationMaster's MaxActorCost on blacklisted maps or option disabled."""
_mapDenInfos: List[DenSpawnInfo] = []
""" A list of all DenSpawnInfos for each PopulationOpportunityDens in the current map with SpawnData and at least one available SpawnPoint """
pool: SpawnPool = SpawnPool.DEN
badassTagWeights = {
    Tag.CHUMP: 30,
    Tag.TOUGH: 30,
    Tag.BADASS: 20,
    Tag.ULTIMATE_BADASS: 10,
    Tag.MINIBOSS: 10,
    Tag.BOSS: 3
}
"""Weights for selecting a spawn by Badass Tag"""

@keybind("Spawn Now", "P", event_filter=EInputEvent.IE_Pressed)
def KeybindPressed() -> None:
    TrySpawnSomething(get_pc())


_modLoaded:bool = False
def ModOptionChanged(option: BaseOption, new_val) -> None:
    global TIMER
    if option == frequencySlider and TIMER.is_running():
        frequencySlider.value = new_val     # This callback occurs before the value is changed
        timeForNextSpawn = GetNewDuration()
        timerData = TIMER._get_timer_data()
        if timerData and (timerData.Rate > timeForNextSpawn or timerData.Count > timeForNextSpawn):
            TIMER.update(timeForNextSpawn, True)
        
    for tag, slider in badassWeightSliders.items():
        if option == slider:
            global badassTagWeights
            badassTagWeights[tag] = new_val
            return

def LoadOptionChanged(option: BaseOption, new_val) -> None:
    global _modLoaded, package_loads, pool
    if option == megaMixSwitch:
        if _modLoaded and megaMixSwitch.value != new_val:
            ShowPackageLoadingHelp()
    
    elif option == spawnPoolSpinner:
        if _modLoaded and pool and (pool < SpawnPool.DLC and SpawnPool[new_val] >= SpawnPool.DLC):
            ShowPackageLoadingHelp()
        pool = SpawnPool[new_val]
        
    if megaMixSwitch.value or pool >= SpawnPool.DLC:
        if not loaded_DLCs:
            #info(f"[{__name__}] Loading ALL REQUIRED PACKAGES")
            package_loads = [x for _,x in combat_packages_by_DLC.items()]
    else:
        package_loads = []
        if loaded_DLCs:
            info(f"[{__name__}] Unloading all spawn objects")
            UnloadLevelSpawnObjects()

_packageLoadingHelpSeen: bool = False
def ShowPackageLoadingHelp():
    global _packageLoadingHelpSeen
    if _packageLoadingHelpSeen:
        return
    _packageLoadingHelpSeen = True
    TrainingBox(
        title="Restart Required",
        message="A restart is required for these change to take effect, if you have already loaded into the game.\n\n" \
            "This may also cause jank with some textures.",
        min_duration=0.2
    ).show()


frequencySlider = SliderOption(
    identifier = "Frequency",
    description = "How long (on average) between ambient spawns, in seconds.",
    value = 150,
    min_value = 10,
    max_value = 300,
    step = 5,
    is_integer = True,
    on_change_while_enabled=ModOptionChanged
)
combatSwitch = BoolOption(
    identifier = "Allow in Combat",
    description = "Whether new ambient spawns can occur whilst you are already in combat."
                + (" This includes losing oxygen." if Game.get_current() is Game.TPS else ""),
    value = False,
)
spawnCapSwitch = BoolOption(
    identifier = "Increase Spawn Cap",
    description = "Increases the maximum possible number of enemies spawned at once, by 3x. Disable this if you have other mods that affect this.",
    value = True,
)
distanceMinSlider = SliderOption(
    identifier = "Min Distance",
    description = "Only spawn points between the Min Distance and Max Distance from the player are valid.",
    value = 200,
    min_value = 0,
    max_value = 20000,
    step = 500,
)
distanceMaxSlider = SliderOption(
    identifier = "Max Distance",
    description = "Only spawn points between the Min Distance and Max Distance from the player are valid.",
    value = 10000,
    min_value = 0,
    max_value = 20000,
    step = 500,
)
targetPlayerSwitch = BoolOption(
    identifier = "Target Player",
    description = "Whether ambient spawns start attacking the player when they spawn.",
    value = False,
)
customSpawnSlider = SliderOption(
    identifier = "Custom Spawn Percentage",
    description = "The percentage of ambient spawns that are bespoke groups of enemies, if any are available for the den.",
    value = 30,
    min_value = 0,
    max_value = 100,
    step = 5,
)
spawnPoolSpinner = SpinnerOption(
    identifier = "Custom Spawn Pools",
    description = "Which enemies are available for custom ambient spawns." \
            "\nChanging this may require a quit to main menu.",
    value = SpawnPool.LEVEL.name,
    choices = [x.name for x in SpawnPool],
    on_change_anytime=LoadOptionChanged
)
megaMixSwitch = BoolOption(
    identifier = "Mega Mix Spawns",
    description = "Whether enemies can substituted for similar variants, e.g. Hyperion loaders with Torgue loaders.",
    value = False,
    on_change_anytime=LoadOptionChanged
)
announceSwitch = BoolOption(
    identifier = "Announce Spawns",
    description = "Whether ambient spawns are announced with a second wind message.",
    value = False,
)

# Sliders for spawn tag weights
badassTagDescriptions: Dict[Tag, str] = {
    Tag.CHUMP : "Chump (e.g. Marauders, Psychos, Midgets, GUN loaders)",
    Tag.TOUGH : "Tough (e.g. Bruisers, Goliaths, WAR Loaders)",
    Tag.BADASS : "Badass (e.g. Badass Marauders, Badass Loaders)",
    Tag.ULTIMATE_BADASS : "Ultimate Badass (e.g. Super Badass Loaders, Badass Psychos)",
    Tag.MINIBOSS : "Mini-boss (Unique enemies)",
    Tag.BOSS : "Boss",
}
badassWeightSliders: Dict[Tag, SliderOption] = {}
for tag, description in badassTagDescriptions.items():
    badassWeightSliders[tag] = SliderOption(
        identifier = f"{tag.name} Weight",
        description = f"{description}.\nThe relative chance for this enemy type to be chosen for a spawn.",
        value = badassTagWeights[tag],
        min_value = 0,
        max_value = 100,
        step = 1,
        on_change_while_enabled=ModOptionChanged
    )
weightsNest = NestedOption(
    identifier = "Weight Options", 
    description = "Options for adjusting the chances for an enemy type to spawn, based on their badass tag.",
    children = [v for _,v in badassWeightSliders.items()]
)

optionsList = [
    frequencySlider,
    combatSwitch,
    spawnCapSwitch,
    distanceMinSlider,
    distanceMaxSlider,
    targetPlayerSwitch,
    customSpawnSlider,
    spawnPoolSpinner,
    megaMixSwitch,
    #announceSwitch,
    weightsNest
]


@hook("WillowGame.FrontendGFxMovie:Start", Type.POST_UNCONDITIONAL)
def MainMenu(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    """ The hooked function gets called when the main menu is loaded """
    if ENGINE.GetCurrentWorldInfo().GetStreamingPersistentMapName() != "menumap":
        return

    global _initialMaxActorCost, _modLoaded
    _modLoaded = True
    _initialMaxActorCost = None # PopulationMaster changes on save quit.
    return


_justLoadedIn: bool = False
@hook("WillowGame.WillowPlayerController:WillowClientShowLoadingMovie", Type.PRE)
def MapChange(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    """ The hooked function gets called when we leave any map. And when we enter one too.
    We make sure to disable spawning incase the timer is active when we transition, causing a crash.
    """
    global _justLoadedIn, _mapDenInfos
    if not _justLoadedIn: # I.E. We're just starting to load a new map
        SPAWNER.StopSpawning()
        _mapDenInfos = []

    # For some reason this function is called after loading in too so we need to flag that
    _justLoadedIn = False


#@hook("WillowGame.WillowGameInfo:PostCommitMapChange", Type.POST_UNCONDITIONAL)
@hook("WillowGame.WillowPlayerController:WillowClientDisableLoadingMovie", Type.POST_UNCONDITIONAL)
def SpawnedIn(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    """ The hooked function gets called when we load any map """
    global _initialMaxActorCost, _justLoadedIn, TIMER
    _justLoadedIn = True
    PC = get_pc()
    if not PC.IsPrimaryPlayer() or int(ENGINE.GetCurrentWorldInfo().NetMode) == 3:
        dev_warning(f"[{__name__}] Either not primary player or a client, so no ambient spawn triggers.")
        return
    
    popMaster = PC.GetWillowGlobals().GetPopulationMaster()
    currentDLC = GetCurrentDLC(PC)
    mapName = PC.WorldInfo.GetStreamingPersistentMapName()
    if mapName in BLACKLIST_MAPS:
        info(f"[{__name__}] {mapName} is a blacklisted map. No ambient spawns.")
        if TIMER.is_running():
            if not TIMER.is_paused():
                TIMER.pause()
        if popMaster and spawnCapSwitch.value and _initialMaxActorCost:
            popMaster.MaxActorCost = _initialMaxActorCost
            _initialMaxActorCost = None
        return
    
    if popMaster and spawnCapSwitch.value and not _initialMaxActorCost:
        # Increase the potential enemies at once
        _initialMaxActorCost = popMaster.MaxActorCost
        popMaster.MaxActorCost = popMaster.MaxActorCost * 3
    
    SetupDensAndCustoms(mapName, currentDLC)

    if not TIMER.is_running():
        timeForNextSpawn = GetNewDuration()
        TIMER.start(timeForNextSpawn, True)
    else:
        if TIMER.is_paused():
            TIMER.resume()


def SetupDensAndCustoms(mapName: str, biome: DLC | None):
    """
    Creates the available den list for the current map, and filters our custom spawn list to those
        available in the loaded map too.
    """
    global _mapDenInfos, pool
        
    allDens = find_all("PopulationOpportunityDen")
    validDens: List[PopulationOpportunityDen] = [x for x in allDens if
        x.Location and x.SpawnPoints and x.SpawnData and (not x.bIsCriticalActor)
        and (x.GetAllegiance() and x.GetAllegiance().Name not in BLACKLIST_ALLEGIANCES)
        and (x.GameStageRegion and x.GameStageRegion.Name not in BLACKLIST_GAME_STAGES)
        and (x.SpawnData.PopulationDefName not in BLACKLIST_POPDEFS)
        and any(y for y in x.SpawnPoints)
    ]
    mapNormalSpawns: List[Spawn] = []
    mapCustomSpawns: List[Spawn] = []
    
    if pool >= SpawnPool.LEVEL:
        uniquePopDefs = {x.PopulationDef for x in validDens if x.PopulationDef}    # Use a set so it doesn't do duplicates
        #misc([popDef.Name for popDef in uniquePopDefs])
        mapNormalSpawns = [s for s in [CustomSpawnFromPopDef(x) for x in uniquePopDefs] if s]
        for x in reversed(mapNormalSpawns):
            if not x:
                mapNormalSpawns.remove(x)
        #misc([spawn.name for spawn in mapNormalSpawns])
            
        mapCustomSpawns = []
        if pool == SpawnPool.GAME:
            for dlcCustomSpawns in CUSTOM_SPAWNS.values():
                mapCustomSpawns = mapCustomSpawns + [x for x in dlcCustomSpawns if x.LoadObjects(mapName.lower())]
        elif pool >= SpawnPool.DLC and biome:
            mapCustomSpawns = mapCustomSpawns = [x for x in CUSTOM_SPAWNS[biome] if x.LoadObjects(mapName.lower())]
        #misc([spawn.name for spawn in mapCustomSpawns])
    
    _mapDenInfos = []
    if len(validDens) == 0:
        return
    for den in validDens:
        #den.SpawnRadius = den.SpawnRadius * 1.5
        denInfo = DenSpawnInfo()
        denInfo.denObject = den
        _mapDenInfos.append(denInfo)
        
        # Store all blank spawn points for our later FOV checks
        denInfo.blankPoints = [spawnPoint for spawnPoint in den.SpawnPoints if spawnPoint and spawnPoint.Class.Name == "WillowPopulationPoint" and not spawnPoint.PointDef]
        
        # Store all CustomSpawns that this den supports
        denInfo.baseSpawn = CustomSpawnFromPopDef(den.PopulationDef)
        
        for customSpawn in mapNormalSpawns:
            if customSpawn.DenSupportsSpawn(den):
                denInfo.levelSpawns.append(customSpawn)
        
        for customSpawn in mapCustomSpawns:
            if customSpawn.DenSupportsSpawn(den):
                denInfo.customSpawns.append(customSpawn)
                
        denInfo.FindFOVSpawns()


def YourTimeIsUp():
    global TIMER
    
    PC = get_pc()
    if not (Pawn:= PC.pawn):
        return
    
    # Try not to spawn if the player is idle
    if PC.PlayerInput and PC.PlayerInput.TimeSinceLastMovement > 20:
        misc(f"[{__name__}] Idle or summin")
        TIMER.update(10, True)
        return

    # I'm using the menu check as a quick catch-all for whatever
    if not (
        PC.CanShowPauseMenu() and
        (combatSwitch.value or not Pawn.LastCombatActionTime or Pawn.WorldInfo.TimeSeconds - Pawn.LastCombatActionTime > 10)
    ):
        misc(f"[{__name__}] In combat or summin {Pawn.LastCombatActionTime} {Pawn.WorldInfo.TimeSeconds}")
        TIMER.update(10, True)
        return

    TrySpawnSomething(PC)
    
    timeForNextSpawn = GetNewDuration()
    TIMER.update(timeForNextSpawn, True)

TIMER : UnrealTimer = UnrealTimer(YourTimeIsUp)


def TrySpawnSomething(PC: WillowPlayerController):
    global _mapDenInfos
 
    # Find dens close to the player
    validDens: List[DenSpawnInfo] = []
    validWeights: List[float] = []
    for denInfo in _mapDenInfos:
        den = denInfo.denObject
        distance = DistFromPlayer(PC, den.Location)
        if distance > distanceMinSlider.value and distance < distanceMaxSlider.value:
            weight = GetLocationWeight(PC, den, denInfo.needsFOVCheck)
            if weight > 0:
                validDens.append(denInfo)
                validWeights.append(weight)
    
    # Spawn some stuff
    if validDens and validWeights:
        chosenDens = random.choices(validDens, validWeights, k=1)
        #misc(f"[{__name__}] Chosen den {chosenDens[0].denObject}")
        spawnInfo = (None, None)
        for denInfo in chosenDens:
            spawnInfo = GenerateSpawnListFromDen(PC, denInfo)
        
        spawnDen = spawnInfo[0]
        spawnList = spawnInfo[1]
        if spawnDen and spawnList:
            SPAWNER.StartSpawning(spawnDen, spawnList, targetPlayerSwitch.value)
    

def GenerateSpawnListFromDen(PC, denInfo: DenSpawnInfo) -> Tuple[PopulationOpportunityDen, List[SpawnItem]]:
    den = denInfo.denObject
    denID = den.ObjectInternalInteger
    gameStage = GetGameStage(PC, den)
    #misc("Den " + str(denID))
    #misc(str(den.SpawnData.PopulationDefName))
    
    currentSpawnList: List[SpawnItem] = []
    if pool > SpawnPool.DEN:
        # Generate the currentSpawnList from either the level spawns or custom spawns for this den.
        validPoints = []
        for spawnPoint in den.SpawnPoints:
            if spawnPoint and spawnPoint.Location:
                if GetLocationWeight(PC, spawnPoint, not spawnPoint.PointDef) > 0:
                    #misc("Valid Point " + str(spawnPoint.PointDef.Name if spawnPoint.PointDef else spawnPoint.Name))
                    validPoints.append(spawnPoint)
        
        validCustomSpawns = []
        if validPoints:
            if denInfo.customSpawns and random.randint(0, 99) < customSpawnSlider.value:
                validCustomSpawns = denInfo.customSpawns
            else:
                validCustomSpawns = denInfo.levelSpawns
        else:
            # If we have no valid FOV points then we might still have blank spawns we can use in view
            if denInfo.fovCustomSpawns:
                #misc("Using BLANK points spawn!")
                validPoints = [*denInfo.blankPoints]
                validCustomSpawns = denInfo.fovCustomSpawns
        #misc(validCustomSpawns)
            
        if validCustomSpawns:
            customSpawnWeights = [badassTagWeights[x.tag] for x in validCustomSpawns]
            if sum(customSpawnWeights) > 0:
                customSpawn: Spawn = random.choices(validCustomSpawns, customSpawnWeights)[0]
                
                if customSpawn:
                    exclusiveValidPoints = []   # Try to pick a unique spawn point until they've all been used
                    for (factory, spawnPointDef, delay) in customSpawn.GetNewFactoryList(den, gameStage, megaMix=megaMixSwitch.value):
                        if not spawnPointDef:
                            if len(exclusiveValidPoints) == 0:
                                exclusiveValidPoints = [*validPoints]
                            chosenSpawnPoint = random.choice(exclusiveValidPoints)
                            exclusiveValidPoints.remove(chosenSpawnPoint)
                            currentSpawnList.append((factory, chosenSpawnPoint, delay))
                        else:
                            # Make sure we're choosing only spawnPoints that match this custom def, if defined
                            customValidPoints = [x for x in validPoints
                                if ((not x.PointDef) and spawnPointDef == "None")
                                or (x.PointDef and x.PointDef.Name == customSpawn.spawnPointDef)
                            ]
                            if len(exclusiveValidPoints) == 0:  # Assuming all spawns in a CustomSpawn can use the same PointDefs!
                                exclusiveValidPoints = [*customValidPoints]
                            if len(exclusiveValidPoints) > 0:
                                chosenSpawnPoint = random.choice(exclusiveValidPoints)
                                #misc(chosenSpawnPoint)
                                exclusiveValidPoints.remove(chosenSpawnPoint)
                                currentSpawnList.append((factory, chosenSpawnPoint, delay))
                            else:
                                # Oh no we can't do all CustomSpawns from this den (player must be looking at all None spawns we can use)
                                #misc(f"Oh no can't actually find a spawn point {spawnPointDef} for {customSpawn.name}, you must be looking at a blank point!")
                                continue
                    if currentSpawnList and announceSwitch.value:
                        show_second_wind_notification(customSpawn.name, ui_sound=None)
            
    if len(currentSpawnList) == 0 and denInfo.baseSpawn:
        # Default to this den's usual spawn
        #misc(f"Normal Spawn from {denID}")
        if announceSwitch.value:
            show_second_wind_notification(denInfo.baseSpawn.name, ui_sound=None)
        for (factory, spawnPointDef, delay) in denInfo.baseSpawn.GetNewFactoryList(den, gameStage, megaMix=megaMixSwitch.value):
            currentSpawnList.append((factory, random.choice([point for point in den.SpawnPoints if point]), delay))

    return (den, currentSpawnList)


def GetNewDuration() -> int:
    averageTime = int(frequencySlider.value)
    randomRange = int(averageTime / 3)
    randy = random.randint(-randomRange, randomRange)
    duration = averageTime + randy
    if duration < frequencySlider.min_value:
        duration = int(frequencySlider.min_value)
    #misc(f"[{__name__}] Next duration " + str(duration))
    return duration


def GetLocationWeight(PC, actor, testFOV: bool = False) -> float:
    """ Returns a weight to choose this spawn point based on player view angle, 0 if invalid, -1 if failed FOV check """
    viewYaw = PC.CalcViewRotation.Yaw * math.pi / 32768
    viewVector = [math.cos(viewYaw), math.sin(viewYaw)]
    # Comparing Yaw only so only care about X,Y plane
    if not actor.Location:
        dev_warning(f"{str(actor)} has no Location!")
        return 0
    location = actor.Location
    normLocation = Normalise([location.X - PC.Pawn.Location.X, location.Y - PC.Pawn.Location.Y])
    dot = viewVector[0] * normLocation[0] + viewVector[1] * normLocation[1]
    
    if testFOV:
        # Probably has no spawn animation so don't do it in front of player.
        #  I CBA with 3D Yaw Pitch Roll maths so just comparing Yaw.
        #  If looking sharply up or down, you might still see these.
        #  Also we don't just spawn all the enemies at once anymore,
        #   so the delay means you might turn and see this anyway :/
        if dot >= 0:
            return -1
    
    # Bias towards points in front of the player
    return ClampRange(0.2, 1.2, dot + 1)
    

def DistFromPlayer(PC, location) -> float:
    """ Returns the distance from the player location on the X and Y planes only """
    playerLocation = PC.pawn.Location
    return math.sqrt(
        (playerLocation.X - location.X)**2 +
        (playerLocation.Y - location.Y)**2
    )

    
def Normalise(vec):
    magnitude = math.sqrt(sum(x * x for x in vec))
    return [x / magnitude for x in vec]


def ClampRange(min, max, x):
    if x < min: return min
    if x > max: return max
    return x


def OnDisable():
    global TIMER
    if TIMER.is_running():
        TIMER.stop()

mod = build_mod(options=optionsList, on_disable=OnDisable)
package_loader.register_mod(mod)
