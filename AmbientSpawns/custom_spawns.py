import enum
import random
from typing import Dict, List, Set, Tuple
import unrealsdk
from unrealsdk import Log

from Mods.AmbientSpawns import level_packages
from Mods.AmbientSpawns.level_packages import *
from Mods import ModMenu


class Tag(enum.IntEnum):
    CHUMP = enum.auto()
    MEDIUM = enum.auto()    # E.g. WAR loader
    BADASS = enum.auto()
    ULTIMATE_BADASS = enum.auto()   # E.g. Big Boi Loader
    MINIBOSS = enum.auto()
    BOSS = enum.auto()
    _LENGTH = enum.auto()

BadassTagWeights = {
    Tag.CHUMP: 30,
    Tag.MEDIUM: 30,
    Tag.BADASS: 20,
    Tag.ULTIMATE_BADASS: 10,
    Tag.MINIBOSS: 10,
    Tag.BOSS: 3
}
"""Weights for selecting a spawn by Badass Tag"""

megaMixCache: List[List[Tuple[object, object]]] = []  #Tuple[AIPawnBalanceDefinition, PopulationFactoryBalancedAIPawn]

def CacheMegaMixPools():
    global megaMixCache
    megaMixCache = []
    for pool in megaMixSubstitutionPools:
        poolCache = []
        poolBodyTag = None
        for factoryPath in pool:
            # We store the AIDef and a loaded Factory to compare and then use
            factoryObj = unrealsdk.FindObject("PopulationFactoryBalancedAIPawn", factoryPath)
            if not factoryObj:
                #Log(f"MegaMix - Can't find factory {factoryPath}")
                continue
            AIDef = factoryObj.PawnBalanceDefinition
            if AIDef:
                if str(AIDef.Class.Name) != "AIPawnBalanceDefinition":
                    # Is another PopDef instead of an AIDef
                    #Log(f"MegaMix - {factoryPath} does not have an AIPawnBalanceDefinition (probably is another PopDef)")
                    continue
                # Check all body tags match in this pool too
                bodyTag = GetBodyTagFromFactory(factoryObj)
                if poolBodyTag:
                    if bodyTag is not poolBodyTag:
                        #Log(f"MegaMix - {factoryPath} pool has different BodyTags {bodyTag}, {poolBodyTag}")
                        poolBodyTag = poolBodyTag
                else:
                    poolBodyTag = bodyTag
                poolCache.append((AIDef, factoryObj))
        if len(poolCache) > 1:
            megaMixCache.append(poolCache)


# This is how I define all bespoke spawns that aren't using the in-game population points.
# I am choosing to return PopulationFactoryBalancedAIPawns instead of WillowPopulationDefinitions,
#  because not all enemies have a unique PopDef, but they do all have a unique factory.


class Spawn:
    def __init__(self, name:str, tag:Tag, spawnPointDef, map_whitelist:List[str], map_blacklist:List[str]):
        self.name = name
        if tag:
            self.tag = tag
        else:
            self.tag = NullCustomSpawn.tag
        self.delayBetweenSpawns = 0.5
        self.minDistance = 0
        
        self.spawnPointDef = spawnPointDef
        """Specify ONLY spawn points with this WillowPopulationPointDefinition e.g. 'GD_ConstructorShared.Den.PopPointDef_OrbitalDrop'.
         "None" as a string really means None object when we use this."""
        self.map_whitelist = map_whitelist
        self.map_blacklist = map_blacklist
        
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
            self.numSpawns = NullCustomSpawn.numSpawns
            self.numSpawnsWeights = NullCustomSpawn.numSpawnsWeights
        self.minSpawns = min(self.numSpawns)
        self.maxSpawns = max(self.numSpawns)
            
        self.popDef = None
        self.factory = factory
        if not factory:
            if popDef:
                self.popDef = popDef
            else:
                self.popDef = NullCustomSpawn.popDef
        
        self.map_blacklist = []
        self.map_whitelist = []
        
        self.factoryObj = None
        self.popDefObj = None
        self.bodyTagObj = None
        
        self.megaMixPools = []
        
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
                    raise Exception(f"{self.Name} - Tried to get a popDefObj when it has either not been loaded, or None!")
                chosenFactory = self.popDefObj.GetRandomFactory(den, gameStage, rarity)
            else:
                if not self.factoryObj:
                    raise Exception(f"{self.Name} - Tried to get a factoryObj when it has either not been loaded, or None!")
                chosenFactory = self.factoryObj

            if chosenFactory:
                if megaMix:
                    # Swap the factory with one from a megaMix pool
                    for pool in self.megaMixPools:
                        if any(chosenFactory.PawnBalanceDefinition is ai for (ai, fact) in pool):
                            (ai, fact) = random.choice(pool)
                            #Log(f"MegaMix - swapping factory {chosenFactory} with {fact}")
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
            self.factoryObj = unrealsdk.FindObject("PopulationFactoryBalancedAIPawn", self.factory)
            if not self.factoryObj:
                #Log(f"{self.factory} not found in this map.")
                return False
            allFactories = [self.factoryObj]
        else:
            self.popDefObj = unrealsdk.FindObject("WillowPopulationDefinition", self.popDef)
            if not self.popDefObj:
                #Log(f"{self.popDef} not found in this map.")
                return False
            allFactories = GetAllFactoriesFromPopDef(self.popDefObj)
            self.factoryObj = [*allFactories][0]  # Assuming all pawns in a factory have the same body tag
            if not self.factoryObj:
                #Log(f"{self.popDef} has no factory!")
                return False
        
        self.bodyTagObj = GetBodyTagFromFactory(self.factoryObj)
                
        # Store cached megaMix pools relevant to this spawn by comparing AIPawnBalanceDefinitions
        self.megaMixPools = GetMegaMixPoolsFromFactoryList(allFactories)
        return True
    
    def DenSupportsSpawn(self, den) -> bool:
        """Checks whether this CustomSpawn can use spawn animations for the given den."""
        if not self.factoryObj:
            # Log(f"A CustomSpawn {self.name} does not have a factory loaded for DenSupportsSpawn!")
            # return False
            raise ValueError(f"A CustomSpawn {self.name} does not have a factory loaded for DenSupportsSpawn!")
        
        for spawn in den.SpawnPoints:
            if not spawn:
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
            # else:
            #     Log(f"{self.name} - Can't find a BodyTag from {self.factoryObj.PathName(self.factoryObj)} for den {den.PathName(den)}.")
            #     Log(f"{self.name} - If this pawn actually has BodyTag=None, it needs to use spawnPointDef=\"None\".")
        
        return False
    
    def IsInDLC(self, DLC: DLC) -> bool:
        if self.factoryObj:
            return Get_DLC_From_Object(self.factoryObj) is DLC
        elif self.popDefObj:
            return Get_DLC_From_Object(self.popDefObj) is DLC
        return False


def GetAllFactoriesFromPopDef(popDef) -> Set:
        """
        Some PopDefs list PopulationFactoryPopulationDefinition instead of PopulationFactoryBalancedAIPawn.
        We recurse through these to get the actual PopulationFactoryBalancedAIPawns.
        """
        allFactories = set()    # Set to discount any duplicates
        for archetype in popDef.ActorArchetypeList:
            spawnFactory = archetype.SpawnFactory
            if spawnFactory:
                if str(spawnFactory.Class.Name) == "PopulationFactoryBalancedAIPawn":
                    allFactories.add(spawnFactory)
                else:
                    # Could be a PopulationFactoryPopulationDefinition instead
                    if spawnFactory.PopulationDef:
                        allFactories = allFactories.union(GetAllFactoriesFromPopDef(spawnFactory.PopulationDef))
        return allFactories

def GetBodyTagFromFactory(factory):
    AIPawnBalanceDef = factory.PawnBalanceDefinition
    if not AIPawnBalanceDef:
        #Log(f"{factory.PathName(factory)} has no PawnBalanceDefinition.")
        return False
    if not AIPawnBalanceDef.AIPawnArchetype:
        #Log(f"{factory.PathName(factory)} has no AIPawnArchetype.")
        return False
    return AIPawnBalanceDef.AIPawnArchetype.BodyClass.BodyTag

def GetMegaMixPoolsFromFactoryList(allFactories) -> List[Tuple[object, object]]:
    return [pool for pool in megaMixCache if any(x[0] in [f.PawnBalanceDefinition for f in allFactories] for x in pool)]

def CustomSpawnFromPopDef(PopDef) -> CustomSpawn:
    if not PopDef:
        return None
    if not PopDef.ActorArchetypeList:
        return None
    
    tag = Tag.CHUMP
    allFactories = GetAllFactoriesFromPopDef(PopDef)
    numBadasses = 0
    numChampions = 0
    if len(allFactories) == 0:
        #Log(f"{PopDef.PathName(PopDef)} has no factories?!")
        return False

    for factory in allFactories:
        if not factory or factory.bIsCriticalActor or not factory.PawnBalanceDefinition:
            return None
        PawnDef = factory.PawnBalanceDefinition
        if PawnDef:
            if PawnDef.Champion:
                numChampions = numChampions + 1
            elif "badass" in PawnDef.PathName(PawnDef).lower():
                numBadasses = numBadasses + 1
    
    if "unique" in PopDef.PathName(PopDef).lower():
        tag = Tag.MINIBOSS
    elif numChampions > len(allFactories) / 2:  # Not accounting for sub-popdef chance but whatevs
        tag = Tag.ULTIMATE_BADASS
    elif numBadasses > len(allFactories) / 2:
        tag = Tag.BADASS

    numSpawns = [1]     # Default for Unique enemies
    if tag == Tag.CHUMP:
        numSpawns = range(3,7)
    elif tag == Tag.BADASS:
        numSpawns = range(2,4)
        
    spawn = CustomSpawn(
        PopDef.Name,
        tag,
        numSpawns,
        popDef=PopDef.PathName(PopDef)
    )
    spawn.popDefObj = PopDef
    spawn.factoryObj = [x for x in allFactories][0]
    spawn.bodyTagObj = GetBodyTagFromFactory(spawn.factoryObj)
    if not spawn.bodyTagObj:
        spawn.spawnPointDef = "None"
        #Log(f"{PopDef.Name} - No BodyTag in {spawn.factoryObj.PathName(spawn.factoryObj)}")
    spawn.megaMixPools = GetMegaMixPoolsFromFactoryList(allFactories)
    return spawn


class NullCustomSpawn(CustomSpawn):
    map_whitelist: List[str] = []
    map_blacklist: List[str] = []
    
    minSpawns: int = 1
    maxSpawns: int = 1
    numSpawns: List[int] = [1]
    numSpawnsWeights: List[int] = [1]
    delayBetweenSpawns = 0.1
    
    name: str = "Default"
    tag: Tag = Tag.CHUMP
    popDef = "GD_Explosives.Populations.Pop_BarrelMixture"
    factory = "GD_Explosives.Populations.Pop_BarrelMixture:PopulationFactoryInteractiveObject_1"


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
            self.customSpawnWeights = [BadassTagWeights[x.tag] for x in customSpawnList]
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


customList: Dict[ModMenu.Game, Dict[str, List[Spawn]]] = {
    ModMenu.Game.BL2: {
        DLC.BL2: [
            # Bandit
            CustomSpawn("A butt-load of midgets",Tag.CHUMP,range(8,15),[4,5,5,3,2,1,1],popDef="GD_Population_Midget.Population.PopDef_MidgetMix_Regular"),
            CustomSpawn("Bruisers",Tag.CHUMP,range(1,4),popDef="GD_Population_Bruiser.Population.PopDef_Bruiser"),
            CustomSpawn("More-rauders",Tag.CHUMP,range(3,7),[2,3,2,1],popDef="GD_Population_Marauder.Population.PopDef_MarauderMix_Regular"),
            
            CustomSpawn("Watch Out! Badass Psychos!",Tag.ULTIMATE_BADASS,range(2,4),[3,2],popDef="GD_Population_Psycho.Population.PopDef_PsychoBadass"),
            CustomSpawn("Badass Marauders",Tag.ULTIMATE_BADASS,range(2,5),[3,3,1],popDef="GD_Population_Bandit.Population.PopDef_BanditBadassMix"),
            
            MultiSpawn("Nomad Commander",Tag.BADASS,customSpawnList=[
                CustomSpawn("Big Nomad",Tag.CHUMP,              popDef="GD_Population_Nomad.Population.PopDef_Nomad_Taskmaster"),
                CustomSpawn("Minions1",Tag.CHUMP,range(3,4),    popDef="GD_Population_Marauder.Population.PopDef_MarauderGrunt"),
                CustomSpawn("Minions2",Tag.CHUMP,range(2,4),    popDef="GD_Population_Marauder.Population.PopDef_Marauder"),
            ]),
            MultiSpawn("Goliath & Friends",Tag.BADASS,customSpawnList=[
                CustomSpawn("Big Goliath",Tag.BADASS,           popDef="GD_Population_Goliath.Population.PopDef_GoliathBadass"),
                CustomSpawn("Minions1",Tag.CHUMP,range(3,4),    popDef="GD_Population_Marauder.Population.PopDef_MarauderMix_Regular"),
                CustomSpawn("Minions2",Tag.CHUMP,range(2,4),    popDef="GD_Population_Midget.Population.PopDef_MidgetMix_Regular"),
            ]),
            MultiSpawn("Friend & Goliaths",Tag.BADASS,customSpawnList=[
                CustomSpawn("Friend",Tag.CHUMP,                     popDef="GD_Population_Midget.Population.PopDef_MidgetBadass"),
                CustomSpawn("Goliaths",Tag.MEDIUM,[1,2,3],[2,2,1],  popDef="GD_Population_Goliath.Population.PopDef_GoliathMix_Regular"),
                CustomSpawn("Big Goliath",Tag.BADASS,               popDef="GD_Population_Goliath.Population.PopDef_GoliathTurret"),
            ]),
            MultiSpawn("BBQ Time",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Pyro",Tag.CHUMP,                   factory="GD_Population_Bandit.Population.PopDef_BanditMix_Ice_IceCanyon:PopulationFactoryBalancedAIPawn_3"),
                CustomSpawn("Midgets",Tag.CHUMP,range(2,5),     popDef="GD_Population_Midget.Population.PopDef_FlamingMidget"),
                CustomSpawn("Fireburn Mix",Tag.CHUMP,range(1,4),popDef="GD_Population_Bandit.Population.PopDef_BanditMix_Ice_IceCanyon"),
            ]),
            
            PoolSpawn("Bandit Minibosses",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Doc Mercy",Tag.MINIBOSS,popDef="GD_Population_Nomad.Population.Unique.PopDef_MrMercy", map_blacklist=["frost_p"]),
                CustomSpawn("Mad Mike 'boutta ruin your day",Tag.MINIBOSS,popDef="GD_Population_Nomad.Population.Unique.PopDef_MadMike", map_blacklist=["dam_p"]),
                CustomSpawn("Prospector",Tag.MINIBOSS,popDef="GD_Population_Nomad.Population.Unique.PopDef_Prospector", map_blacklist="tundraexpress_p"),
                MultiSpawn("Assassin Tagteam",Tag.BOSS,customSpawnList=[
                    CustomSpawn("Ass Wot",Tag.MINIBOSS,     popDef="GD_Population_Marauder.Population.Unique.PopDef_Assassin1"),
                    CustomSpawn("Ass Oney",Tag.MINIBOSS,    popDef="GD_Population_Nomad.Population.Unique.PopDef_Assassin2"),
                    CustomSpawn("Ass Reeth",Tag.MINIBOSS,   popDef="GD_Population_Psycho.Population.Unique.PopDef_Assassin3"),
                    CustomSpawn("Ass Rouf",Tag.MINIBOSS,    popDef="GD_Population_Rat.Population.Unique.PopDef_Assassin4"),
                ], map_blacklist=["southpawfactory_p"]),    # Not allowed where they spawn normally
                MultiSpawn("Deputy Winger",Tag.MINIBOSS,customSpawnList=[
                    CustomSpawn("Deputy",Tag.MINIBOSS,      popDef="GD_Population_Sheriff.Population.Pop_Deputy"),
                    CustomSpawn("Marshals",Tag.CHUMP,[4,5], popDef="GD_Population_Sheriff.Population.Pop_Marshal"),
                ], map_blacklist=["grass_lynchwood_p"]),
            ], customSpawnWeights=[2,2,2,1,2]),

            # Rats
            MultiSpawn("Mine Rats",Tag.CHUMP,customSpawnList=[
                CustomSpawn("Tunnel Rats",Tag.CHUMP,range(2,4),     factory="GD_Population_Bandit.Population.PopDef_BanditMix_Lynchwood_RatMiners:PopulationFactoryBalancedAIPawn_6"),
                CustomSpawn("Miner Rat Mix",Tag.CHUMP,range(2,5),   popDef="GD_Population_Bandit.Population.PopDef_BanditMix_Lynchwood_RatMiners"),
            ]),
            MultiSpawn("Laney & Co.",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Laney",Tag.MINIBOSS,   popDef="GD_Population_Rat.Population.Unique.PopDef_Laney"),
                CustomSpawn("Dwarf1",Tag.MINIBOSS,  popDef="GD_Population_Midget.Population.Unique.PopDef_LaneyDwarf1"),
                CustomSpawn("Dwarf2",Tag.MINIBOSS,  popDef="GD_Population_Midget.Population.Unique.PopDef_LaneyDwarf2"),
                CustomSpawn("Dwarf3",Tag.MINIBOSS,  popDef="GD_Population_Midget.Population.Unique.PopDef_LaneyDwarf3"),
                CustomSpawn("Dwarf4",Tag.MINIBOSS,  popDef="GD_Population_Midget.Population.Unique.PopDef_LaneyDwarf4"),
                CustomSpawn("Dwarf5",Tag.MINIBOSS,  popDef="GD_Population_Midget.Population.Unique.PopDef_LaneyDwarf5"),
                CustomSpawn("Dwarf6",Tag.MINIBOSS,  popDef="GD_Population_Midget.Population.Unique.PopDef_LaneyDwarf6"),
                CustomSpawn("Dwarf7",Tag.MINIBOSS,  popDef="GD_Population_Midget.Population.Unique.PopDef_LaneyDwarf7")
            ], map_blacklist=["fridge_p"]),
            MultiSpawn("TMNR",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Dan",Tag.MINIBOSS,                 popDef="GD_Population_Rat.Population.Unique.PopDef_RatDan"),
                CustomSpawn("Lee",Tag.MINIBOSS,                 popDef="GD_Population_Rat.Population.Unique.PopDef_RatLee"),
                CustomSpawn("Mick",Tag.MINIBOSS,                popDef="GD_Population_Rat.Population.Unique.PopDef_RatMick"),
                CustomSpawn("Ralph",Tag.MINIBOSS,               popDef="GD_Population_Rat.Population.Unique.PopDef_RatRalph"),
                CustomSpawn("Flinter",Tag.MINIBOSS,[0,1],[2,1], popDef="GD_Population_Rat.Population.Unique.PopDef_RatEasterEgg")
            ], map_blacklist=["dam_p"]),
            
            # Hyperion
            CustomSpawn("Helios ATTACKS!",Tag.MEDIUM,range(8,15),popDef="GD_Population_Loader.Population.PopDef_LoaderMix_Regular",spawnPointDef="PopPointDef_OrbitalDrop"),
            MultiSpawn("Helios ATTACKS AGAIN (because it's cool)",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("RPG",Tag.CHUMP,[2,3],[1,1],    popDef="GD_Population_Loader.Population.PopDef_LoaderRPG"),
                CustomSpawn("SGT",Tag.CHUMP,[2,3],[1,1],    popDef="GD_Population_Loader.Population.PopDef_LoaderSGT"),
                CustomSpawn("WAR",Tag.MEDIUM,[1,2],[4,1],   popDef="GD_Population_Loader.Population.PopDef_LoaderWAR"),
            ]),
            CustomSpawn("Helios ATTACKS - Bunker Mix",Tag.MEDIUM,range(6,13),popDef="GD_Population_Loader.Population.PopDef_LoaderMix_BunkerFight",spawnPointDef="PopPointDef_OrbitalDrop"),
            CustomSpawn("Lookout! Badass Loaders",Tag.BADASS,[2,3,4],[7,4,1],popDef="GD_Population_Loader.Population.PopDef_LoaderBadass"),
            CustomSpawn("Big Boi Loader",Tag.ULTIMATE_BADASS,[1,2],[4,1],popDef="GD_Population_Loader.Population.PopDef_LoaderSuperBadass"),
            CustomSpawn("EXPlooooosions",Tag.CHUMP,range(5,11),[1,2,3,3,2,2],popDef="GD_Population_Loader.Population.PopDef_LoaderEXP"),
            CustomSpawn("LEEEEROYYYYY",Tag.BOSS,factory="GD_Population_Midget.Population.LootMidget.PopDef_LootMidget_HyperionMix:PopulationFactoryBalancedAIPawn_5",spawnPointDef="None"),
            MultiSpawn("Loaders+Surveyors",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Loaders",Tag.CHUMP,range(3,7),             popDef="GD_Population_Loader.Population.PopDef_LoaderMix_Military"),
                CustomSpawn("Badass Surveyor",Tag.BADASS,[1,2],[2,1],   popDef="GD_Population_Probe.Population.PopDef_ProbeMix_Badass"),
                CustomSpawn("Surveyors",Tag.CHUMP,range(2,5),           popDef="GD_Population_Probe.Population.PopDef_ProbeMix_Regular"),
            ]),
            MultiSpawn("Loaders+Engis",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Loaders",Tag.CHUMP,range(4,7),     popDef="GD_Population_Loader.Population.PopDef_LoaderMix_Regular"),
                CustomSpawn("EngiArms",Tag.CHUMP,range(1,3),    popDef="GD_Population_Engineer.Population.PopDef_EngineerArms"),
                CustomSpawn("EngiFleshy",Tag.CHUMP,range(1,3),  popDef="GD_Population_Engineer.Population.PopDef_Engineer"),
            ]),
            MultiSpawn("BlackOps",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Snipers",Tag.CHUMP,range(2,4),     popDef="GD_Population_Engineer.Population.PopDef_BlackOps"),
                CustomSpawn("Cloakers",Tag.CHUMP,range(2,4),    popDef="GD_Population_Engineer.Population.PopDef_HyperionInfiltrator"),
            ]),
            MultiSpawn("Assault",Tag.MEDIUM,customSpawnList=[
                # Soldier needs allegiance to match the turrets so no den change
                CustomSpawn("Soldier",Tag.CHUMP,range(2,4),     popDef="GD_Population_Engineer.Population.PopDef_HyperionSoldier"),
                CustomSpawn("Rockets",Tag.CHUMP,range(1,3),     factory="GD_Population_Hyperion.Population.PopDef_HyperionMix_Fyrestone:PopulationFactoryBalancedAIPawn_4"),
            ]),
            MultiSpawn("Flying enemies are fun",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Jets",Tag.CHUMP,range(3,5),        popDef="GD_Population_Loader.Population.PopDef_LoaderJET"),
                CustomSpawn("Surveyors",Tag.CHUMP,range(2,5),   popDef="GD_Population_Probe.Population.PopDef_ProbeMix_Regular")
            ]),
            CustomSpawn("Wilhelm",Tag.BOSS,factory="GD_Population_Loader.Population.Unique.PopDef_Willhelm:PopulationFactoryBalancedAIPawn_1",spawnPointDef="None",map_blacklist=["tundratrain_p"]),
            
            # Fauna - some just basic mixes to pad so not only custom minibosses
            # Rakk attacks don't work in other maps for some reason
            #CustomSpawn("Release the Rakk!",Tag.CHUMP,[4,8],popDef="GD_Population_Rakk.Population.PopDef_Rakk",spawnPointDef="None"),
            #CustomSpawn("Skag Mix",Tag.CHUMP,range(4,7),popDef="GD_Population_Skag.Population.PopDef_SkagMix_Regular"),
            #CustomSpawn("Bullymong Mix",Tag.CHUMP,range(4,7),popDef="GD_Population_PrimalBeast.Population.PopDef_PrimalBeastMix_Ash"),
            MultiSpawn("Thresher Mix",Tag.CHUMP,customSpawnList=[
                CustomSpawn("Threshers",Tag.CHUMP,range(4,7),   popDef="GD_Population_Thresher.Population.PopDef_ThresherMix_Regular"),
                CustomSpawn("Tentacles",Tag.CHUMP,range(4,7),   popDef="GD_Population_Thresher.Population.PopDef_TentacleMix_Regular")
            ]),
            CustomSpawn("Spiderant Mix",Tag.CHUMP,range(4,7),popDef="GD_Population_SpiderAnt.Population.PopDef_SpiderantMix_Regular"),
            CustomSpawn("Sponics",Tag.CHUMP,range(3,7),factory="GD_Population_SpiderAnt.Population.PopDef_SpiderantMix_Regular:PopulationFactoryBalancedAIPawn_2"),
            PoolSpawn("Stalker Mix",Tag.MEDIUM,numPicks=4,customSpawnList=[
                CustomSpawn("Stalker",Tag.CHUMP,[1,2],          popDef="GD_Population_Stalker.Population.PopDef_Stalker"),
                CustomSpawn("Badass",Tag.BADASS,[1],            popDef="GD_Population_Stalker.Population.PopDef_StalkerBadass"),
                CustomSpawn("Ambush",Tag.ULTIMATE_BADASS,[1],   popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Ambush"),
                CustomSpawn("Cyclone",Tag.MEDIUM,[1,2],         popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Cyclone"),
                CustomSpawn("Stalker",Tag.CHUMP,[1,2],          popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Needle"),
                CustomSpawn("Spring",Tag.CHUMP,[1,2],           popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Spring"),
            ], customSpawnWeights=[3,1,1,4,3,3]),
            
            MultiSpawn("Skag Ma & Pa",Tag.BADASS,customSpawnList=[
                CustomSpawn("Badass",Tag.BADASS,[2],        popDef="GD_Population_Skag.Population.PopDef_SkagMix_Badass"),
                CustomSpawn("Pups",Tag.CHUMP,range(4,10),   popDef="GD_Population_Skag.Population.PopDef_SkagPup")
            ]),
            PoolSpawn("Creepers",Tag.MINIBOSS,numPicks=3,customSpawnList=[
                CustomSpawn("Badass Creeper",Tag.MINIBOSS,[1],     popDef="GD_Population_Creeper.Population.PopDef_CreeperBadass",spawnPointDef="None"),
                CustomSpawn("Normal Creeper",Tag.MINIBOSS,[1,2],   popDef="GD_Population_Creeper.Population.PopDef_Creeper",spawnPointDef="None"),
            ], customSpawnWeights=[1,3], spawnPointDef="None"),
            
            MultiSpawn("Terramorphous Peek",Tag.BOSS,customSpawnList=[
                CustomSpawn("Spikes",Tag.MINIBOSS,[1,2],[3,1],  popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidA",spawnPointDef="None"),
                CustomSpawn("Rock",Tag.MINIBOSS,[1,2],[3,1],    popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidC",spawnPointDef="None"),
                CustomSpawn("Beam",Tag.MINIBOSS,[1,2],[3,1],    popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidD",spawnPointDef="None"),
                CustomSpawn("Masher",Tag.MINIBOSS,[1,2],[3,1],  popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidE",spawnPointDef="None"),
            ], spawnPointDef="None"),
            CustomSpawn("Terramorphous Peek Fire",Tag.BOSS,[3,4,5],[2,3,1],popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidF",spawnPointDef="None"),
    
            # None PointDef padding (so we don't get too many boss spawns here)
            CustomSpawn("FOV Stalker",Tag.CHUMP,range(2,4),popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Cyclone",spawnPointDef="None"),
            CustomSpawn("FOV Thresher",Tag.CHUMP,range(2,4),popDef="GD_Population_Thresher.Population.PopDef_ThresherMix_Regular",spawnPointDef="None"),
        ],
        
        DLC.Scarlett: [
            # Sandworms just don't work outside of terrain they usually appear :/
            # MultiSpawn("Sandworm Ambush",Tag.CHUMP,customSpawnList=[
            #     CustomSpawn("Queen",Tag.MEDIUM,             popDef="GD_Orchid_Pop_SandWorm.Population.PopDef_Orchid_SandWormQueen",spawnPointDef="None"),
            #     CustomSpawn("Worms",Tag.CHUMP,range(2,6),   popDef="GD_Orchid_Pop_SandWorm.Population.PopDef_Orchid_SandWorm",spawnPointDef="None"),
            # ],spawnPointDef="None",map_whitelist=["Orchid_OasisTown_P","Orchid_SaltFlats_P"]),
            # CustomSpawn("Rakk Hive - Outta Nowhere!",Tag.BOSS,popDef="GD_Orchid_Pop_RakkHive.Character.PopDef_Orchid_RakkHive",spawnPointDef="None"),
            PoolSpawn("Avast or we'll blast ya",Tag.CHUMP,numPicks=6,customSpawnList=[
                CustomSpawn("Captain",Tag.BADASS,   popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateCaptain"),
                CustomSpawn("Cursed",Tag.MEDIUM,    popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateCursed"),
                CustomSpawn("Grenadier",Tag.CHUMP,  popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateGrenadier"),
                CustomSpawn("Hunter",Tag.CHUMP,     popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateHunter"),
                CustomSpawn("Marauder",Tag.CHUMP,   popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateMarauder"),
                CustomSpawn("Ninja",Tag.CHUMP,      popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateNinja"),
                CustomSpawn("Psycho",Tag.CHUMP,     popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PiratePsycho"),
            ], customSpawnWeights=[2,3,5,5,5,5,5]),
            MultiSpawn("Pirate Raiding Party",Tag.MEDIUM,customSpawnList=[
                PoolSpawn("Large Lad",Tag.BADASS,customSpawnList=[
                    CustomSpawn("Anchorman",Tag.BADASS, popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_AnchorMan"),
                    CustomSpawn("Whaler",Tag.BADASS,    factory="GD_Orchid_Pop_Pirates.MapPopulations.PopDef_Orchid_SpireMix:PopulationFactoryBalancedAIPawn_12"),
                    CustomSpawn("Minelayer",Tag.BADASS, factory="GD_Orchid_Pop_Pirates.MapPopulations.PopDef_Orchid_SpireMix:PopulationFactoryBalancedAIPawn_14"),
                    CustomSpawn("Buccaneer",Tag.MEDIUM, popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_SwordMan"),
                ]),
                PoolSpawn("Chumps",Tag.CHUMP,numPicks=4,customSpawnList=[
                    CustomSpawn("Captain",Tag.BADASS,   popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateCaptain"),
                    CustomSpawn("Cursed",Tag.MEDIUM,    popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateCursed"),
                    CustomSpawn("Grenadier",Tag.CHUMP,  popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateGrenadier"),
                    CustomSpawn("Hunter",Tag.CHUMP,     popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateHunter"),
                    CustomSpawn("Marauder",Tag.CHUMP,   popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateMarauder"),
                    CustomSpawn("Ninja",Tag.CHUMP,      popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateNinja"),
                    CustomSpawn("Psycho",Tag.CHUMP,     popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PiratePsycho"),
                ], customSpawnWeights=[2,3,5,5,5,5,5])
            ]),
            MultiSpawn("Would you kindly harvest this midget",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Mr Bubbles",Tag.MINIBOSS,  popDef="GD_Orchid_Pop_BubblesLilSis.Population.PopDef_Orchid_Bubbles"),
                CustomSpawn("Little Sis",Tag.MINIBOSS,  popDef="GD_Orchid_Pop_BubblesLilSis.Population.PopDef_Orchid_LittleSis"),
            ], map_blacklist=["Orchid_Spire_P"]),
            MultiSpawn("Scarlett Crew",Tag.ULTIMATE_BADASS,customSpawnList=[
                CustomSpawn("Lt. White",Tag.BADASS,         popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Orchid_PirateHenchman"),
                CustomSpawn("Lt. Hoffman",Tag.BADASS,       popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Orchid_PirateHenchman2"),
                CustomSpawn("Crew",Tag.MEDIUM,range(1,4),   popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Betrayal_Mix"),
                CustomSpawn("Ninjas",Tag.MEDIUM,range(1,3), popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Orchid_ScarlettNinja"),
            ], map_blacklist=["Orchid_Spire_P"])
        ],
        
        DLC.Torgue: [
            CustomSpawn("Torgue Loaders",Tag.MEDIUM,range(3,7),popDef="GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge"),
            MultiSpawn("Arena Goliath & Friends",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Goliath",Tag.MEDIUM,[1,2],[2,1],   popDef="GD_Iris_Population_Goliath.Population.PopDef_Iris_ArenaGoliath"),
                CustomSpawn("Psychos",Tag.CHUMP,range(0,2),     popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerMidget_Torgue"),
                CustomSpawn("Midgets",Tag.CHUMP,range(1,3),     popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Torgue"),
            ]),
            MultiSpawn("Mommas Gang",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Enforcer",Tag.MEDIUM,[1,2],[2,1],  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBiker_Angels"),
                CustomSpawn("Angel Mix",Tag.MEDIUM,range(2,6),  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Gang_AngelsMix"),
            ]),
            MultiSpawn("Burner Gang",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Enforcer",Tag.MEDIUM,[1,2],[2,1],  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBiker_Dragon"),
                CustomSpawn("Demon Mix",Tag.MEDIUM,range(2,6),  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Gang_DragonMix"),
            ]),
            MultiSpawn("Torgue Gang",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Enforcer",Tag.MEDIUM,[1,2],[2,1],  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBiker_Torgue"),
                CustomSpawn("Torgue Mix",Tag.MEDIUM,range(2,6), popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Gang_TorgueMix"),
            ]),
        ],
        
        DLC.Hammerlock: [
            CustomSpawn("Elite Savages",Tag.ULTIMATE_BADASS,[2,3,4],[1,2,2],popDef="GD_Sage_Pop_Natives.Population.PopDef_Native_Elite"),
            CustomSpawn("Spore Pinata Party",Tag.CHUMP,[3,4,5],popDef="GD_Sage_Pop_Spore.Population.PopDef_Sage_GiantSpore_Mix",spawnPointDef="None"),
            MultiSpawn("FOV Scaylions",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Champion",Tag.BADASS,      popDef="GD_Sage_Pop_Scaylion.Population.PopDef_Sage_ScaylionMix_Champion",spawnPointDef="None"),
                CustomSpawn("Mix",Tag.CHUMP,range(2,5), popDef="GD_Sage_Pop_Scaylion.Population.PopDef_Sage_ScaylionMix_Regular",spawnPointDef="None"),
            ], spawnPointDef="None"),
            MultiSpawn("FOV Boraks",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Badass",Tag.BADASS,        popDef="GD_Sage_Pop_Rhino.Population.PopDef_RhinoMix_Badass",spawnPointDef="None"),
                CustomSpawn("Baby",Tag.CHUMP,range(2,5), popDef="GD_Sage_Pop_Rhino.Population.PopDef_Sage_RhinoBaby",spawnPointDef="None"),
            ], spawnPointDef="None")
        ],
        
        DLC.DragonKeep: [
            # Orcs
            CustomSpawn("Handsome Tower ATTACKS!",Tag.MEDIUM,range(6,15),popDef="GD_Aster_Pop_Orcs.Population.PopDef_OrcsDen_Regular",spawnPointDef="PopPointDef_Orc_OrbitalDrop"),
            CustomSpawn("Orcsplooooosions",Tag.CHUMP,range(5,11),[1,2,3,3,2,2],popDef="GD_Aster_Pop_Orcs.Population.PopDef_OrcsDen_Kamikaze"),
            MultiSpawn("Orc Warlord Party",Tag.ULTIMATE_BADASS,customSpawnList=[
                PoolSpawn("Warlord",Tag.ULTIMATE_BADASS,customSpawnList=[
                    #CustomSpawn("Grug",Tag.ULTIMATE_BADASS,popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_WarlordGrug"),
                    CustomSpawn("Slog",Tag.ULTIMATE_BADASS,popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_WarlordSlog"),
                    CustomSpawn("Turge",Tag.ULTIMATE_BADASS,popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_WarlordTurge")
                ]),
                CustomSpawn("Grunts",Tag.CHUMP,range(2,6),popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_Grunt"),
                CustomSpawn("Bashers",Tag.CHUMP,range(1,4),popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_Basher"),
                CustomSpawn("Zerkers",Tag.MEDIUM,range(0,3),popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orczerker"),
            ]),
            # Spiders
            MultiSpawn("Arachne Hunting Party",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Reapers",Tag.MEDIUM,range(4,8),    popDef="GD_Aster_Pop_Spiders.Population.PopDef_Arachne"),
                CustomSpawn("Minions",Tag.CHUMP,range(4,8),     popDef="GD_Aster_Pop_Spiders.Population.PopDef_SpiderDen_Regular")
            ]),
            # CBA load Dark Forest and fix stumpy materials just for this
            #CustomSpawn("Pixie",Tag.BOSS,popDef="GD_Aster_Pop_Wisp.Population.PopDef_Aster_Wisp",spawnPointDef="None"),
            # Knights
            MultiSpawn("Target Practise",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Badass Archer",Tag.BADASS,popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_BadassFireArcher"),
                CustomSpawn("Archers",Tag.CHUMP,range(2,5),popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_Archer")
            ]),
            MultiSpawn("Paladins",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Paladins",Tag.MEDIUM,[3],popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_Paladin"),
                CustomSpawn("Chumps",Tag.CHUMP,range(3,7),popDef="GD_Aster_Pop_Knights.Population.PopDef_KnightsDen_Regular")
            ]),
            CustomSpawn("It's time to CLEAN THE FLOOR WITH YOU",Tag.BOSS,range(5,11),popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_Broomstick",spawnPointDef="None"),
            # Skeletons
            MultiSpawn("Immortals",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Immortal",Tag.MEDIUM,[3],popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonImmortal"),
                PoolSpawn("Distractions",Tag.CHUMP,numPicks=4,customSpawnList=[
                    CustomSpawn("Skellys",Tag.CHUMP,popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonCrystal"),
                    CustomSpawn("Suiciders",Tag.CHUMP,popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonSuicide"),
                    CustomSpawn("Crystals",Tag.CHUMP,popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonCrystal"),
                    CustomSpawn("Warriors",Tag.CHUMP,popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonWarrior")
                ])
            ]),
            PoolSpawn("Skeleton King",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Aliah",Tag.MINIBOSS,   popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonKing_Aliah"),
                CustomSpawn("Crono",Tag.MINIBOSS,   popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonKing_Crono"),
                CustomSpawn("Nazar",Tag.MINIBOSS,   popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonKing_Nazar"),
                CustomSpawn("Seth",Tag.MINIBOSS,    popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonKing_Seth")
            ], map_blacklist="Dead_Forest_P"),
            # Wizards
            CustomSpawn("Wizards",Tag.MEDIUM,[2,3],[3,1],popDef="GD_Aster_Pop_Wizards.Population.PopDef_WizardsDen_Regular"),
            CustomSpawn("AbracaMAGIC",Tag.BADASS,popDef="GD_Aster_Pop_Wizards.Population.PopDef_WizardsDen_Badass"),
            # MultiSpawn("Familial Reconciliation",Tag.MINIBOSS,customSpawnList=[
            #     CustomSpawn("Edgar",Tag.MINIBOSS,popDef="GD_Aster_Pop_Wizards.Population.PopDef_Wizard_DeadBrotherEdgar"),
            #     CustomSpawn("Simon",Tag.MINIBOSS,popDef="GD_Aster_Pop_Wizards.Population.PopDef_Wizard_DeadBrotherSimon"),
            # ]),
            # Mines
            CustomSpawn("Dwarfzerkers",Tag.CHUMP,range(4,7),popDef="GD_Aster_Pop_Dwarves.Population.PopDef_Dwarfzerker"),
            MultiSpawn("Golem Wranglers",Tag.MEDIUM,customSpawnList=[
                PoolSpawn("Golem Choice",Tag.MEDIUM,customSpawnList=[
                    CustomSpawn("Golem",Tag.MEDIUM,         popDef="GD_Aster_Pop_Golems.Population.PopDef_GolemRock",spawnPointDef="None"),
                    CustomSpawn("Badass Golem",Tag.BADASS,  popDef="GD_Aster_Pop_Golems.Population.PopDef_Golem_Badass",spawnPointDef="None"),
                ], customSpawnWeights=[2,1], spawnPointDef="None"),
                CustomSpawn("Dwarfs",Tag.CHUMP,range(3,6),  popDef="GD_Aster_Pop_Dwarves.Population.PopDef_DwarfsDen_Regular",spawnPointDef="None"),
                CustomSpawn("Badass Dwarf",Tag.BADASS,[0,1],popDef="GD_Aster_Pop_Dwarves.Population.PopDef_Dwarf_Badass",spawnPointDef="None")
            ], spawnPointDef="None"),
            CustomSpawn("Flying Golems",Tag.MEDIUM,range(2,5),popDef="GD_Aster_Pop_Golems.Population.PopDef_GolemFlying"),
            CustomSpawn("Maxibillion",Tag.MINIBOSS,popDef="GD_Aster_Pop_Golems.Population.PopDef_GolemFlying_Maxibillion"),
        ],
        
        DLC.FFS: [
            CustomSpawn("Sanctuary ATTACKS!",Tag.MEDIUM,range(4,11),popDef="GD_Anemone_InfectedPodTendril.Population.PopDef_InfectedPodTendril",spawnPointDef="PopPointDef_OrbitalDrop_Infection_Test"),
            MultiSpawn("Golem Skag Walking Service",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Golem",Tag.BADASS,popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedGolem_Badass",spawnPointDef="None"),
                CustomSpawn("Skags",Tag.CHUMP,range(3,6),popDef="GD_Anemone_Pop_WildLife.Population.PopDef_Infected_SkagMIX",spawnPointDef="None"),
            ], spawnPointDef="None"),
            PoolSpawn("Sentient Mutating Funguys In My Grill",Tag.MEDIUM,numPicks=4,customSpawnList=[
                CustomSpawn("Bruisers",Tag.MEDIUM,[1,2],    popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedBruiser"),
                CustomSpawn("Psychos",Tag.CHUMP,[1,2],      popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedCurse"),
                CustomSpawn("Suiciders",Tag.CHUMP,[1,2],    popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedCurse"),
                CustomSpawn("Midgets",Tag.CHUMP,[1,2],      popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedMidget"),
                CustomSpawn("Goliath",Tag.MEDIUM,[1],       popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedGoliath"),
            ], customSpawnWeights=[3,3,2,3,1]),
            PoolSpawn("New Pandora Chumps",Tag.MEDIUM,numPicks=4,customSpawnList=[
                CustomSpawn("Flamer",Tag.CHUMP,[1,2],       factory="GD_Anemone_Pop_NP.Population.PopDef_NewPandoraMix_Basic:PopulationFactoryBalancedAIPawn_4"),
                CustomSpawn("Commander",Tag.MEDIUM,[1,2],   popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Commander"),
                CustomSpawn("Enforcer",Tag.CHUMP,[1,2],     popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Enforcer"),
                CustomSpawn("Recruit",Tag.CHUMP,[1,2,3],    popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Enlisted"),
                CustomSpawn("Infecto",Tag.CHUMP,[1],        factory="GD_Anemone_Pop_NP.Population.PopDef_NewPandoraMIX_Supports:PopulationFactoryBalancedAIPawn_5"),
                CustomSpawn("Medic",Tag.CHUMP,[1],          popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Medic"),
                CustomSpawn("Sniper",Tag.CHUMP,[1,2],       popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_sniper"),
            ], customSpawnWeights=[3,1,3,3,3,1,2]),
            MultiSpawn("New Pandora Lieutenant Squad",Tag.MINIBOSS,customSpawnList=[
                PoolSpawn("Lieutenant",Tag.MINIBOSS,customSpawnList=[
                    CustomSpawn("Angvar",Tag.MINIBOSS,  popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Lt_Angvar"),
                    CustomSpawn("Bolson",Tag.MINIBOSS,  popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Lt_Bolson"),
                    CustomSpawn("Hoffman",Tag.MINIBOSS, popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Lt_Hoffman"),
                    CustomSpawn("Tetra",Tag.MINIBOSS,   popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Lt_Tetra"),
                ]),
                CustomSpawn("Grunts",Tag.CHUMP,range(3,6),popDef="GD_Anemone_Pop_NP.Population.PopDef_NewPandoraMIX_Grunts"),
            ]),
            MultiSpawn("Dark Web",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Dark Web",Tag.MINIBOSS,popDef="GD_Anemone_A_Queen_Digi.Population.PopDef_Anemone_TheDarkWeb"),
                CustomSpawn("Minions",Tag.CHUMP,[4],popDef="GD_Anemone_DarkWeb_Minions.Population.PopDef_Anemone_DarkWeb_Minions"),
            ], map_blacklist=["OldDust_P"]),
            CustomSpawn("Cassius",Tag.BOSS,popDef="GD_Anemone_Pop_Cassius.GD_Anemone_PopDef_Cassius",spawnPointDef="None",map_blacklist=["ResearchCenter_P"]),
            
            CustomSpawn("FOV Infected Pods",Tag.MEDIUM,range(3,8),popDef="GD_Anemone_InfectedPodTendril.Population.PopDef_InfectedPodTendril",spawnPointDef="None"),
        ],
        
        DLC.Headhunters: [
            MultiSpawn("Send It, Chefs",Tag.ULTIMATE_BADASS,customSpawnList=[
                PoolSpawn("ButcherBoss",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Gouda Remsay",Tag.ULTIMATE_BADASS, popDef="GD_ButcherBoss.Balance.PopDef_ButcherBoss"),
                    CustomSpawn("Brulee",Tag.ULTIMATE_BADASS,       popDef="GD_ButcherBoss2.Balance.PopDef_ButcherBoss2"),
                    CustomSpawn("Bork Bork",Tag.ULTIMATE_BADASS,    popDef="GD_ButcherBoss3.Balance.PopDef_ButcherBoss3"),
                    CustomSpawn("Rat Chef",Tag.ULTIMATE_BADASS,     popDef="GD_RatChef.Balance.PopDef_RatChef")
                ]),
                CustomSpawn("Butchers",Tag.CHUMP,range(3,6),popDef="GD_Butcher.Balance.PopDef_Butcher")
            ], map_blacklist=["Hunger_P"]),
            PoolSpawn("Tribute Pair",Tag.ULTIMATE_BADASS,customSpawnList=[
                MultiSpawn("Tributes of Sawtooth",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_CraterFemale.Balance.PopDef_CraterFemale"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_CraterMale.Balance.PopDef_CraterMale")
                ]),
                MultiSpawn("Tributes of Opportunity",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_EngineeFemale.Balance.PopDef_EngineerFemale"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_EngineerMale.Balance.PopDef_EngineerMale")
                ]),
                MultiSpawn("Tributes of Southern Shelf",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_FleshripperFemale.Balance.PopDef_FleshripperFemale"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_FleshripperMale.Balance.PopDef_FleshripperMale")
                ]),
                MultiSpawn("Tributes of Frostburn",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_IncineratorFemale.Balance.PopDef_IncineratorFemale"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_IncineratorMale.Balance.PopDef_IncineratorMale")
                ]),
                MultiSpawn("Tributes of Lynchwood",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    factory="GD_Population_AlliumHunger.Population.PopDef_TurkeyTributeMix:PopulationFactoryBalancedAIPawn_4"),
                    CustomSpawn("Male",Tag.BADASS,      factory="GD_Population_AlliumHunger.Population.PopDef_TurkeyTributeMix:PopulationFactoryBalancedAIPawn_5")
                ]),
                MultiSpawn("Tributes of Sanctuary",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    factory="GD_Population_AlliumHunger.Population.PopDef_TurkeyTributeMix:PopulationFactoryBalancedAIPawn_6"),
                    CustomSpawn("Male",Tag.BADASS,      factory="GD_Population_AlliumHunger.Population.PopDef_TurkeyTributeMix:PopulationFactoryBalancedAIPawn_7")
                ]),
                MultiSpawn("Tributes of Wurmwater",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_SandFemale.Balance.PopDef_SandFemale"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_SandMale.Balance.PopDef_SandMale")
                ]),
            ], map_blacklist=["Hunger_P"]),
            PoolSpawn("Love Thresher",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Blue",Tag.BADASS,     popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherBlue", spawnPointDef="None"),
                CustomSpawn("Green",Tag.MEDIUM,    popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherGreen", spawnPointDef="None"),
                CustomSpawn("Orange",Tag.BOSS,     popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherOrange", spawnPointDef="None"),
                CustomSpawn("Purple",Tag.MINIBOSS, popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherPurple", spawnPointDef="None"),
                CustomSpawn("White",Tag.CHUMP,     popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherWhite", spawnPointDef="None"),
            ], map_blacklist=["Distillery_P"], spawnPointDef="None"),
            MultiSpawn("Crabworms",Tag.CHUMP,customSpawnList=[
                CustomSpawn("Craboid",Tag.CHUMP,range(0,3),     popDef="GD_Population_Crabworms.Population.PopDef_Craboid"),
                CustomSpawn("CraboidGiant",Tag.MEDIUM,[0,1],    popDef="GD_Population_Crabworms.Population.PopDef_CraboidGiant"),
                CustomSpawn("Crabworm",Tag.CHUMP,range(1,4),    popDef="GD_Population_Crabworms.Population.PopDef_Crabworm"),
                CustomSpawn("Crawthumper",Tag.CHUMP,range(0,4), popDef="GD_Population_Crabworms.Population.PopDef_CrawThumper"),
            ])
        ],
        
        DLC.Digistruct: [
        ]
    },
    ModMenu.Game.TPS: {
        DLC.TPS: [
        ],    
        DLC.Claptastic: [
        ]
    }
}[ModMenu.Game.GetCurrent()]

megaMixSubstitutionPools: List[List[str]] = {
    ModMenu.Game.BL2:[
        # Loaders
        [
            "GD_Population_Loader.Population.PopDef_LoaderBUL:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_1",
        ],
        [
            "GD_Population_Loader.Population.PopDef_LoaderEXP:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_0",
        ],
        [
            "GD_Population_Loader.Population.PopDef_LoaderBadass:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_2",
        ],
        [
            "GD_Population_Loader.Population.PopDef_LoaderGUN:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_3",
        ],
        [
            "GD_Population_Loader.Population.PopDef_LoaderHOT:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_4",
        ],
        [
            "GD_Population_Loader.Population.PopDef_LoaderJET:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_5",
        ],
        [
            "GD_Population_Loader.Population.PopDef_LoaderPWR:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_6",
        ],
        [
            "GD_Population_Loader.Population.PopDef_LoaderRPG:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge:PopulationFactoryBalancedAIPawn_7",
        ],
        [   # JNK with ARR
            "GD_Population_Loader.Population.PopDef_LoaderJunk:PopulationFactoryBalancedAIPawn_1",
            "GD_Orchid_Pop_Loader.Population.PopDef_Orchid_Loader_RefineryMix:PopulationFactoryBalancedAIPawn_4",
        ],
        [   # Psychos
            "GD_Population_Psycho.Population.PopDef_Psycho:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_Psycho.Population.PopDef_PsychoBurning:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_Psycho.Population.PopDef_PsychoSnow:PopulationFactoryBalancedAIPawn_0",
            "GD_Allium_PsychoKitchen.Balance.PopDef_PsychoKitchen:PopulationFactoryBalancedAIPawn_0",
            "GD_Anemone_Pop_Bandits.Balance.PopDef_Ini_Psycho:PopulationFactoryBalancedAIPawn_0",
            "GD_HodunkPsycho.Balance.PopDef_HodunkPsycho:PopulationFactoryBalancedAIPawn_0",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Angels:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Dragon:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Torgue:PopulationFactoryBalancedAIPawn_1",
            "GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PiratePsycho:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_AlliumXmas.Population.PopDef_SnowPsychos:PopulationFactoryBalancedAIPawn_1",
            "GD_HodunkPsycho.Balance.PopDef_HodunkPsycho:PopulationFactoryBalancedAIPawn_0",
            "GD_Nast_Zaford_Grunt.Balance.PopDef_Nast_ZafordMix:PopulationFactoryBalancedAIPawn_0",
            "GD_Psycho_Digi.Population.PopDef_Psycho_Digi:PopulationFactoryBalancedAIPawn_0",
        ],
        [   # Suicide Psychos
            "GD_Population_Psycho.Population.PopDef_PsychoSuicide:PopulationFactoryBalancedAIPawn_0",
            "GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_MarauderMix:PopulationFactoryBalancedAIPawn_9",
        ],
        [   # Badass Psychos
            "GD_Population_Psycho.Population.PopDef_PsychoBadass:PopulationFactoryBalancedAIPawn_0",
            "GD_Iris_Population_Psycho.Population.PopDef_Iris_PsychoBadassBiker:PopulationFactoryBalancedAIPawn_4",
            "GD_Lobelia_TannisPops.Population.PopDef_BanditMixture:PopulationFactoryBalancedAIPawn_18",
        ],
        [   # Marauders
            "GD_Population_Marauder.Population.PopDef_Marauder:PopulationFactoryBalancedAIPawn_0",
            "GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateMarauder:PopulationFactoryBalancedAIPawn_0",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Angels:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Dragon:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Torgue:PopulationFactoryBalancedAIPawn_1",
            "GD_MarauderRegular_Digi.Population.PopDef_Marauder_Regular_Digi:PopulationFactoryBalancedAIPawn_2",
        ],
        [   # Marauder Grunts (Can't use cover)
            "GD_Population_Marauder.Population.PopDef_MarauderGrunt:PopulationFactoryBalancedAIPawn_0",
            "GD_Nast_Hodunk_Grunt.Balance.PopDef_Nast_HodunkGrunt:PopulationFactoryBalancedAIPawn_0",
            "GD_Nast_Zaford_Grunt.Balance.PopDef_Nast_ZafordGrunt:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_AlliumXmas.Population.PopDef_SnowMarauders:PopulationFactoryBalancedAIPawn_0",
            "GD_Allium_MarauderKitchen.Balance.PopDef_MarauderKitchen:PopulationFactoryBalancedAIPawn_0",
        ],
        [   # Badass Marauders
            "GD_Population_Marauder.Population.PopDef_MarauderBadass:PopulationFactoryBalancedAIPawn_0",
            "GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateCaptain:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_AlliumXmas.Population.PopDef_SnowBanditMix:PopulationFactoryBalancedAIPawn_3",
            "GD_HodunkBadass.Balance.PopDef_HodunkBadass:PopulationFactoryBalancedAIPawn_0",
            "GD_ZafordBadass.Balance.PopDef_ZafordBadass:PopulationFactoryBalancedAIPawn_0",
            "GD_MarauderBadass_Digi.Population.PopDef_MarauderBadass_Digi:PopulationFactoryBalancedAIPawn_0",
        ],
        [   # Midgets
            "GD_Population_Midget.Population.PopDef_MidgetMix_Regular:PopulationFactoryBalancedAIPawn_11",
            #"GD_Population_Midget.Population.PopDef_MidgetBone1:PopulationFactoryBalancedAIPawn_0",    # Fridge package not loaded
            "GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_MarauderMix:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerMidget_Angels:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerMidget_Dragon:PopulationFactoryBalancedAIPawn_1",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerMidget_Torgue:PopulationFactoryBalancedAIPawn_1",
            "GD_Allium_Butcher_Midget.Balance.PopDef_ButcherMidget:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_AlliumXmas.Population.PopDef_SnowBanditMix:PopulationFactoryBalancedAIPawn_2",
            "GD_PsychoMidget_Digi.Population.PopDef_PsychoMidget_Digi:PopulationFactoryBalancedAIPawn_0",
        ],
        [   # Bruisers
            "GD_Population_Bruiser.Population.PopDef_Bruiser:PopulationFactoryBalancedAIPawn_0",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerBruiser_Dragon:PopulationFactoryBalancedAIPawn_3",
            "GD_Iris_Population_Bruiser.Population.PopDef_Iris_BikerBruiser:PopulationFactoryBalancedAIPawn_3",
            "GD_Anemone_Pop_Infected.Population.PopDef_Infected_MIX:PopulationFactoryBalancedAIPawn_4",
        ],
        [   # Nomads
            "GD_Population_Nomad.Population.PopDef_Nomad:PopulationFactoryBalancedAIPawn_0",
            "GD_Lobelia_TannisPops.Population.PopDef_BanditMixture:PopulationFactoryBalancedAIPawn_2",
        ],
        [   # Goliaths
            "GD_Population_Goliath.Population.PopDef_Goliath:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_AlliumXmas.Population.PopDef_SnowBanditMix:PopulationFactoryBalancedAIPawn_4",
            "GD_Anemone_Pop_Infected.Population.PopDef_InfectedGoliath:PopulationFactoryBalancedAIPawn_0",
        ],
        [   # Goliath Blaster with Arena Goliath
            "GD_Population_Goliath.Population.PopDef_GoliathMix_Regular:PopulationFactoryBalancedAIPawn_14",
            "GD_Iris_Population_Goliath.Population.PopDef_Iris_ArenaGoliath:PopulationFactoryBalancedAIPawn_0",
        ],
        [   # Stalker with Tri-tail stalker - Ambush or Needle?
            "GD_Population_Stalker.Population.PopDef_StalkerMix_Needle:PopulationFactoryBalancedAIPawn_0",
            "GD_Orchid_Pop_Stalker.Population.PopDef_Orchid_StalkerMix_Regular:PopulationFactoryBalancedAIPawn_3",
        ],
        [   # Hyperion Engineer with Torgue Engineer
            "GD_Population_Engineer.Population.PopDef_EngineerArms:PopulationFactoryBalancedAIPawn_0",
            "GD_Iris_Population_Biker.Gangs.PopDef_Iris_EngineerArmsBarrel_Torgue:PopulationFactoryBalancedAIPawn_0",
        ],
        [   # Slag Skag with Digi Skag
            "GD_Population_Skag.Population.PopDef_SkagMix_Badass:PopulationFactoryBalancedAIPawn_3",
            "GD_SkagBadassSlag_Digi.Population.PopDef_SkagBadassSlag_Digi:PopulationFactoryBalancedAIPawn_2",
        ],
        [   # Slagged Spore with Infected Spore
            "GD_Sage_Pop_Spore.Population.PopDef_Sage_GiantSpore_Mix:PopulationFactoryBalancedAIPawn_4",
            "GD_Anemone_Pop_WildLife.Population.PopDef_SporeMIX_OldDust2:PopulationFactoryBalancedAIPawn_5",
        ],
        [   # Varkids (but not Bloods) with Tropical Varkids
            "GD_Population_BugMorph.Population.PopDef_BugMorphMix_Regular:PopulationFactoryBalancedAIPawn_1",
            "GD_Population_BugMorphs.Population.PopDef_BugMorph_TropicalMix:PopulationFactoryBalancedAIPawn_0",
            "GD_Population_BugMorphs.Population.PopDef_BugMorph_TropicalMix:PopulationFactoryBalancedAIPawn_1",
            "GD_Population_BugMorphs.Population.PopDef_BugMorph_TropicalMix:PopulationFactoryBalancedAIPawn_2",
        ],
    ],
    ModMenu.Game.TPS:[
    ]
}[ModMenu.Game.GetCurrent()]
"""Each list is a pool of PopulationFactoryBalancedAIPawn - we can get the AIPawnBalanceDefinition from the factory here to compare"""