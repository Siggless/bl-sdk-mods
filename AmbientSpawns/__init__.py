from typing import List, Tuple, Union
import enum
import math, random
import unrealsdk
from unrealsdk import Log

from Mods import ModMenu
from Mods.AmbientSpawns import custom_spawns
from Mods.AmbientSpawns import level_packages
from Mods.AmbientSpawns.level_packages import *
from Mods.UserFeedback import ShowChatMessage, TrainingBox

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
        "CastleKeep_P", # Crashes maybe due to climb spawn point?
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

BLACKLIST_POPDEFS = {   # Static enemies or minibosses that aren't caught
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
        "PopDef_WitchDoctorMix",
        "PopDef_WitchDoctorFire",
        "PopDef_DrifterRaid",
        "PopDef_FlamingSkull",
        "PopDef_Anemone_AutoCannon"
    ],
    ModMenu.Game.TPS: [
    ]
}[ModMenu.Game.GetCurrent()]

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

MIN_TIME_DURATION = 10

POPDEF_PREFIX_EXCLUDED_FROM_FOV_CHECKS = [  # Enemies that spawn cloaked so look OK in view
    "PopDef_Stalker",
    "PopDef_Thresher",
    "PopDef_Native_Elite",
]

FACTORY_EXCLUDED_FROM_ALLEGIANCE_CHANGE = [ # Enemies whose allegiance is important e.g. Wilhelm needs to match his surveyors
    "GD_Population_Loader.Population.Unique.PopDef_Willhelm:PopulationFactoryBalancedAIPawn_1",
    "GD_Anemone_Pop_Infected.Population.PopDef_InfectedGolem_Badass:PopulationFactoryBalancedAIPawn_0"
]

class SpawnPool(enum.IntEnum):
    DEN = enum.auto()
    LEVEL = enum.auto()
    DLC = enum.auto()
    GAME = enum.auto()

class AmbientSpawns(ModMenu.SDKMod):
    Name: str = "Ambient Spawns"
    Description: str = "<font size='20' color='#00ffe8'>Ambient Spawns</font>\n" \
        "Periodically spawns random groups of enemies.\n\n" \
        "Options for controlling the frequency and distance of spawns, " \
        "and also whether custom groups of enemies can spawn.\n\n" \
        "If enabled, enemies from all levels are loaded upon reaching the main menu, causing a delay.\n" \
        "This may cause some jank with textures."
    Author: str = "Siggles"
    Version: str = "1.0.0"
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
    
    minDistance: int = 10
    maxDistance: int = 10000
    canSpawnWhilstInCombat = False
    increaseSpawnCap = True
    customSpawnPercentage = 30
    initialMaxActorCost = None
    provokeDens = True
    
    megaMixActive = False
    pool: SpawnPool = None
    currentDLC: DLC = DLC.BL2
    heliosActor = None

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
        """ A list of all PopDefs in the current map - to use for custom Spawn Pools"""
        
        self.frequencySlider = ModMenu.Options.Slider(
            Caption="Frequency",
            Description="How long (on average) between ambient spawns, in seconds.",
            StartingValue=100,
            MinValue=MIN_TIME_DURATION,
            MaxValue=200,
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
        self.spawnPoolSpinner = ModMenu.Options.Spinner(
            Caption="Custom Spawn Pools",
            Description="Which enemies are available for custom ambient spawns." \
                    "\nChanging this may require a game restart.",
            StartingValue=SpawnPool.LEVEL.name,
            Choices=[x.name for x in SpawnPool],
        )
        self.customSpawnSlider = ModMenu.Options.Slider(
            Caption="Custom Spawn Percentage",
            Description="The percentage of ambient spawns that are bespoke groups of enemies, if any are available for the den.",
            StartingValue=30,
            MinValue=0,
            MaxValue=100,
            Increment=5,
        )
        self.Options = [
            self.frequencySlider,
            self.combatSwitch,
            self.spawnCapSwitch,
            self.distanceMinSlider,
            self.distanceMaxSlider,
            self.provokeDenSwitch,
            self.spawnPoolSpinner,
            self.customSpawnSlider,
        ]
    
    def ModOptionChanged(self, option: ModMenu.Options.Base, new_value) -> None:
        if option == self.frequencySlider:
            self.averageTimeForNextSpawn = new_value
            self.timeRandomRange = int(new_value / 3)
            if self.timeForNextSpawn > self.averageTimeForNextSpawn:
                self.timeForNextSpawn = self.averageTimeForNextSpawn
        elif option == self.combatSwitch:
            self.canSpawnWhilstInCombat = new_value
        elif option == self.spawnCapSwitch:
            self.increaseSpawnCap = new_value
        elif option == self.distanceMinSlider:
            self.minDistance = new_value
        elif option == self.distanceMaxSlider:
            self.maxDistance = new_value
        elif option == self.provokeDenSwitch:
            self.provokeDens = new_value
        elif option == self.spawnPoolSpinner:
            if self.pool and \
                (self.pool < SpawnPool.DLC and SpawnPool[new_value] >= SpawnPool.DLC or \
                self.pool >= SpawnPool.DLC and SpawnPool[new_value] < SpawnPool.DLC):
                self.ShowPackageLoadingHelp()
            self.pool = SpawnPool[new_value]
        elif option == self.customSpawnSlider:
            self.customSpawnPercentage = new_value
    
    packageLoadingHelpSeen : bool = False
    def ShowPackageLoadingHelp(self):
        if self.packageLoadingHelpSeen:
            return
        TrainingBox(
            Title="Restart Required",
            Message="A game relaunch is required for these changes to take effect.\n\n" \
                "If required, enemies from all levels are loaded upon entering the main menu.\n" \
                "<font color='#FFA500'>This will cause a long delay between the title screen and main menu!</font>\n\n" \
                "This may also cause jank with some textures.",
            MinDuration=0.2
        ).Show()
    
    @ModMenu.Hook("WillowGame.FrontendGFxMovie.Start")
    def MainMenu(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """
        The hooked function gets called when the menumap loads, but we need our SaveEnabledState
            set to LoadWithSettings to ensure it hits this on the initial launch!
        """
        if unrealsdk.GetEngine().GetCurrentWorldInfo().GetStreamingPersistentMapName() != "menumap":
            return True

        if self.megaMixActive or self.pool >= SpawnPool.DLC:
            Log(f"[{__name__}] LOADING ALL REQUIRED PACKAGES")
            # Load all enemies from all DLCs
            for deeellcee in level_packages.combat_packages_by_DLC:
                level_packages.LoadLevelSpawnObjects(deeellcee)
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
        # For some reason this function is called after loading in too so we need to flag that
        self.justLoadedIn = False
        return True
    
    @ModMenu.Hook("WillowGame.WillowPlayerController.WillowClientDisableLoadingMovie")
    def SpawnedIn(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        """ The hooked function gets called when we load any map """
        self.justLoadedIn = True
        PC = unrealsdk.GetEngine().GamePlayers[0].Actor

        if not PC.IsPrimaryPlayer():
            Log(f"[{__name__}] Not primary player so no ambient spawn triggers.")
            return
        
        popMaster = PC.GetWillowGlobals().GetPopulationMaster()
        self.currentDLC = GetCurrentDLC(PC)
        self.mapName = PC.WorldInfo.GetStreamingPersistentMapName()
        if self.mapName in BLACKLIST_MAPS:
            Log(f"[{__name__}] {self.mapName} is a blacklisted map. No ambient spawns.")
            unrealsdk.RemoveHook("WillowGame.WillowPlayerController.PlayerTick", f"{self.Name}.PlayerTick")
            if popMaster and self.increaseSpawnCap and self.initialMaxActorCost:
                popMaster.MaxActorCost = self.initialMaxActorCost
                self.initialMaxActorCost = None
            return True
        
        if popMaster and self.increaseSpawnCap and not self.initialMaxActorCost:
            # Increase the potential enemies at once
            self.initialMaxActorCost = popMaster.MaxActorCost
            popMaster.MaxActorCost = popMaster.MaxActorCost * 3
        
        #Log("Generating Custom Spawns for this map...")
        self.SetupDensAndCustoms(self.mapName, self.currentDLC)

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
    

    def SetupDensAndCustoms(self, mapName:str, biome:DLC):
        """
        Creates the available den list for the current map, and filters out custom spawn list to those
         available in the loaded map too.
        """
        self.heliosActor = None
        for x in unrealsdk.FindAll("InterpActor"):
            if x.ReplicatedMesh and x.ReplicatedMesh.Name == "MoonBase02":
                self.heliosActor = x
                break
        
        allDens = unrealsdk.FindAll("PopulationOpportunityDen")
        #self.spawns = unrealsdk.FindAll("WillowPopulationPoint")
        self.mapDens = [x for x in allDens if
                        x.Location and x.SpawnPoints and x.SpawnData and (not x.bIsCriticalActor)
                        and (x.GetAllegiance() and x.GetAllegiance().Name not in BLACKLIST_ALLEGIANCES)
                        and (x.SpawnData.PopulationDefName not in BLACKLIST_POPDEFS)
                        and any(y for y in x.SpawnPoints)   # and y.PointDef - No because threshers have no PointDef
                        ]
        
        if self.pool >= SpawnPool.LEVEL:
            uniquePopDefs = {x.PopulationDef for x in self.mapDens if x.PopulationDef}    # Use a set so it doesn't do duplicates
            #Log(uniquePopDefs)
            self.mapNormalSpawns = [custom_spawns.CustomSpawnFromPopDef(x) for x in uniquePopDefs]
            for x in reversed(self.mapNormalSpawns):
                if not x:
                    self.mapNormalSpawns.remove(x)
            #Log(self.mapNormalSpawns)
                
            self.mapCustomSpawns = []
            if self.pool == SpawnPool.DLC and biome:
                self.mapCustomSpawns = self.mapCustomSpawns = [x for x in custom_spawns.customList[biome] if x.LoadObjects(mapName.lower())]
            elif self.pool == SpawnPool.GAME:
                for dlcCustomSpawns in custom_spawns.customList.values():
                    self.mapCustomSpawns = self.mapCustomSpawns + [x for x in dlcCustomSpawns if x.LoadObjects(mapName.lower())]
        
            self.normalSpawnByDen = {}
            self.customSpawnByDen = {}
            if len(self.mapDens) == 0:
                return
            for den in self.mapDens:
                den.SpawnRadius = den.SpawnRadius * 1.5
                
                # Store all CustomSpawns that this den supports
                self.normalSpawnByDen[den.ObjectInternalInteger] = []
                denList = self.normalSpawnByDen[den.ObjectInternalInteger]
                for customSpawn in self.mapNormalSpawns:
                    if customSpawn.DenSupportsSpawn(den):
                        denList.append(customSpawn)
                
                self.customSpawnByDen[den.ObjectInternalInteger] = []
                denList = self.customSpawnByDen[den.ObjectInternalInteger]
                for customSpawn in self.mapCustomSpawns:
                    if customSpawn.DenSupportsSpawn(den):
                        denList.append(customSpawn)
    

    def DoTheThing(self):
        # Check player conditions - I'm using the menu checks as a quick catch-all for whatever
        PC = unrealsdk.GetEngine().GamePlayers[0].Actor
        Pawn = PC.pawn
        if not Pawn:
            return

        if not (
            PC.CanShowPauseMenu() and
            (self.canSpawnWhilstInCombat or not Pawn.LastCombatActionTime or Pawn.WorldInfo.TimeSeconds - Pawn.LastCombatActionTime > 5)
        ):
            #Log("In combat or summin")
            return
        
        # Find dens close to the player
        #Log("It's spawn time baybeeeee")
        validDens = []
        validWeights = []
        for den in self.mapDens:
            #Log(f"Distance check {den.SpawnData.PopulationDefName} {den.PathName(den)}")
            distance = DistFromPlayer(PC, den.Location)
            if distance > self.minDistance and distance < self.maxDistance:
                weight = GetLocationWeight(PC, den, all(not x.PointDef for x in den.SpawnPoints if x))
                if weight > 0:
                    validDens.append(den)
                    validWeights.append(weight)
        
        # Spawn some stuff
        if validDens:
            chosenDens = random.choices(validDens, validWeights, k=1)
            for den in chosenDens:
                self.GenerateSpawnListFromDen(PC, den)
                
            if self.currentSpawnList and len(self.currentSpawnList) > 0:
                self.StartSpawning()
        
        self.timeForNextSpawn = self.GetNewDuration()
    
    def GenerateSpawnListFromDen(self, PC, den) -> List[Tuple[object, object, float]]:
        gameStage = self.GetGameStage(PC, den)
        denID = den.ObjectInternalInteger
        #Log("Den " + str(denID))
        
        if self.pool > SpawnPool.DEN or not self.customSpawnByDen[denID]:
            validPoints = []
            for spawnPoint in den.SpawnPoints:
                if spawnPoint:
                    if spawnPoint.Location and GetLocationWeight(PC, spawnPoint, not spawnPoint.PointDef) > 0:
                        validPoints.append(spawnPoint)
            
            exclusiveValidPoints = [*validPoints]
            # Generate the currentSpawnList using either a CustomSpawn or den factory.
            self.currentSpawnList: List[(object, object)] = []
            if len(self.customSpawnByDen[denID])>0 and random.randint(0,99)<self.customSpawnPercentage:
                # Pick a random CustomSpawn from this den's valid CustomSpawns
                validCustomSpawns = self.customSpawnByDen[denID]
            else:
                validCustomSpawns = self.normalSpawnByDen[denID]
                
            if len(validCustomSpawns) > 0:
                #Log([x.name for x in validCustomSpawns])
                customSpawnWeights = [custom_spawns.BadassTagWeights[x.tag] for x in validCustomSpawns]
                #Log(customSpawnWeights)
                customSpawn = random.choices(validCustomSpawns, customSpawnWeights)[0]
                #Log(f"Chosen spawn {customSpawn.name}")
                
                if customSpawn:
                    exclusiveValidPoints = []
                    for (factory, spawnPointDef, delay) in customSpawn.GetNewFactoryList(den, gameStage):
                        if not spawnPointDef:
                            if len(exclusiveValidPoints) == 0:
                                exclusiveValidPoints = [*validPoints]
                            chosenSpawnPoint = random.choice(exclusiveValidPoints)
                            exclusiveValidPoints.remove(chosenSpawnPoint)
                            self.currentSpawnList.append((factory, chosenSpawnPoint, delay))
                        else:
                            # Make sure we're choosing only spawnPoints that match this custom def, if defined
                            customValidSpawns = [x for x in validPoints
                                if ((not x.PointDef) and spawnPointDef == "None")
                                or (x.PointDef.Name == customSpawn.spawnPointDef)
                            ]
                            if len(exclusiveValidPoints) == 0:
                                exclusiveValidPoints = [*customValidSpawns]
                            if len(exclusiveValidPoints) > 0:
                                # Try to pick a unique spawn point until they've all been used
                                chosenSpawnPoint = random.choice(exclusiveValidPoints)
                                exclusiveValidPoints.remove(chosenSpawnPoint)
                                self.currentSpawnList.append((factory, chosenSpawnPoint, delay))
                            else:
                                # Oh no we can't do all CustomSpawns from this den (player must be looking at all None spawns we can use)
                                self.currentSpawnList = None
                                #Log(f"Oh no can't actually spawn {customSpawn.name}, you must be looking at a blank point!")
                                break
                
            
        if not self.currentSpawnList and len(exclusiveValidPoints) > 0:
            self.currentSpawnList: List[(object, object)] = []
            numSpawns = random.randint(2,5)
            for _ in range(numSpawns):
                factory = den.PopulationDef.GetRandomFactory(den, gameStage, 1)
                if len(exclusiveValidPoints) == 0:
                    exclusiveValidPoints = [*validPoints]
                chosenSpawnPoint = random.choice(exclusiveValidPoints)
                self.currentSpawnList.append((factory, chosenSpawnPoint, 0.2))
                exclusiveValidPoints.remove(chosenSpawnPoint)
                if factory.PawnBalanceDefinition and factory.PawnBalanceDefinition.Champion:
                    break

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
        #Log(str(len(self.currentSpawnList)) + " spawns left")
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
            # Some spawns play the giant muzzle flash instead IDK why...
            loc = spawn.StretchyActor.Location
            rot = spawn.StretchyActor.Rotation
        else:
            loc = spawn.Location
            rot = spawn.Rotation
        locTuple = (loc.X, loc.Y, loc.Z)
        rotTuple = (rot.Pitch, rot.Yaw, rot.Roll)
        
        # This function ensures that the spawns are destroyed on map change
        spawnedPawn = popMaster.SpawnActorFromOpportunity(factory,
                                            den,
                                            locTuple,rotTuple,
                                            gameStage,1,
                                            0,0,    # Setting oppIndex from GetOpportunityIndex crashes sometimes - bullymongs
                                            False,False
                                            )

        # I hope you're not here looking for answers...
        if spawnedPawn:
            # Play the SpecialMove spawn animation
            spawn.ActorSpawned(spawnedPawn)
            #spawnedPawn.MySpawnPoint = spawn
            
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
            # I would like to get the full AI node tree in the AIDef running like regular spawns,
            #  so they Patrol, etc, but can't get that working.
            #Log(mind.AIClass.AIDef.NodeList)
            
            if mind.AIClass:
                mind.AIClass.CombatMusicTargetingThreat = preClassThreat
            
            # Also get nearby patrolling enemies from this den to attack
            if self.provokeDens:
                den.TriggerProvokedEvents()
                denAI = den.GetAIComponent()
                denAI.AddTarget(PC.pawn)
                denAI.NotifyAttackedBy(PC.pawn)
                        
            #spawnedPawn.PlayTaunt()    # Sometimes crashes because AKEvents not loaded?
    
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

    def GetGameStage(self, PC, den=None):
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


def GetLocationWeight(PC, actor, testFOV:bool = False) -> int:
    """ Returns a weight to choose this spawn point based on player view angle, or 0 if invalid """
    viewYaw = PC.CalcViewRotation.Yaw * math.pi / 32768
    viewVector = [math.cos(viewYaw), math.sin(viewYaw)]
    # Comparing Yaw only so only care about X,Y plane
    if not actor.Location:
        #Log(f"{str(actor)} has no Location!")
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
            return 0
    
    # Bias towards points in front of the player
    return ClampRange(0.2, 1.2, dot + 1)#**2
    

def DistFromPlayer(PC, location) -> float:
    """ Returns the distance from the player location on the X and Y planes only """
    playerLocation = PC.pawn.Location
    return math.sqrt(
        (playerLocation.X - location.X)**2 +
        (playerLocation.Y - location.Y)**2
    )
    
def Normalise(vec):
    magnitude = math.sqrt(sum(x*x for x in vec))
    return [x/magnitude for x in vec]

def ClampRange(min, max, x):
    if x < min: return min
    if x > max: return max
    return x


instance = AmbientSpawns()

# # Lets us reload the mod in-game using the console command pyexec
# if __name__ == "__main__":
#     unrealsdk.Log(f"[{instance.Name}] Manually loaded")
#     for mod in ModMenu.Mods:
#         if mod.Name == instance.Name:
#             if mod.IsEnabled:
#                 mod.Disable()
#             ModMenu.Mods.remove(mod)
#             unrealsdk.Log(f"[{instance.Name}] Removed last instance")

#             # Fixes inspect.getfile()
#             instance.__class__.__module__ = mod.__class__.__module__
#             break

ModMenu.RegisterMod(instance)
