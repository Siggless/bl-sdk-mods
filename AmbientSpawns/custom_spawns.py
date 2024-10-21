import enum
import random
import unrealsdk
from unrealsdk import Log
from typing import *

try:
    from . import level_packages
    from .level_packages import *
    from . import ModMenu
except ImportError:
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
    Tag.MEDIUM: 40,
    Tag.BADASS: 50,
    Tag.ULTIMATE_BADASS: 20,
    Tag.MINIBOSS: 10,
    Tag.BOSS: 5
}
"""Weights for selecting a spawn by Badass Tag"""

popDefSubstitutionPools=[
    [
        "GD_Population_Psycho.Population.PopDef_PsychoBadass",
        "GD_Iris_Population_Psycho.Population.PopDef_Iris_PsychoBadassBiker"
    ],
    [
        "GD_Population_Psycho.Population.PopDef_Psycho",
        "GD_Population_Psycho.Population.PopDef_PsychoBurning",
        "GD_Population_Psycho.Population.PopDef_PsychoSnow",
        "GD_Allium_PsychoKitchen.Balance.PopDef_PsychoKitchen",
        "GD_Anemone_Pop_Bandits.Balance.PopDef_Ini_Psycho",
        "GD_HodunkPsycho.Balance.PopDef_HodunkPsycho",
        "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Angels",
        "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Dragon",
        "GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Torgue",
        "GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PiratePsycho",
        "GD_Population_AlliumXmas.Population.PopDef_SnowPsychos",
        "GD_Psycho_Digi.Population.PopDef_Psycho_Digi"
    ]
]
"""If a popDef isn't found in this map, or there are other ones available, we can make it a bit
more random by choosing one to subsitute - particularly in the DLC areas.
"""
# TODO Cache the sub-list in the CustomSpawns on load, then pick each spawn. If MegaMix

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
    def GetNewFactoryList(self, den, gameStage, rarity = 1):
        """Returns a list of (factory, spawnPointDef, delay) for a random instance of this spawn"""
        raise NotImplementedError


class CustomSpawn(Spawn):
    """Spawns a random number of a given popDef or factory."""
    def __init__(self, name, tag, numSpawns=None, numSpawnsWeights=None, popDef=None, factory=None, spawnPointDef=None, map_whitelist=[], map_blacklist=[]) -> None:
        super().__init__(name, tag, spawnPointDef, map_whitelist, map_blacklist)
        
        if numSpawns:
            self.numSpawns =  list(numSpawns)
            if numSpawnsWeights:
                self.numSpawnsWeights =  list(numSpawnsWeights)
                if len(self.numSpawns) != len(self.numSpawnsWeights):
                    raise ValueError(f"{self.name} numSpawnsWeights do not match numSpawns:\t{self.numSpawns} - {self.numSpawnsWeights}")
            else:
                self.numSpawnsWeights = [1 for x in self.numSpawns]
        else:
            self.numSpawns = NullCustomSpawn.numSpawns
            self.numSpawnsWeights = NullCustomSpawn.numSpawnsWeights
        self.minSpawns = min(self.numSpawns)
        self.maxSpawns = max(self.numSpawns)
            
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
        
    def GetRandomNumSpawns(self):
        if self.minSpawns == self.maxSpawns:
            return self.minSpawns
        return random.choices(self.numSpawns, self.numSpawnsWeights)[0]
    
    def GetNewFactoryList(self, den, gameStage, rarity=1):
        """Returns a list of the single factory if defined, or a random factory from the popDef if not"""
        thisNumSpawns = self.GetRandomNumSpawns()
        # A random-ish delay makes the Helios groups way better
        delayRange = int(100 * self.delayBetweenSpawns / 3)
        
        factoryList = []
        for i in range(thisNumSpawns):
            randomDelay = self.delayBetweenSpawns + random.randint(-delayRange, delayRange) / 100
            if self.popDefObj:
                if not self.popDefObj:
                    raise Exception("Tried to get a popDefObj when it has either not been loaded, or None!")
                factoryList.append((self.popDefObj.GetRandomFactory(den, gameStage, rarity), self.spawnPointDef, randomDelay))
            else:
                if not self.factoryObj:
                    raise Exception("Tried to get a factoryObj when it has either not been loaded, or None!")
                factoryList.append((self.factoryObj, self.spawnPointDef, randomDelay))
        return factoryList

    def LoadObjects(self, mapNameLower) -> bool:
        """ 
        Tries to load the defined PopDef/Factory object for this spawn.
        Also tries to store MegaMix PopDef lists, if enabled.
        Returns whether successful (and therefore usable in the current map).
        """
        if mapNameLower in self.map_blacklist:
            return False
        
        self.factoryObj = None
        if self.factory:
            self.factoryObj = unrealsdk.FindObject("PopulationFactoryBalancedAIPawn", self.factory)
            if not self.factoryObj:
                Log(f"{self.factory} not found in this map.")
                return False
        else:
            self.popDefObj = unrealsdk.FindObject("WillowPopulationDefinition", self.popDef)
            if not self.popDefObj:
                Log(f"{self.popDef} not found in this map.")
                return False
            self.factoryObj = self.popDefObj.ActorArchetypeList[0].SpawnFactory  # Assuming all pawns in a factory have the same body tag
        return True

    # Don't forget to filter to maps first to cut it down with white and blacklists!
    def DenSupportsSpawn(self, den) -> bool:
        """Checks whether this CustomSpawn can use spawn animations for the given den."""
        if not self.factoryObj:
            raise ValueError("A CustomSpawn does not have a factory loaded for DenSupportsSpawn!")
        
        AIPawnBalanceDef = self.factoryObj.PawnBalanceDefinition
        if not AIPawnBalanceDef:
            Log(f"{self.factoryObj.Name} has no AIPawnArchetype.")
            return False
        customBodyTag = AIPawnBalanceDef.AIPawnArchetype.BodyClass.BodyTag
        if not customBodyTag:
            Log(f"Can't find a BodyTag from {self.popDefObj.Name} from den {den.PathName(den)}.")
            #return False
            return True
        
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
            else:
                for bodyTag in [animMap.Key for animMap in spawn.PointDef.AnimMap if animMap.Key]:
                    # Check this tag matches the enemy we want to spawn
                    if bodyTag is customBodyTag:
                        #Log(f"{self.popDef} BodyTag {bodyTag.Name} matches den's factory BodyTag {customBodyTag.Name}.")
                        return True
        return False
    
    def IsInDLC(self, DLC: DLC) -> bool:
        if self.factoryObj:
            return Get_DLC_From_Object(self.factoryObj) is DLC
        elif self.popDefObj:
            return Get_DLC_From_Object(self.popDefObj) is DLC
        return False


def CustomSpawnFromPopDef(PopDef) -> CustomSpawn:
    if not PopDef:
        return None
    if not PopDef.ActorArchetypeList:
        return None
    
    tag = Tag.CHUMP
    for archetype in PopDef.ActorArchetypeList:
        factory = archetype.SpawnFactory
        # Some archetypes are another factory instead of a popdef
        if not factory or factory.bIsCriticalActor or not (factory.PawnBalanceDefinition or factory.PopulationDef):
            return None
        if factory.PawnBalanceDefinition and factory.PawnBalanceDefinition.Champion:
            tag = Tag.MEDIUM

    spawn = CustomSpawn(
        PopDef.Name,
        tag,
        range(3,7) if tag is Tag.CHUMP else range(2,4),
        popDef=PopDef.PathName(PopDef)
    )
    spawn.popDefObj = PopDef
    spawn.factoryObj = PopDef.ActorArchetypeList[0].SpawnFactory
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
    """Spawns a number of CustomSpawns randomly picked from a pool or CustomSpawns"""
    def __init__(self, name, tag, numPicks=None, customSpawnList=[], customSpawnWeights=[], spawnPointDef=None, map_whitelist=[], map_blacklist=[]) -> None:
        super().__init__(name, tag, spawnPointDef, map_whitelist, map_blacklist)
        
        self.customSpawnList = customSpawnList
        if customSpawnWeights:
            self.customSpawnWeights = customSpawnWeights
            if len(customSpawnWeights) != len(customSpawnList):
                raise ValueError(f"{name} num weights don't match num spawns!")
        else:
            self.customSpawnWeights = [1 for x in customSpawnList]
        if numPicks:
            self.numSpawn = numPicks
        else:
            self.numSpawn = 1
        self.activeSpawnList = [*self.customSpawnList]
        self.activeSpawnWeights = [*self.customSpawnWeights]
    
    def GetNewFactoryList(self, den, gameStage, rarity=1):
        """Returns the factory list for 'numPicks' randomly chosen CustomSpawns in this PoolSpawn"""
        factoryList = []
        for choice in random.choices(self.activeSpawnList, self.activeSpawnWeights, k=self.numSpawn):
            factoryList = factoryList + choice.GetNewFactoryList(den, gameStage, rarity)
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
        return any(x.DenSupportsSpawn(den) for x in self.customSpawnList)


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
    
    def GetNewFactoryList(self, den, gameStage, rarity=1):
        """Returns the factory list combining each CustomSpawn in this MultiSpawn"""
        factoryList = []
        for i, customSpawn in enumerate(self.customSpawnList):
            for j in range(self.numSpawn[i]):
                factoryList = factoryList + customSpawn.GetNewFactoryList(den, gameStage, rarity)
        return factoryList
    
    def LoadObjects(self, mapNameLower) -> bool:
        if mapNameLower in self.map_blacklist:
            return False
        return all(x.LoadObjects(mapNameLower) for x in self.customSpawnList)
    
    def DenSupportsSpawn(self, den) -> bool:
        return all(x.DenSupportsSpawn(den) for x in self.customSpawnList)


class MegaMixSpawn:
    """Makes multiple random choices from the given CustomSpawns - for mixing enemy variants from different DLCs"""


customList: Dict[ModMenu.Game, Dict[str, List[Spawn]]] = {
    ModMenu.Game.BL2: {
        DLC.BL2: [
            # Bandit
            CustomSpawn("A butt-load of midgets",Tag.CHUMP,range(8,15),[4,5,5,3,2,1,1],popDef="GD_Population_Midget.Population.PopDef_MidgetMix_Regular"),
            CustomSpawn("Bruisers",Tag.CHUMP,range(1,4),popDef="GD_Population_Bruiser.Population.PopDef_Bruiser"),
            CustomSpawn("More-rauders",Tag.CHUMP,range(3,7),[2,3,2,1],popDef="GD_Population_Marauder.Population.PopDef_MarauderMix_Regular"),
            
            CustomSpawn("Lookout! Badass Psychos!",Tag.ULTIMATE_BADASS,range(2,5),[3,3,2],popDef="GD_Population_Psycho.Population.PopDef_PsychoBadass"),
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
                CustomSpawn("Friend",Tag.CHUMP,                 popDef="GD_Population_Midget.Population.PopDef_MidgetBadass"),
                CustomSpawn("Goliaths",Tag.MEDIUM,range(1,4),   popDef="GD_Population_Goliath.Population.PopDef_GoliathMix_Regular"),
                CustomSpawn("Big Goliath",Tag.BADASS,           popDef="GD_Population_Goliath.Population.PopDef_GoliathTurret"),
            ]),
            
            # TODO Flamers from Frostburn/Ice_P
            
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
            ], customSpawnWeights=[2,2,2,1]),

            # Rats
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
                CustomSpawn("Flinter",Tag.MINIBOSS,[0,1],[1,1], popDef="GD_Population_Rat.Population.Unique.PopDef_RatEasterEgg")
            ], map_blacklist=["dam_p"]),
            
            # Hyperion
            CustomSpawn("Helios ATTACKS!",Tag.MEDIUM,range(8,15),popDef="GD_Population_Loader.Population.PopDef_LoaderMix_Regular",spawnPointDef="PopPointDef_OrbitalDrop"),
            MultiSpawn("Helios ATTACKS AGAIN (because it's cool)",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("RPG",Tag.CHUMP,[2,3],[1,1],    popDef="GD_Population_Loader.Population.PopDef_LoaderRPG"),
                CustomSpawn("SGT",Tag.CHUMP,[2,3],[1,1],    popDef="GD_Population_Loader.Population.PopDef_LoaderSGT"),
                CustomSpawn("WAR",Tag.MEDIUM,[1,2],[4,1],   popDef="GD_Population_Loader.Population.PopDef_LoaderWAR"),
            ]),
            CustomSpawn("Helios ATTACKS - Bunker Mix",Tag.MEDIUM,range(8,15),popDef="GD_Population_Loader.Population.PopDef_LoaderMix_BunkerFight",spawnPointDef="PopPointDef_OrbitalDrop"),
            CustomSpawn("Badass loaders",Tag.BADASS,[2,3,4],[7,4,1],popDef="GD_Population_Loader.Population.PopDef_LoaderBadass"),
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
                CustomSpawn("Soldier",Tag.CHUMP,[1,2],[4,1],    popDef="GD_Population_Engineer.Population.PopDef_HyperionSoldier"),
            ]),
            MultiSpawn("Flying enemies are fun",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Jets",Tag.CHUMP,range(3,5),        popDef="GD_Population_Loader.Population.PopDef_LoaderJET"),
                CustomSpawn("Surveyors",Tag.CHUMP,range(3,5),   popDef="GD_Population_Probe.Population.PopDef_ProbeMix_Regular")
            ]),
            # TODO Wilhelm boss from TundraTrain
            
            # Fauna
            CustomSpawn("Release the Rakk!",Tag.CHUMP,[4,8],popDef="GD_Population_Rakk.Population.PopDef_Rakk"),
            
            MultiSpawn("Skag Ma & Pa",Tag.BADASS,customSpawnList=[
                CustomSpawn("Badass",Tag.BADASS,[2],        popDef="GD_Population_Skag.Population.PopDef_SkagMix_Badass"),
                CustomSpawn("Pups",Tag.CHUMP,range(4,10),   popDef="GD_Population_Skag.Population.PopDef_SkagPup")
            ]),
            
            MultiSpawn("Terramorphous Peek",Tag.BOSS,customSpawnList=[
                CustomSpawn("Spikes",Tag.MINIBOSS,[1,2],[3,1],  popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidA",spawnPointDef="None"),
                CustomSpawn("Rock",Tag.MINIBOSS,[1,2],[3,1],    popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidC",spawnPointDef="None"),
                CustomSpawn("Beam",Tag.MINIBOSS,[1,2],[3,1],    popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidD",spawnPointDef="None"),
                CustomSpawn("Masher",Tag.MINIBOSS,[1,2],[3,1],  popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidE",spawnPointDef="None"),
            ],spawnPointDef="None"),
            CustomSpawn("Terramorphous Peek Fire",Tag.MINIBOSS,[2,3,4],[1,2,1],popDef="GD_Population_Thresher.Population.Unique.PopDef_TentacleRaidF",spawnPointDef="None"),
    
        ],
        DLC.Scarlett: [
        ],
        DLC.Torgue: [
        ],
        DLC.Hammerlock: [
            CustomSpawn("Elite Savages",Tag.ULTIMATE_BADASS,[2,3,4],[1,2,2],popDef="GD_Sage_Pop_Natives.Population.PopDef_Native_Elite"),
            # TODO Spore Pinata Party
        ],
        DLC.DragonKeep: [
            CustomSpawn("Handsome Tower ATTACKS!",Tag.MEDIUM,range(8,15),popDef="GD_Aster_Pop_Orcs.Population.PopDef_OrcsDen_Regular",spawnPointDef="PopPointDef_Orc_OrbitalDrop"),
            MultiSpawn("Arachne Hunting Party",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Reapers",Tag.MEDIUM,range(4,8),    popDef="GD_Aster_Pop_Spiders.Population.PopDef_Arachne"),
                CustomSpawn("Minions",Tag.CHUMP,range(4,8),     popDef="GD_Aster_Pop_Spiders.Population.PopDef_SpiderDen_Regular")
            ]),
        ],
        DLC.FFS: [
            MultiSpawn("Sandworm Ambush",Tag.MEDIUM,customSpawnList=[
                CustomSpawn("Queen",Tag.MEDIUM,             popDef="GD_Anemone_Pop_WildLife.Population.PopDef_SandWorm_Queen"),
                CustomSpawn("Worms",Tag.CHUMP,range(2,6),   popDef="GD_Anemone_Pop_WildLife.Population.PopDef_InfectedSandWorm")
            ]),
            CustomSpawn("Sanctuary ATTACKS!",Tag.MEDIUM,range(8,15),popDef="GD_Anemone_Pop_Infected.Population.PopDef_Infected_MIX",spawnPointDef="PopPointDef_OrbitalDrop_Infection_Test"),
            # TODO Sentient mutating Spores in my grill
        ],
        DLC.Headhunters: [
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
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_Lynchwood_Female.Character.Pawn_Lynchwood_Female"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_Lynchwood_Male.Character.Pawn_Lynchwood_Male")
                ]),
                MultiSpawn("Tributes of Sanctuary",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_RaiderFemale.Character.Pawn_RaiderFemale"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_RaiderMale.Character.Pawn_RaiderMale")
                ]),
                MultiSpawn("Tributes of Wurmwater",Tag.ULTIMATE_BADASS,customSpawnList=[
                    CustomSpawn("Female",Tag.BADASS,    popDef="GD_SandFemale.Balance.PopDef_SandFemale"),
                    CustomSpawn("Male",Tag.BADASS,      popDef="GD_SandMale.Balance.PopDef_SandMale")
                ]),
            ],map_blacklist=["Hunger_P"])
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
