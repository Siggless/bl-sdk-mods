import math, random
from typing import Dict, List, Tuple
import unrealsdk
from unrealsdk import Log

from Mods import ModMenu
from Mods.AmbientSpawns import custom_spawns
from Mods.AmbientSpawns import level_packages
from Mods.AmbientSpawns.level_packages import *
try:
    from Mods.UserFeedback import ShowChatMessage, TrainingBox
except ImportError as ex:
    import webbrowser
    webbrowser.open("https://bl-sdk.github.io/requirements/?mod=AmbientSpawns&UserFeedback")
    raise ex

"""
Blacklists to exclude spawning in boss maps and slaughters,
 and exclude static enemies like turrets.
"""
BLACKLIST_MAPS = {
    ModMenu.Game.BL2: [
        "Boss_Cliffs_P",
        "VOGChamber_P",
        "TundraTrain_P",
        "BanditSlaughter_P",
        "Luckys_P",
        "CreatureSlaughter_P",
        "RobotSlaughter_P",
        "SanctuaryAir_P",
        "Sanctuary_P",
        "ThresherRaid_P",
        "Boss_Volcano_P",
        "Orchid_WormBelly_P",
        "Iris_Moxxi_P",
        "Iris_DL2_Interior_P",
        "Iris_DL1_TAS_P",
        "Iris_DL1_P",
        "Sage_HyperionShip_P",
        "Village_P",
        "CastleKeep_P",     # Crashes maybe due to climb spawn point?
        "TempleSlaughter_P",
        "DungeonRaid_P",
        "SanctIntro_P",
        "BackBurner_P",
        "GaiusSanctuary_P",
        "SandwormLair_P",
        "TestingZone_P"
    ],
    ModMenu.Game.TPS: [
        "MoonSlaughter_P",
        "Spaceport_P",
        "LaserBoss_P",
        "JacksOffice_P",
        "Meriff_P",
        "Digsite_Rk5arena_P",
        "Ma_SubBoss_P",
        "Ma_FinalBoss_P",
        "Eridian_Slaughter_P"
    ]
}[ModMenu.Game.GetCurrent()]

BLACKLIST_POPDEFS = {
    ModMenu.Game.BL2: [
        None,
        "PopDef_SavageLee",
        "PopDef_Laney",
        "PopDef_Constructor",   # Highlands Outwash bridge
        'PopDef_ConstructorBadass',
        'PopDef_ConstructorMix_Regular',
        "PopDef_ConstructorTurret",
        "PopDef_BanditTurret",
        "PopDef_Hyperion_TurretGun",
        "PopDef_Hyperion_LargeTurret",
        "PopDef_Hyperion_VOGTurret",
        "PopDef_TentacleA",
        "PopDef_Iris_RakkMix_Crater",
        "PopDef_Iris_BikeWithMotorMama",
        "PopDef_Iris_RaidMamaSupportBike",
        "PopDef_Iris_BikeWithDriverAndSidecarMix",  # Motor Mama arena sides
        "PopDef_WitchDoctorMix",
        "PopDef_WitchDoctorFire",
        "PopDef_FanBoat_Manned",
        "PopDef_DrifterRaid",
        "PopDef_Treant",   # Just too many
        "PopDef_Treant_StandStill",
        "PopDef_DwarfsDen_StandStill",
        "PopDef_Knight_Archer_StandStill",
        "PopDef_Knight_BadassFireArcher_Standstill",
        "PopDef_SkeletonArcher_StandStill",
        "PopDef_SkeletonArcherMage_StandStill",
        "PopDef_FlamingSkull",
        "PopDef_Anemone_AutoCannon"
    ],
    ModMenu.Game.TPS: [
    ]
}[ModMenu.Game.GetCurrent()]
"""Static enemies or minibosses that aren't caught, or dens that we want to exclude"""

BLACKLIST_ALLEGIANCES = {
    ModMenu.Game.BL2: [
        "Allegiance_Player",
        "Allegiance_NPCNeutral",
        "Allegiance_MissionNPC",
        "Allegiance_Treant_Friendly",
        "Allegiance_Wisp"
    ],
    ModMenu.Game.TPS: [
        "Allegiance_Player",
        "Allegiance_NPCNeutral",
        "Allegiance_MissionNPC"
    ]
}[ModMenu.Game.GetCurrent()]

MIN_TIME_DURATION = 20

POPDEF_PREFIX_EXCLUDED_FROM_FOV_CHECKS = [ 
    "PopDef_Stalker",
    "PopDef_Thresher",
    "PopDef_Tentacle",
    "PopDef_Native_Elite",
    "PopDef_InfectedPod",
]
"""Enemies that spawn cloaked so look OK in view"""

FACTORY_EXCLUDED_FROM_ALLEGIANCE_CHANGE = [
    "GD_Population_Loader.Population.Unique.PopDef_Willhelm:PopulationFactoryBalancedAIPawn_1",
    "GD_Population_Engineer.Population.PopDef_HyperionSoldier:PopulationFactoryBalancedAIPawn_0",
    "GD_Population_Hyperion.Population.PopDef_HyperionMix_Fyrestone:PopulationFactoryBalancedAIPawn_4", # Is fine, but grouped with soldier for a CustomSpawn
    "GD_Aster_Pop_Golems.Population.PopDef_GolemRock:PopulationFactoryBalancedAIPawn_0",
    "GD_Aster_Pop_Golems.Population.PopDef_Golem_Badass:PopulationFactoryBalancedAIPawn_0",
    "GD_Anemone_Pop_Infected.Population.PopDef_InfectedGolem_Badass:PopulationFactoryBalancedAIPawn_0"
]
"""Enemies whose allegiance is important e.g. Wilhelm needs to match his surveyors"""


class SpawnPool(enum.IntEnum):
    DEN = enum.auto()
    LEVEL = enum.auto()
    DLC = enum.auto()
    GAME = enum.auto()


class DenSpawnInfo:
    """Stores the info and spawns that we use from a den"""
    def __init__(self) -> None:
        self.denObject: object
        self.needsFOVCheck: bool = True
        self.baseSpawn: custom_spawns.CustomSpawn
        """The default spawns from this den's own PopDef"""
        self.levelSpawns: List[custom_spawns.CustomSpawn] = []
        """All valid spawns from this level"""
        self.customSpawns: List[custom_spawns.CustomSpawn] = []
        """All valid spawns from our custom spawn list"""
        self.fovCustomSpawns: List[custom_spawns.CustomSpawn] = []
        """All valid custom spawns that can spawn from a blank point in view"""
        self.blankPoints: List[object] = []
        """List of all blank spawn points for this den"""
    
    def FindFOVSpawns(self):
        if len(self.blankPoints) == 0:
            self.needsFOVCheck = False
            return
        self.needsFOVCheck = True
        for spawn in self.customSpawns:
            if isinstance(spawn, custom_spawns.CustomSpawn):
                if spawn.popDef:
                    path = spawn.popDef
                else:
                    path = spawn.factory
                if any(x in path for x in POPDEF_PREFIX_EXCLUDED_FROM_FOV_CHECKS):
                    self.fovCustomSpawns.append(spawn)
                    self.needsFOVCheck = False


class AmbientSpawns(ModMenu.SDKMod):
    Name: str = "Ambient Spawns"
    Description: str = "<font size='20' color='#00ffe8'>Ambient Spawns</font>\n" \
        "Periodically spawns random groups of enemies.\n\n" \
        "Options for controlling the frequency and distance of spawns, " \
        "and also whether custom groups of enemies can spawn.\n\n" \
        "If enabled, enemies from all levels are loaded upon reaching the main menu, causing a delay.\n" \
        "This may cause some jank with textures."
    Author: str = "Siggles"
    Version: str = "1.1.0"
    SaveEnabledState: ModMenu.EnabledSaveType = ModMenu.EnabledSaveType.LoadWithSettings

    Types: ModMenu.ModTypes = ModMenu.ModTypes.Gameplay
    SupportedGames: ModMenu.Game = ModMenu.Game.BL2
    
    lastTime = 0    # Is world time not real time
    timeForNextSpawn = 20
    averageTimeForNextSpawn = 30
    timeRandomRange: int = 10
    
    justLoadedIn: bool = False
    isSpawning: bool = False
    lastSpawnDelayTime = 0
    currentSpawnDelay = 0.1
    currentSpawnDen = None
    currentSpawnList = []
    lastChosenSpawnPoint = None
    
    initialMaxActorCost = None
    """To reset PopulationMaster's MaxActorCost on blacklisted maps or option disabled."""
    
    megaMixActive = None
    pool: SpawnPool = None
    currentDLC: DLC = DLC.BL2

    # Keybinds = [ModMenu.Keybind("Spawn Now", "P")]

    # def GameInputPressed(self, bind: ModMenu.Keybind, event: ModMenu.InputEvent) -> None:
    #     if event != ModMenu.InputEvent.Pressed:
    #         return
    #     self.EndSpawning()
    #     self.DoTheThing()

    def __init__(self) -> None:
        super().__init__()
        
        self.mapDens = []
        """ A list of all PopulationOpportunityDens in the current map with at SpawnData least one available SpawnPoint """
        self.mapPopDefs = []
        """ A list of all PopDefs in the current map - to use for custom Spawn Pools """
        self.mapDenInfos: List[DenSpawnInfo] = []
        """ A list of all DenSpawnInfos for each Den in the current map """
        
        self.frequencySlider = ModMenu.Options.Slider(
            Caption="Frequency",
            Description="How long (on average) between ambient spawns, in seconds.",
            StartingValue=100,
            MinValue=MIN_TIME_DURATION,
            MaxValue=300,
            Increment=5,
        )
        self.combatSwitch = ModMenu.Options.Boolean(
            Caption="Allow in Combat",
            Description="Whether new ambient spawns can occur whilst you are already in combat.",
            StartingValue=False,
        )
        self.spawnCapSwitch = ModMenu.Options.Boolean(
            Caption="Increase Spawn Cap",
            Description="Increases the maximum possible number of enemies spawned at once, by 3x. Disable this if you have other mods that affect this.",
            StartingValue=True,
        )
        self.distanceMinSlider = ModMenu.Options.Slider(
            Caption="Min Distance",
            Description="Only spawn points between the Min Distance and Max Distance from the player are valid.",
            StartingValue=10,
            MinValue=10,
            MaxValue=20000,
            Increment=500,
        )
        self.distanceMaxSlider = ModMenu.Options.Slider(
            Caption="Max Distance",
            Description="Only spawn points between the Min Distance and Max Distance from the player are valid.",
            StartingValue=10000,
            MinValue=10,
            MaxValue=20000,
            Increment=500,
        )
        self.provokeDenSwitch = ModMenu.Options.Boolean(
            Caption="Provoke Dens",
            Description="Whether ambient spawns cause patrolling enemies linked to the same spawn point to attack too.",
            StartingValue=True,
        )
        self.customSpawnSlider = ModMenu.Options.Slider(
            Caption="Custom Spawn Percentage",
            Description="The percentage of ambient spawns that are bespoke groups of enemies, if any are available for the den.",
            StartingValue=30,
            MinValue=0,
            MaxValue=100,
            Increment=5,
        )
        self.spawnPoolSpinner = ModMenu.Options.Spinner(
            Caption="Custom Spawn Pools",
            Description="Which enemies are available for custom ambient spawns." \
                    "\nChanging this may require a game restart.",
            StartingValue=SpawnPool.LEVEL.name,
            Choices=[x.name for x in SpawnPool],
        )
        self.megaMixSwitch = ModMenu.Options.Boolean(
            Caption="Mega Mix Spawns",
            Description="Whether enemies can substituted for similar variants from other DLCS, e.g. Hyperion loaders with Torgue loaders.",
            StartingValue=False,
        )
        self.Options = [
            self.frequencySlider,
            self.combatSwitch,
            self.spawnCapSwitch,
            self.distanceMinSlider,
            self.distanceMaxSlider,
            self.provokeDenSwitch,
            self.customSpawnSlider,
            self.spawnPoolSpinner,
            self.megaMixSwitch,
        ]
    
    def ModOptionChanged(self, option: ModMenu.Options.Base, new_value) -> None:
        if option == self.frequencySlider:
            self.averageTimeForNextSpawn = new_value
            self.timeRandomRange = int(new_value / 3)
            if self.timeForNextSpawn > self.averageTimeForNextSpawn:
                self.timeForNextSpawn = self.averageTimeForNextSpawn
        elif option == self.megaMixSwitch:
            if self.megaMixActive and new_value:
                self.ShowPackageLoadingHelp()
            self.megaMixActive = new_value
        elif option == self.spawnPoolSpinner:
            if self.pool and (self.pool < SpawnPool.DLC and SpawnPool[new_value] >= SpawnPool.DLC):
                self.ShowPackageLoadingHelp()
            self.pool = SpawnPool[new_value]
    
    packageLoadingHelpSeen: bool = False
    def ShowPackageLoadingHelp(self):
        if self.packageLoadingHelpSeen:
            return
        self.packageLoadingHelpSeen = True
        TrainingBox(
            Title="Restart Required",
            Message="A game relaunch is required for these changes to take effect.\n\n" \
                "If required, enemies from all levels are loaded upon entering the main menu.\n" \
                "<font color='#FFA500'>This will cause a long delay between the title screen and main menu!</font>\n\n" \
                "This may also cause jank with some textures.",
            MinDuration=0.2
        ).Show()
    
    #@ModMenu.Hook("WillowGame.WillowPlayerPawnDataManager.LoadPlayerPawnDataAsync")
    @ModMenu.Hook("WillowGame.FrontendGFxMovie.Start")
    def MainMenu(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """ The hooked function gets called when the menumap loads, but we need our SaveEnabledState
         set to LoadWithSettings to ensure it hits this on the initial launch!
        """
        if unrealsdk.GetEngine().GetCurrentWorldInfo().GetStreamingPersistentMapName() != "menumap":
            return True
        
        if self.megaMixActive or self.pool >= SpawnPool.DLC:
            Log(f"[{__name__}] Loading ALL REQUIRED PACKAGES")
            # Load all enemies from all DLCs
            for deeellcee in level_packages.combat_packages_by_DLC:
                level_packages.LoadLevelSpawnObjects(deeellcee)
            custom_spawns.CacheMegaMixPools()
        return True
    
    @ModMenu.Hook("WillowGame.WillowPlayerController.WillowClientShowLoadingMovie")
    def MapChange(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """ The hooked function gets called when we leave any map.
        We make sure to disable spawning incase the timer is active when we transition, causing a crash.
        """
        if not self.justLoadedIn: # I.E. We're just starting to load a new map
            unrealsdk.RemoveHook("WillowGame.WillowPlayerController.PlayerTick", f"{self.Name}.PlayerTick")
            self.EndSpawning()
            self.currentSpawnList = []
            self.mapDenInfos = []
            self.mapDens = []
            self.mapNormalSpawns = []
            self.mapCustomSpawns = []
        # For some reason this function is called after loading in too so we need to flag that
        self.justLoadedIn = False
        return True
    
    @ModMenu.Hook("WillowGame.WillowPlayerController.WillowClientDisableLoadingMovie")
    def SpawnedIn(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """ The hooked function gets called when we load any map """
        self.justLoadedIn = True
        PC = unrealsdk.GetEngine().GamePlayers[0].Actor
        if not PC.IsPrimaryPlayer() or int(unrealsdk.GetEngine().GetCurrentWorldInfo().NetMode) == 3:
            Log(f"[{__name__}] Either not primary player or a client, so no ambient spawn triggers.")
            return
        
        popMaster = PC.GetWillowGlobals().GetPopulationMaster()
        self.currentDLC = GetCurrentDLC(PC)
        self.mapName = PC.WorldInfo.GetStreamingPersistentMapName()
        if self.mapName in BLACKLIST_MAPS:
            Log(f"[{__name__}] {self.mapName} is a blacklisted map. No ambient spawns.")
            unrealsdk.RemoveHook("WillowGame.WillowPlayerController.PlayerTick", f"{self.Name}.PlayerTick")
            if popMaster and self.spawnCapSwitch.CurrentValue and self.initialMaxActorCost:
                popMaster.MaxActorCost = self.initialMaxActorCost
                self.initialMaxActorCost = None
            return True
        
        if popMaster and self.spawnCapSwitch.CurrentValue and not self.initialMaxActorCost:
            # Increase the potential enemies at once
            self.initialMaxActorCost = popMaster.MaxActorCost
            popMaster.MaxActorCost = popMaster.MaxActorCost * 3
        
        #Log("Generating Custom Spawns for this map...")
        self.SetupDensAndCustoms(self.mapName, self.currentDLC)
        #Log("Done! Resetting timer.")
        self.lastTime = caller.WorldInfo.TimeSeconds
        self.timeForNextSpawn = self.GetNewDuration()
        
        def PlayerTick(caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
            """ We really shouldn't be checking this every tick but I can't get in-game Timers working. """
            if self.isSpawning:
                # Continue with the current playing spawn
                elapsedSpawnTime = caller.WorldInfo.TimeSeconds - self.lastSpawnDelayTime
                if elapsedSpawnTime >= self.currentSpawnDelay:
                    self.DoNextSpawn()
                    self.lastSpawnDelayTime = caller.WorldInfo.TimeSeconds
            else:
                # Check for a new spawn
                elapsedWorldTime = caller.WorldInfo.TimeSeconds - self.lastTime
                if elapsedWorldTime >= self.timeForNextSpawn:
                    #try:
                    self.DoTheThing()
                    # except TypeError:
                    #     Log('Whoops error with spawning!')
                    self.lastTime = caller.WorldInfo.TimeSeconds
            return True
        
        unrealsdk.RunHook("WillowGame.WillowPlayerController.PlayerTick", f"{self.Name}.PlayerTick", PlayerTick)
        return True
    

    def SetupDensAndCustoms(self, mapName: str, biome: DLC):
        """
        Creates the available den list for the current map, and filters out custom spawn list to those
         available in the loaded map too.
        I am identifying dens by their ObjectInternalInteger and store:
         The CustomSpawn for the den's own PopDef to use as a default.
         All matching CustomSpawns for the current pool setting.
         Matching CustomSpawns specifically that can spawn in view, for our special case.
        """
        
        allDens = unrealsdk.FindAll("PopulationOpportunityDen")
        #self.spawns = unrealsdk.FindAll("WillowPopulationPoint")
        self.mapDens = [x for x in allDens if
                        x.Location and x.SpawnPoints and x.SpawnData and (not x.bIsCriticalActor)
                        and (x.GetAllegiance() and x.GetAllegiance().Name not in BLACKLIST_ALLEGIANCES)
                        and (x.SpawnData.PopulationDefName not in BLACKLIST_POPDEFS)
                        and any(y for y in x.SpawnPoints)
                        ]
        
        if self.pool >= SpawnPool.LEVEL:
            uniquePopDefs = {x.PopulationDef for x in self.mapDens if x.PopulationDef}    # Use a set so it doesn't do duplicates
            self.mapNormalSpawns = [custom_spawns.CustomSpawnFromPopDef(x) for x in uniquePopDefs]
            for x in reversed(self.mapNormalSpawns):
                if not x:
                    self.mapNormalSpawns.remove(x)
                
            self.mapCustomSpawns = []
            if self.pool == SpawnPool.DLC and biome:
                self.mapCustomSpawns = self.mapCustomSpawns = [x for x in custom_spawns.customList[biome] if x.LoadObjects(mapName.lower())]
            elif self.pool == SpawnPool.GAME:
                for dlcCustomSpawns in custom_spawns.customList.values():
                    self.mapCustomSpawns = self.mapCustomSpawns + [x for x in dlcCustomSpawns if x.LoadObjects(mapName.lower())]
        
        self.mapDenInfos: List[DenSpawnInfo] = []
        if len(self.mapDens) == 0:
            return
        for den in self.mapDens:
            den.SpawnRadius = den.SpawnRadius * 1.5
            denInfo = DenSpawnInfo()
            denInfo.denObject = den
            self.mapDenInfos.append(denInfo)
            
            # Store all blank spawn points for our later FOV checks
            denInfo.blankPoints = [spawnPoint for spawnPoint in den.SpawnPoints if spawnPoint and not spawnPoint.PointDef]
            
            # Store all CustomSpawns that this den supports
            denInfo.baseSpawn = custom_spawns.CustomSpawnFromPopDef(den.PopulationDef)
            
            for customSpawn in self.mapNormalSpawns:
                if customSpawn.DenSupportsSpawn(den):
                    denInfo.levelSpawns.append(customSpawn)
            
            for customSpawn in self.mapCustomSpawns:
                if customSpawn.DenSupportsSpawn(den):
                    denInfo.customSpawns.append(customSpawn)
                    
            denInfo.FindFOVSpawns()
    
    def DoTheThing(self):
        # Check player conditions - I'm using the menu checks as a quick catch-all for whatever
        PC = unrealsdk.GetEngine().GamePlayers[0].Actor
        Pawn = PC.pawn
        if not Pawn:
            return

        if not (
            PC.CanShowPauseMenu() and
            (self.combatSwitch.CurrentValue or not Pawn.LastCombatActionTime or Pawn.WorldInfo.TimeSeconds - Pawn.LastCombatActionTime > 5)
        ):
            #Log("In combat or summin")
            self.timeForNextSpawn = self.timeForNextSpawn + 10
            return
        
        # Find dens close to the player
        #Log("It's spawn time baybeeeee")
        validDens: List[DenSpawnInfo] = []
        validWeights: List[float] = []
        for denInfo in self.mapDenInfos:
            den = denInfo.denObject
            distance = DistFromPlayer(PC, den.Location)
            if distance > self.distanceMinSlider.CurrentValue and distance < self.distanceMaxSlider.CurrentValue:
                weight = GetLocationWeight(PC, den, denInfo.needsFOVCheck)
                if weight > 0:
                    validDens.append(denInfo)
                    validWeights.append(weight)
        
        # Spawn some stuff
        if validDens:
            chosenDens = random.choices(validDens, validWeights, k=1)
            for denInfo in chosenDens:
                self.GenerateSpawnListFromDen(PC, denInfo)
                
            if self.currentSpawnList:
                self.StartSpawning()
        
        self.timeForNextSpawn = self.GetNewDuration()
    
    def GenerateSpawnListFromDen(self, PC, denInfo: DenSpawnInfo) -> List[Tuple[object, object, float]]:
        den = denInfo.denObject
        gameStage = self.GetGameStage(PC, den)
        
        if self.pool > SpawnPool.DEN:
            # Generate the currentSpawnList from either the level spawns or custom spawns for this den.
            self.currentSpawnList: List[(object, object)] = []
            
            validPoints = []
            for spawnPoint in den.SpawnPoints:
                if spawnPoint and spawnPoint.Location:
                    if GetLocationWeight(PC, spawnPoint, not spawnPoint.PointDef) > 0:
                        validPoints.append(spawnPoint)
            
            validCustomSpawns = []
            if len(validPoints) > 0:
                if len(denInfo.customSpawns) > 0 and random.randint(0, 99) < self.customSpawnSlider.CurrentValue:
                    validCustomSpawns = denInfo.customSpawns
                else:
                    validCustomSpawns = denInfo.levelSpawns
            else:
                # If we have no valid FOV points then we might still have blank spawns we can use in view
                if len(denInfo.fovCustomSpawns) > 0:
                    #Log("Using BLANK points spawn!")
                    validPoints = [*denInfo.blankPoints]
                    validCustomSpawns = denInfo.fovCustomSpawns
                
            if len(validCustomSpawns) > 0:
                #Log([x.name for x in validCustomSpawns])
                customSpawnWeights = [custom_spawns.BadassTagWeights[x.tag] for x in validCustomSpawns]
                #Log(customSpawnWeights)
                customSpawn: custom_spawns.CustomSpawn = random.choices(validCustomSpawns, customSpawnWeights)[0]
                #Log(f"Chosen spawn {customSpawn.name}")
                
                if customSpawn:
                    exclusiveValidPoints = []   # Try to pick a unique spawn point until they've all been used
                    for (factory, spawnPointDef, delay) in customSpawn.GetNewFactoryList(den, gameStage, megaMix=self.megaMixActive):
                        if not spawnPointDef:
                            if len(exclusiveValidPoints) == 0:
                                exclusiveValidPoints = [*validPoints]
                            chosenSpawnPoint = random.choice(exclusiveValidPoints)
                            exclusiveValidPoints.remove(chosenSpawnPoint)
                            self.currentSpawnList.append((factory, chosenSpawnPoint, delay))
                        else:
                            # Make sure we're choosing only spawnPoints that match this custom def, if defined
                            customValidPoints = [x for x in validPoints
                                if ((not x.PointDef) and spawnPointDef == "None")
                                or (x.PointDef.Name == customSpawn.spawnPointDef)
                            ]
                            if len(exclusiveValidPoints) == 0:  # Assuming all spawns in a CustomSpawn can use the same PointDefs!
                                exclusiveValidPoints = [*customValidPoints]
                            if len(exclusiveValidPoints) > 0:
                                chosenSpawnPoint = random.choice(exclusiveValidPoints)
                                exclusiveValidPoints.remove(chosenSpawnPoint)
                                self.currentSpawnList.append((factory, chosenSpawnPoint, delay))
                            else:
                                # Oh no we can't do all CustomSpawns from this den (player must be looking at all None spawns we can use)
                                #Log(f"Oh no can't actually find a spawn point {spawnPointDef} for {customSpawn.name}, you must be looking at a blank point!")
                                continue
                    # if self.currentSpawnList:
                    #     ShowChatMessage(self.Name, customSpawn.name)
                
        if len(self.currentSpawnList) == 0 and denInfo.baseSpawn:
            # Default to this den's usual spawn
            #ShowChatMessage(self.Name, denInfo.baseSpawn.name)
            for (factory, spawnPointDef, delay) in denInfo.baseSpawn.GetNewFactoryList(den, gameStage, megaMix=self.megaMixActive):
                self.currentSpawnList.append((factory, random.choice([point for point in den.SpawnPoints if point]), delay))

        self.currentSpawnDen = den
        return self.currentSpawnList


    """
    Since in the worst case we will be spawning many enemies from a single spawn point,
     we add a delay between each spawn using the PlayerTick.
    """
    def StartSpawning(self):
        self.isSpawning = True
        self.lastSpawnDelayTime = 0
        #Log(self.currentSpawnList)
        #Log("-----Spawning-----")
    
    def DoNextSpawn(self):
        (factory, spawn, delay) = self.currentSpawnList.pop(0)
        
        if len(self.currentSpawnList) == 0:
            self.EndSpawning()
        
        if not factory or not spawn:
            return
        
        # Try not to spawn enemies on top of eachother by adjusting the delay
        if len(self.currentSpawnList) > 0:
            if spawn is self.currentSpawnList[0][1]:
                delay = delay + 3
            self.currentSpawnDelay = delay
        
        den = self.currentSpawnDen
        PC = unrealsdk.GetEngine().GamePlayers[0].Actor
        gameStage = self.GetGameStage(PC, den)
        popMaster = PC.GetWillowGlobals().GetPopulationMaster()
        
        if spawn.StretchyActor:
            # Fix up the Helios spawn anim and other orbital ones
            loc = spawn.StretchyActor.Location
            rot = spawn.StretchyActor.Rotation
        else:
            loc = spawn.Location
            rot = spawn.Rotation
        locTuple = (loc.X, loc.Y, loc.Z)
        rotTuple = (rot.Pitch, rot.Yaw, rot.Roll)
        
        # This function ensures that the spawns are destroyed on map change
        spawnedPawn = popMaster.SpawnActorFromOpportunity(
            factory,
            den,
            locTuple, rotTuple,
            gameStage, 1,
            0, 0,    # Setting oppIndex from GetOpportunityIndex crashes sometimes - bullymongs
            False, False
        )

        # I hope you're not here looking for answers...
        if spawnedPawn:
            spawn.ActorSpawned(spawnedPawn)     # Play the SpecialMove spawn animation
            if spawn:
                spawnedPawn.MySpawnPoint = spawn    # Orbital drop ground shake and spawn anims
            
            # If it's the Infected Pods then rotate them to try and stop them overlapping in the same point
            if factory.PathName(factory).startswith("GD_Anemone_InfectedPodTendril.Population.PopDef_InfectedPodTendril"):
                rotTuple = (rot.Pitch, int(len(self.currentSpawnList) * 7000), rot.Roll)
                spawnedPawn.Rotation = rotTuple
            
            # Prevent different allegiance enemies attacking eachother from the same den
            if factory.PathName(factory) not in FACTORY_EXCLUDED_FROM_ALLEGIANCE_CHANGE:
                spawnedPawn.SetAllegiance(den.GetAllegiance())
            
            mind = spawnedPawn.MyWillowMind
            if mind.AIClass:    # Don't affect the combat music on initial target (weird if spawned miles away and can't path)
                preClassThreat = mind.AIClass.CombatMusicTargetingThreat
                mind.AIClass.CombatMusicTargetingThreat = 0
            
            # Start attacking the player on spawn
            AIComp = mind.GetAIComponent()
            AIComp.AddTarget(PC.pawn)
            AIComp.NotifyAttackedBy(PC.pawn)
            mind.GetAIDefinition().TargetSearchRadius = self.distanceMaxSlider.CurrentValue    # This may change it for ALL of this definition too...
            # I would like to get the full AI node tree in the AIDef running like regular spawns,
            #  so they Patrol, etc, but can't get that working.
            #Log(mind.AIClass.AIDef.NodeList)
            
            if mind.AIClass:
                mind.AIClass.CombatMusicTargetingThreat = preClassThreat
            
            # Also get nearby patrolling enemies from this den to attack
            if self.provokeDenSwitch.CurrentValue:
                den.TriggerProvokedEvents()
                denAI = den.GetAIComponent()
                denAI.AddTarget(PC.pawn)
                denAI.NotifyAttackedBy(PC.pawn)
                        
            spawnedPawn.PlayTaunt()
    
    def EndSpawning(self):
        self.isSpawning = False
        #Log("-----Spawning OVER-----")

    def GetNewDuration(self) -> int:
        randy = random.randint(-self.timeRandomRange, self.timeRandomRange)
        duration = self.averageTimeForNextSpawn + randy
        if duration < MIN_TIME_DURATION:
            duration = MIN_TIME_DURATION
        #ShowChatMessage(self.Name, "Next duration " + str(duration))
        return duration

    def GetGameStage(self, PC, den=None) -> int:
        stage = 0
        if den:
            out = den.GetOpportunityGameStage()
            if out[0]:
                stage = out[1]
        if stage == 0:
            # From WillowPlayerController.FixupPlaythroughTwo
            mission = PC.MissionPlaythroughs[1].MissionList[0].MissionDef.NextMissionInChain
            if mission:
                out = mission.GameStageRegion.GetRegionGameStage()
                if out[0]:
                    stage = out[1]
        if stage == 0:
            if PC.pawn:
                stage = PC.pawn.GetGameStage()
            else:
                stage = 1
        return stage


def GetLocationWeight(PC, actor, testFOV: bool = False) -> float:
    """ Returns a weight to choose this spawn point based on player view angle, 0 if invalid, -1 if failed FOV check """
    viewYaw = PC.CalcViewRotation.Yaw * math.pi / 32768
    viewVector = [math.cos(viewYaw), math.sin(viewYaw)]
    # Comparing Yaw only so only care about X,Y plane
    if not actor.Location:
        return 0
    location = actor.Location
    normLocation = Normalise([location.X - PC.Pawn.Location.X, location.Y - PC.Pawn.Location.Y])
    dot = viewVector[0]*normLocation[0] + viewVector[1]*normLocation[1]
    
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


instance = AmbientSpawns()

# Lets us reload the mod in-game using the console command pyexec
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
