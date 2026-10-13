import enum, random

from unrealsdk import find_class, find_object
from unrealsdk.logging import dev_warning, misc
from unrealsdk.unreal import UObject
from mods_base import Game

from typing import List, Set, Tuple
AIPawnBalanceDefinition = UObject
PopulationBodyTag = UObject
PopulationFactoryBalancedAIPawn  = UObject
PopulationFactoryWillowVehicle  = UObject
WillowPopulationDefinition = UObject
WillowPopulationPointDefinition = UObject
MegaMixPool = List[Tuple[AIPawnBalanceDefinition, PopulationFactoryBalancedAIPawn]]

ClassPopulationFactoryBalancedAIPawn = find_class("PopulationFactoryBalancedAIPawn")
ClassPopulationFactoryPopulationDefinition = find_class("PopulationFactoryPopulationDefinition")
ClassPopulationFactoryWillowVehicle = find_class("PopulationFactoryWillowVehicle")
ClassWillowPopulationPoint = find_class("WillowPopulationPoint")

from .level_packages import DLC, GetDLCFromObject

if Game.get_current() == Game.TPS:
    from .TPS.megamix import MEGAMIX_SUBSTITUTION_POOLS
else:
    from .BL2.megamix import MEGAMIX_SUBSTITUTION_POOLS


class Tag(enum.IntEnum):
    CHUMP = enum.auto()
    TOUGH = enum.auto()    # E.g. WAR loader
    BADASS = enum.auto()
    ULTIMATE_BADASS = enum.auto()   # E.g. Big Boi Loader
    MINIBOSS = enum.auto()
    BOSS = enum.auto()
    _LENGTH = enum.auto()


POPDEF_TAG_OVERRIDES = [
    "PopDef_Orchid_SandWormQueen",
    "PopDef_WitchDoctorMix",
    "PopDef_WitchDoctorFire",
    "PopDef_Treant",
    "PopDef_HiveMind",
    "PopDef_HiveFlyer_TritonFlats",
    "PopDef_HiveFlyers_Station_TritonFlats",
    "PopDef_ShockHives_TritonFlats",
    "PopDef_BadassHive",
    "PopDef_ShockHive",
    "PopDef_CryoHive",
    "PopDef_GiantCryoHive",
    "PopDef_ScavWastelandWalker",
    "PopDef_ElementalIce_Rider",
    "PopDef_DahlMarine_CentralTerm",
    "PopDef_Clap_L3K",
    "PopDef_Opha_Normal",
    "PopDef_Opha_Heavy",
]
"""PopDefs that aren't caught by our other checks but we want to tag as ULTIMATE_BADASS"""


megaMixCache: List[MegaMixPool] = []

def CacheMegaMixPools():
    global megaMixCache
    megaMixCache = []
    for pool in MEGAMIX_SUBSTITUTION_POOLS: # type: ignore
        poolCache: MegaMixPool = []
        poolBodyTag = None
        for factoryPath in pool:
            # We store the AIDef and a loaded Factory to compare and then use
            try:
                factoryObj = find_object(ClassPopulationFactoryBalancedAIPawn, factoryPath)
            except ValueError:
                dev_warning(f"MegaMix - Can't find factory {factoryPath}")
                continue
            AIDef = factoryObj.PawnBalanceDefinition
            if AIDef:
                if str(AIDef.Class.Name) != "AIPawnBalanceDefinition":
                    # Is another PopDef instead of an AIDef
                    dev_warning(f"MegaMix - {factoryPath} does not have an AIPawnBalanceDefinition (probably is another PopDef)")
                    continue
                # Check all body tags match in this pool too
                bodyTag = GetBodyTagFromFactory(factoryObj)
                if not poolBodyTag:
                    poolBodyTag = bodyTag
                poolCache.append((AIDef, factoryObj))
        if len(poolCache) > 1:
            megaMixCache.append(poolCache)


def GetMegaMixPoolsFromFactoryList(allFactories: List[PopulationFactoryBalancedAIPawn | PopulationFactoryWillowVehicle]) -> List[MegaMixPool]:
    pawnFactories = [f for f in allFactories if f.Class is ClassPopulationFactoryBalancedAIPawn]
    return [pool for pool in megaMixCache if any(x[0] in [f.PawnBalanceDefinition for f in pawnFactories] for x in pool)]


def GetAllFactoriesFromPopDef(popDef: WillowPopulationDefinition) -> Set[PopulationFactoryBalancedAIPawn | PopulationFactoryWillowVehicle]:
    """
    Some PopDefs list PopulationFactoryPopulationDefinition instead of PopulationFactoryBalancedAIPawn.
    We recurse through these to get the actual PopulationFactoryBalancedAIPawns.
    Some vehicle ones have PopulationFactoryWillowVehicle instead.
    """
    allFactories = set()    # Set to discount any duplicates
    for archetype in popDef.ActorArchetypeList:
        spawnFactory = archetype.SpawnFactory
        if spawnFactory:
            factoryClass = spawnFactory.Class
            if factoryClass is ClassPopulationFactoryBalancedAIPawn or factoryClass is ClassPopulationFactoryWillowVehicle:
                allFactories.add(spawnFactory)
            elif factoryClass == ClassPopulationFactoryPopulationDefinition:
                if spawnFactory.PopulationDef:
                    allFactories = allFactories.union(GetAllFactoriesFromPopDef(spawnFactory.PopulationDef))
    return allFactories


def GetBodyTagFromFactory(factory) -> PopulationBodyTag | None:
    if factory.Class is not ClassPopulationFactoryBalancedAIPawn:
        return None
    
    AIPawnBalanceDef = factory.PawnBalanceDefinition
    if not AIPawnBalanceDef:
        return None
    if not AIPawnBalanceDef.AIPawnArchetype:
        return None
    return AIPawnBalanceDef.AIPawnArchetype.BodyClass.BodyTag


"""
This is how I define all bespoke spawns that aren't using the in-game population points.
I am choosing to return PopulationFactoryBalancedAIPawns instead of WillowPopulationDefinitions,
 because not all enemies have a unique PopDef, but they do all have a unique factory.
"""

class Spawn:
    def __init__(self, name: str, tag: Tag, spawnPointDef: WillowPopulationPointDefinition | str | None, map_whitelist: List[str], map_blacklist: List[str]):
        self.name = name
        if tag:
            self.tag = tag
        else:
            self.tag = Tag.CHUMP
        self.delayBetweenSpawns = 0.5
        self.minDistance = 0
        
        self.spawnPointDef: WillowPopulationPointDefinition | str | None = spawnPointDef
        """Specify ONLY spawn points with this WillowPopulationPointDefinition e.g. 'GD_ConstructorShared.Den.PopPointDef_OrbitalDrop'.
         "None" as a string really means None object when we use this."""
        if self.spawnPointDef == "None":
            self.delayBetweenSpawns = 0.1
        self.map_whitelist = [mapName.lower() for mapName in map_whitelist]
        self.map_blacklist = [mapName.lower() for mapName in map_blacklist]
        
    def LoadObjects(self, mapNameLower) -> bool:
        raise NotImplementedError
    
    def DenSupportsSpawn(self, den) -> bool:
        raise NotImplementedError
    
    def GetNewFactoryList(self, den, gameStage, rarity=1, megaMix=False):
        """Returns a list of (factory, spawnPointDef, delay) for a random instance of this spawn"""
        raise NotImplementedError


class CustomSpawn(Spawn):
    """Spawns a random number of a given popDef or factory."""
    def __init__(self, name, tag, numSpawns=None, numSpawnsWeights=None, popDef=None, factory=None, spawnPointDef=None, map_whitelist=[], map_blacklist=[]) -> None:
        super().__init__(name, tag, spawnPointDef, map_whitelist, map_blacklist)
        
        if numSpawns:
            self.numSpawns = list(numSpawns)
            if numSpawnsWeights:
                self.numSpawnsWeights = list(numSpawnsWeights)
                if len(self.numSpawns) != len(self.numSpawnsWeights):
                    raise ValueError(f"{self.name} numSpawnsWeights do not match numSpawns:\t{self.numSpawns} - {self.numSpawnsWeights}")
            else:
                self.numSpawnsWeights = [1 for x in self.numSpawns]
        else:
            self.numSpawns = [1]
            self.numSpawnsWeights = [1]
        self.minSpawns = min(self.numSpawns)
        self.maxSpawns = max(self.numSpawns)
            
        self.popDef: str | None = None
        self.factory: str | None = factory
        if not factory:
            if popDef:
                self.popDef = popDef
            else:
                self.popDef = "GD_Explosives.Populations.Pop_BarrelMixture"
        
        self.map_blacklist = []
        self.map_whitelist = []
        
        self.factoryObj: PopulationFactoryBalancedAIPawn | None = None
        self.popDefObj: WillowPopulationDefinition | None = None
        self.bodyTagObj: PopulationBodyTag | None = None
        
        self.megaMixPools: List[MegaMixPool] = []
    
    
    def GetRandomNumSpawns(self):
        if self.minSpawns == self.maxSpawns:
            return self.minSpawns
        return random.choices(self.numSpawns, self.numSpawnsWeights)[0]
    
    
    def GetNewFactoryList(self, den, gameStage, rarity=1, megaMix=False):
        """Returns a list of the single factory if defined, or a random factory from the popDef if not"""
        thisNumSpawns = self.GetRandomNumSpawns()
        # A random-ish delay makes the Helios groups way better
        delayRange = int(100 * self.delayBetweenSpawns / 3)
        
        factoryList = []
        for i in range(thisNumSpawns):
            randomDelay = self.delayBetweenSpawns + random.randint(-delayRange, delayRange) / 100
            if self.popDefObj:
                if not self.popDefObj:
                    raise Exception(f"{self.name} - Tried to get a popDefObj when it has either not been loaded, or None!")
                chosenFactory = self.popDefObj.GetRandomFactory(den, gameStage, rarity)
            else:
                if not self.factoryObj:
                    raise Exception(f"{self.name} - Tried to get a factoryObj when it has either not been loaded, or None!")
                chosenFactory = self.factoryObj

            if chosenFactory:
                if megaMix:
                    # Swap the factory with one from a megaMix pool
                    for pool in self.megaMixPools:
                        if any(chosenFactory.PawnBalanceDefinition is ai for (ai, fact) in pool):
                            (ai, fact) = random.choice(pool)
                            #misc(f"MegaMix - swapping factory {chosenFactory} with {fact}")
                            chosenFactory = fact
                factoryList.append((chosenFactory, self.spawnPointDef, randomDelay))
        return factoryList


    def LoadObjects(self, mapNameLower) -> bool:
        """
        Tries to load the defined PopDef/Factory object for this spawn.
        Also tries to store MegaMix PopDef lists, if enabled.
        If mapNameLower is not None, also checks whether the given map is white/blacklisted for this CustomSpawn.
        Returns whether successful (and therefore usable in the current map).
        """
        if mapNameLower:
            if len(self.map_whitelist) > 0 and mapNameLower not in self.map_whitelist:
                return False
            if len(self.map_blacklist) > 0 and mapNameLower in self.map_blacklist:
                return False
        
        self.factoryObj = None
        allFactories = []
        if self.factory:
            try:
                self.factoryObj = find_object("PopulationFactoryBalancedAIPawn", self.factory)
            except ValueError:
                misc(f"{self.factory} not found in this map.")
                return False
            allFactories = [self.factoryObj]
        elif self.popDef:
            try:
                self.popDefObj = find_object("WillowPopulationDefinition", self.popDef)
            except ValueError:
                misc(f"{self.popDef} not found in this map.")
                return False
            allFactories = list(GetAllFactoriesFromPopDef(self.popDefObj))
            self.factoryObj = [*allFactories][0]  # Assuming all pawns in a factory have the same body tag
            if not self.factoryObj:
                dev_warning(f"{self.popDef} has no factory!")
                return False
        else:
            return False
        
        self.bodyTagObj = GetBodyTagFromFactory(self.factoryObj)
                
        # Store cached megaMix pools relevant to this spawn by comparing AIPawnBalanceDefinitions
        self.megaMixPools = GetMegaMixPoolsFromFactoryList(allFactories)
        return True
    
    
    def DenSupportsSpawn(self, den) -> bool:
        """Checks whether this CustomSpawn can use spawn animations for the given den."""
        if not self.factoryObj:
            raise ValueError(f"A CustomSpawn {self.name} does not have a factory loaded for DenSupportsSpawn!")
        
        for spawn in den.SpawnPoints:
            if not spawn or spawn.Class is not ClassWillowPopulationPoint:    # Some are just base PopulationPoints which don't have a PointDef attr
                continue
            if not spawn.PointDef:
                # No spawn anims at all, but we still can't guarantee these are available to spawn if the player is looking at it.
                if self.spawnPointDef and self.spawnPointDef == "None":
                    return True
                continue
            
            if self.spawnPointDef:
                # If we have given a specific spawn point then just check that
                if self.spawnPointDef == spawn.PointDef.Name:
                    return True
            elif self.bodyTagObj:
                for bodyTag in [animMap.Key for animMap in spawn.PointDef.AnimMap if animMap.Key]:
                    # Check this tag matches the enemy we want to spawn
                    if bodyTag is self.bodyTagObj:
                        return True
            else:
                dev_warning(f"{self.name} - Can't find a BodyTag from {self.factoryObj.PathName(self.factoryObj)} for den {den.PathName(den)}.")
                dev_warning(f"{self.name} - If this pawn actually has BodyTag=None, it needs to use spawnPointDef=\"None\".")
        
        return False
    
    
    def IsInDLC(self, DLC: DLC) -> bool:
        if self.factoryObj:
            return GetDLCFromObject(self.factoryObj) is DLC
        elif self.popDefObj:
            return GetDLCFromObject(self.popDefObj) is DLC
        return False


class PoolSpawn(Spawn):
    """Spawns a number of CustomSpawns randomly picked from a pool of CustomSpawns"""
    def __init__(self, name, tag, numPicks=None, customSpawnList=[], customSpawnWeights=[], spawnPointDef=None, map_whitelist=[], map_blacklist=[]) -> None:
        super().__init__(name, tag, spawnPointDef, map_whitelist, map_blacklist)
        
        self.customSpawnList = customSpawnList
        if customSpawnWeights:
            self.customSpawnWeights = customSpawnWeights
            if len(customSpawnWeights) != len(customSpawnList):
                raise ValueError(f"{name} num weights {len(customSpawnWeights)} don't match num spawns {len(customSpawnList)}!")
        else:
            self.customSpawnWeights = [1 for x in customSpawnList]
        if numPicks:
            self.numSpawn = numPicks
        else:
            self.numSpawn = 1
        self.activeSpawnList = [*self.customSpawnList]
        self.activeSpawnWeights = [*self.customSpawnWeights]
    
    
    def GetNewFactoryList(self, den, gameStage, rarity=1, megaMix=False):
        """Returns the factory list for 'numPicks' randomly chosen CustomSpawns in this PoolSpawn"""
        factoryList = []
        for choice in random.choices(self.activeSpawnList, self.activeSpawnWeights, k=self.numSpawn):
            factoryList = factoryList + choice.GetNewFactoryList(den, gameStage, rarity, megaMix)
        return factoryList
    
    
    def LoadObjects(self, mapNameLower) -> bool:
        """ Loads objects in all CustomSpawns.
        Populates the activeSpawnList with all that could be loaded.
        Returns whether ANY CustomSpawns are loaded.
        """
        self.activeSpawnList = []
        self.activeSpawnWeights = []
        for i, x in enumerate(self.customSpawnList):
            if x.LoadObjects(mapNameLower):
                self.activeSpawnList.append(x)
                self.activeSpawnWeights.append(self.customSpawnWeights[i])
        return len(self.activeSpawnList) > 0
    
    
    def DenSupportsSpawn(self, den) -> bool:
        return any(x.DenSupportsSpawn(den) for x in self.activeSpawnList)


class MultiSpawn(Spawn):
    """Spawns a fixed number of each CustomSpawn"""
    def __init__(self, name, tag, numSpawn=None, customSpawnList=[], spawnPointDef=None, map_whitelist=[], map_blacklist=[]) -> None:
        super().__init__(name, tag, spawnPointDef, map_whitelist, map_blacklist)
        self.minDistance = 2000
        
        self.customSpawnList: List[Spawn] = customSpawnList
        if numSpawn:
            self.numSpawn = numSpawn
        else:
            self.numSpawn = [1 for x in customSpawnList]
    
    
    def GetNewFactoryList(self, den, gameStage, rarity=1, megaMix=False):
        """Returns the factory list combining each CustomSpawn in this MultiSpawn"""
        factoryList = []
        for i, customSpawn in enumerate(self.customSpawnList):
            for j in range(self.numSpawn[i]):
                factoryList = factoryList + customSpawn.GetNewFactoryList(den, gameStage, rarity, megaMix)
        return factoryList
    
    
    def LoadObjects(self, mapNameLower) -> bool:
        if len(self.map_whitelist) > 0 and mapNameLower not in self.map_whitelist:
            return False
        if len(self.map_blacklist) > 0 and mapNameLower in self.map_blacklist:
            return False
        return all(x.LoadObjects(mapNameLower) for x in self.customSpawnList)
    
    
    def DenSupportsSpawn(self, den) -> bool:
        return all(x.DenSupportsSpawn(den) for x in self.customSpawnList)


def CustomSpawnFromPopDef(PopDef: WillowPopulationDefinition) -> CustomSpawn | None:
    if not PopDef:
        return None
    if not PopDef.ActorArchetypeList:
        return None
    
    tag = Tag.CHUMP
    allFactories = list(GetAllFactoriesFromPopDef(PopDef))
    numBadasses = 0
    numChampions = 0
    if len(allFactories) == 0:
        dev_warning(f"{PopDef.PathName(PopDef)} has no factories?!")
        return None
    
    for factory in allFactories:
        if not factory or factory.bIsCriticalActor:
            return None
        if factory.Class is ClassPopulationFactoryWillowVehicle and factory.VehicleArchetype:
            # Tag vehicles as champions so only 1 per spawn
            numChampions = numChampions + 1
            continue
        if not factory.PawnBalanceDefinition:
            return None

        PawnDef = factory.PawnBalanceDefinition
        if PawnDef:
            if PawnDef.Champion:
                numChampions = numChampions + 1
            elif "badass" in PawnDef.PathName(PawnDef).lower():
                numBadasses = numBadasses + 1
    
    if "unique" in PopDef.PathName(PopDef).lower():
        tag = Tag.MINIBOSS
    # Not accounting for sub-popdef chance but whatevs
    elif numChampions > len(allFactories) / 2 or PopDef.Name in POPDEF_TAG_OVERRIDES:
        tag = Tag.ULTIMATE_BADASS
    elif numBadasses > len(allFactories) / 2:
        tag = Tag.BADASS

    numSpawns = [1]     # Default for Unique enemies
    if tag == Tag.CHUMP:
        numSpawns = range(3, 7)
    elif tag == Tag.BADASS:
        numSpawns = range(2, 4)
        
    spawn = CustomSpawn(
        PopDef.Name.removeprefix("PopDef_"),
        tag,
        numSpawns,
        popDef=PopDef.PathName(PopDef)
    )
    spawn.popDefObj = PopDef
    spawn.factoryObj = [x for x in allFactories][0]
    spawn.bodyTagObj = GetBodyTagFromFactory(spawn.factoryObj)
    if not spawn.bodyTagObj:
        spawn.spawnPointDef = "None"
    spawn.megaMixPools = GetMegaMixPoolsFromFactoryList(allFactories)
    return spawn
