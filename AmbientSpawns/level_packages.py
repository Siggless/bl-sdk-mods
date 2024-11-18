import enum
import time
import unrealsdk
from unrealsdk import Log
from Mods import ModMenu

class DLC(enum.IntEnum):
    BL2 = enum.auto()
    Scarlett = enum.auto()
    Torgue = enum.auto()
    Hammerlock = enum.auto()
    DragonKeep = enum.auto()
    FFS = enum.auto()
    Headhunters = enum.auto()
    Digistruct = enum.auto()
    TPS = enum.auto()
    Claptastic = enum.auto()
    ShockDrop = enum.auto()

CurrentGame = ModMenu.Game.GetCurrent()
BaseDLC = DLC.TPS if CurrentGame is ModMenu.Game.TPS else DLC.BL2

DLC_outer_prefixes = {
    ModMenu.Game.BL2: {
        #DLC.BL2: ["GD_Population"],  # We can't distinguish this with Headhunter ones just using prefix
        DLC.Scarlett: ["GD_Orchid"],
        DLC.Torgue: ["GD_Iris"],
        DLC.Hammerlock: ["GD_Sage"],
        DLC.DragonKeep: ["GD_Aster"],
        DLC.FFS: ["GD_Anemone"],
        DLC.Headhunters: [
            "GD_Allium",
            "GD_Population_Allium",
            # Winter
            "GD_Snow",
            # Halloween
            "GD_Demonic",
            "GD_Pop_HallowSkeleton",
            "GD_PumpkinMinion",
            "GD_Spycho",
            # Thanksgiving
            "GD_Butcher",
            "GD_Crater",
            "GD_EngineeFemale",
            "GD_EngineerMale",
            "GD_Fleshripper",
            "GD_Incinerator",
            "GD_RatChef",
            "GD_Sand",
            "GD_SmallTurkeyMinion"
            # Valentines
            "GD_Nast",
            "GD_Population_VDay",
            "GD_Hodunk",
            "GD_Zaford",
            # Wam Bam
            "GD_Population_Crabworms",
            "GD_Crawmerax",
        ],
        DLC.Digistruct: [
            "GD_Lobelia",
            "GD_MarauderBadass_Digi",
            "GD_MarauderRegular_Digi",
            "GD_MrMercy_Digi",
            "GD_Probe",
            "GD_Psycho_Digi",
            "GD_RatGrunt_Digi",
            "GD_Skag",
            "GD_Spiderant",
        ]
    },
    ModMenu.Game.TPS: {
        #DLC.TPS: ["GD_Population"],
        DLC.Claptastic: [],
        DLC.ShockDrop: []
    }
}[CurrentGame]

def Get_DLC_From_Object(object) -> str:
    if not object:
        return None
    
    outer = object.Outer
    path = object.PathName(object)
    for DLC in DLC_outer_prefixes:
        if any(path.startsWith(prefix) for prefix in DLC):
            return DLC
    # Default to base game since there are some headhunters in GD_Population_*
    return BaseDLC

levels_by_DLC = {
    ModMenu.Game.BL2: {
        DLC.BL2: [
            "Stockade_P",
            "Fyrestone_P",
            "DamTop_P",
            "Dam_P",
            "Boss_Cliffs_P",
            "Caverns_P",
            "VOGChamber_P",
            "Interlude_P",
            "TundraTrain_P",
            "Ash_P",
            "BanditSlaughter_P",
            "Fridge_P",
            "HypInterlude_P",
            "IceCanyon_P",
            "FinalBossAscent_P",
            "Outwash_P",
            "Grass_P",
            "Luckys_P",
            "Grass_Lynchwood_P",
            "CreatureSlaughter_P",
            "HyperionCity_P",
            "RobotSlaughter_P",
            "SanctuaryAir_P",
            "Sanctuary_P",
            "Sanctuary_Hole_P",
            "CraterLake_P",
            "Cove_P",
            "SouthernShelf_P",
            "SouthpawFactory_P",
            "ThresherRaid_P",
            "Grass_Cliffs_P",
            "Ice_P",
            "Frost_P",
            "TundraExpress_P",
            "Boss_Volcano_P",
            "PandoraPark_P",
            "Glacial_P",
        ],
        DLC.Scarlett: [
            "Orchid_Caves_P",
            "Orchid_WormBelly_P",
            "Orchid_Spire_P",
            "Orchid_OasisTown_P",
            "Orchid_ShipGraveyard_P",
            "Orchid_Refinery_P",
            "Orchid_SaltFlats_P",
        ],
        DLC.Torgue: [
            "Iris_Moxxi_P",
            "Iris_Hub_P",
            "Iris_DL2_P",
            "Iris_DL3_P",
            "Iris_DL2_Interior_P",
            "Iris_Hub2_P",
            "Iris_DL1_TAS_P",
            "Iris_DL1_P",
        ],
        DLC.Hammerlock: [
            "Sage_PowerStation_P",
            "Sage_Cliffs_P",
            "Sage_HyperionShip_P",
            "Sage_Underground_P",
            "Sage_RockForest_P",
        ],
        DLC.DragonKeep: [
            "Dark_Forest_P",
            "CastleKeep_P",
            "Village_P",
            "CastleExterior_P",
            "Dead_Forest_P",
            "Dungeon_P",
            "Mines_P",
            "TempleSlaughter_P",
            "Docks_P",
            "DungeonRaid_P",
        ],
        DLC.FFS: [
            "Backburner_P",
            "Sandworm_P",
            "OldDust_P",
            "Helios_P",
            "SanctIntro_P",
            "ResearchCenter_P",
            "GaiusSanctuary_P",
            "SandwormLair_P",
        ],
        DLC.Headhunters: [
            "Hunger_P",
            "Pumpkin_Patch_P",
            "Xmas_P",
            "Distillery_P",
            "Easter_P",
        ],
        DLC.Digistruct: [
            "TestingZone_P",
        ]
    },
    ModMenu.Game.TPS: {
        DLC.TPS: [
            
        ],
        DLC.Claptastic: [
            
        ],
        DLC.ShockDrop: [
            
        ],
    },
}[CurrentGame]

combat_packages_by_DLC = {
    DLC.BL2: [
        # Need to load the _P packages first to make sure BodyTags and stuff are found
        "BanditSlaughter_P.upk",
        "BanditSlaughter_Combat.upk",
        "CreatureSlaughter_P.upk",
        "CreatureSlaughter_Dynamic.upk",
        "RobotSlaughter_P.upk",
        "RobotSlaughter_Dynamic.upk",
        
        # Extra non-Combats we need for missing bits i.e. minibosses
        "Caverns_P.upk",                    # Creepers
        "Cove_Dynamic.upk",                 # MidgetBadass
        "Dam_Dynamic.upk",                  # Marauder
        "Ice_Dynamic.upk",                  # Ice Bullymongs?
        "Fridge_Dynamic.upk",               # Laney
        "Frost_Dynamic.upk",                # Mr Mercy, Bad Maw, Nomad Badass
        "Grass_Lynchwood_Dynamic.upk",      # Marshals, Deputy, Sheriff
        # "HyperionCity_Dynamic.upk",         # ProbeMix_Badass, Foreman
        "SouthpawFactory_Dynamic.upk",      # Assassins
        "TundraTrain_Dynamic.upk",          # Wilhelm

        "Ash_Combat.upk",                   # Rock Bullymongs
        # "BanditSlaughter_Combat.upk",
        # "Boss_Cliffs_Combat.upk",
        "Boss_Cliffs_CombatLoader.upk",     # Loader Bunker Mix
        # "Boss_Volcano_Combat.upk",
        # "Boss_Volcano_Combat_Monster.upk",  # Volcanic Rakk
        # "CraterLake_Combat.upk",
        # "CreatureSlaughter_Combat.upk",
        "Dam_Combat.upk",                   # Mad Mike
        # "DamTop_Combat.upk",
        "FinalBossAscent_Combat.upk",       # HyperionInfiltrator
        # "Fridge_Combat.upk",
        "Fyrestone_Combat.upk",             # Loader Militar Mix
        "Grass_Cliffs_Combat.upk",          # HyperionSoldier
        # "Grass_Combat.upk",
        "Grass_Lynchwood_Combat.upk",       # Miners, Skag Riders
        "IceCanyon_Combat.upk",             # Flame Bandits
        # "Interlude_Combat.upk",
        # "Outwash_Combat.upk",
        "PandoraPark_Combat.upk",           # Stalkers
        # "Sanctuary_Hole_Combat.upk",
        # "SouthernShelf_Combat.upk",
        "Stockade_Combat.upk",              # Junk Loader
        "ThresherRaid_P.upk",               # Terry
        "TundraExpress_Combat.upk",         # Prospector
        # "VOGChamber_Combat.upk",
        
    ],
    DLC.Torgue: [
        # "Iris_Hub_P.upk",
        # "Iris_Hub_Combat.upk",
        # "Iris_Hub_Dynamic.upk",
        "Iris_DL3_P.upk",                   # Forge Loaders
        #"Iris_DL3_Dynamic.upk",            # Forge Loaders (nope need defs from _P)
        "Iris_DL1_Battle.upk",              # Arena Gangs
        #"Iris_Hub2_Combat.upk",            # Monster Truck
        "Iris_DL2_Combat.upk",              # Badass Biker Psycho
        #"Iris_DL2_Interior_Combat.upk",
        #"Iris_DL1_TAS_Combat.upk"
    ],
    DLC.Scarlett: [
        "Orchid_Refinery_Combat.upk",       # ARR Loader
        "Orchid_OasisTown_Combat.upk",      # NoBeard, Pirate Cursed
        "Orchid_Caves_Combat.upk",          # Blue Crystalisks, Pirates
        "Orchid_Spire_P.upk",               # Big Pirates, Mr Bubbles
        "Orchid_Spire_Dynamic.upk",         # Scarlett Crew
        "Orchid_ShipGraveyard_Combat.upk",  # Anchorman
        "Orchid_SaltFlats_Combat.upk"       # Pirate Grenadier
        #"Orchid_WormBelly_Dynamic.upk",     # Rakk Hive, Worms
    ],
    DLC.Hammerlock: [
        #"Sage_Cliffs_Combat.upk",       # Elite Savages - but broken need something else, whatevs
        "Sage_PowerStation_P.upk",
        "Sage_PowerStation_Combat.upk",
        #"Sage_RockForest_Combat.upk",
        #"Sage_Underground_Combat.upk",
    ],
    DLC.DragonKeep: [
        "TempleSlaughter_P.upk",        # Materials for knights
        "TempleSlaughter_Combat.upk",
        "Dead_Forest_Combat.upk",
        #"Docks_Combat.upk",
        "Dungeon_Combat.upk",
        #"Dungeon_Mission.upk",          # Dead Brothers
        #"DungeonRaid_Combat.upk",
        "Mines_Combat.upk",
        "Mines_Dynamic.upk",            # Flying Golem
        "Mines_Mission.upk",            # Maxibillion, Broomstick
        #"CastleExterior_Combat.upk",
        #"CastleKeep_Combat.upk",
        #"Dark_Forest_P.upk",            # Materials for treants
        #"Dark_Forest_Combat.upk"
    ],
    DLC.Headhunters: [
        "Xmas_Combat.upk",              # Snow Bandits
        "Xmas_Dynamic.upk",             # Snow Psychos
        "Hunger_Boss.upk",              # Tributes
        "Hunger_Dynamic.upk",           # Incinerator Tribute
        "Hunger_Mission_1.upk",         # ButcherBoss1-3, RatChef, Tributes
        "Hunger_Mission_2.upk",         # Engineer Tributes
        "Hunger_Mission_3.upk",         # ButcherBoss2-3, ButcherMidget
        #"Pumpkin_Patch_Combat.upk",
        "Distillery_Dynamic.upk",       # Special Threshers
        "Distillery_Mission.upk",       # Hodunks and Zafords
        "Easter_Combat.upk"             # Crabworms, Tropical Varkids
    ],
    DLC.FFS: [
        "BackBurner_P.upk",             # Infected materials
        "BackBurner_Mission_Main.upk",  # Infected materials
        "ResearchCenter_MissionMain.upk",
        "ResearchCenter_MissionSide.upk",
        "OldDust_Lair.upk",             # Infected Bandits
        "OldDust_LD.upk",               # Infected Goliath, Curse
        "OldDust_Mission_Main.upk",
        "OldDust_Mission_Side.upk",
        "Sandworm_Encounters",          # Infected Golem Badass
        "Sandworm_Mission_Side.upk",
        "Helios_Mission_Main.upk",
        "Helios_Mission_Side.upk",
    ],
    DLC.Digistruct: [
        "TestingZone_Combat.upk"
    ]
}

loaded_DLCs = []

def GetCurrentDLC(PC) -> str:
    map_name = PC.WorldInfo.GetStreamingPersistentMapName()
    for DLC in levels_by_DLC:
        if map_name.lower() in [x.lower() for x in levels_by_DLC[DLC]]:
            #Log(f"{map_name} found in {DLC.name}")
            return DLC
    #Log(f"{map_name} not found!")
    return None

def KeepAliveAllClass(class_name: str):
    objects = unrealsdk.FindAll(class_name)
    for object in objects:
        unrealsdk.KeepAlive(object)

def LoadLevelSpawnObjects(DLC: str):
    if DLC in loaded_DLCs:
        #Log(f"DLC {DLC.name} levels are already loaded!")
        return
    
    for package_name in combat_packages_by_DLC[DLC]:
        unrealsdk.LoadPackage(package_name)
        KeepAliveAllClass("WillowPopulationDefinition")
        KeepAliveAllClass("PopulationFactoryBalancedAIPawn")

        # We will also need to only do this on the MENUMAP because otherwise is crashes on level change
        # Due to garbage collection
        # # AK
        # KeepAliveAllClass("AkEvent")
        # # Anim
        # KeepAliveAllClass("AnimSet")
        # # Char/Veh
        # KeepAliveAllClass("Material")
        # KeepAliveAllClass("MaterialInstanceConstant")
        # KeepAliveAllClass("PhysicsAsset")
        # KeepAliveAllClass("SkeletalMeshSocket")
        # KeepAliveAllClass("StaticMesh")
        # KeepAliveAllClass("Texture2D")
        # # FX
        # KeepAliveAllClass("ParticleSpriteEmitter")
        # KeepAliveAllClass("ParticleSystem")
        # # GD_AI
        # KeepAliveAllClass("AIResource")
        # KeepAliveAllClass("AttributeDefinition")
        # KeepAliveAllClass("PawnAllegiance")
        # KeepAliveAllClass("PopulationBodyTag")
        # KeepAliveAllClass("PopulationSpawnedActorTagDefinition")
        # KeepAliveAllClass("TargetingDefinition")
        # # GD_Balance
        # KeepAliveAllClass("AttributeInitializationDefinition")
        # KeepAliveAllClass("InteractiveObjectDefinition")
        # KeepAliveAllClass("InteractiveObjectBalanceDefinition")
        # # GD_ENEMY
        # KeepAliveAllClass("AIClassDefinition")
        # KeepAliveAllClass("AIPawnBalanceDefinition")
        # KeepAliveAllClass("BehaviorVolumeDefinition")
        # KeepAliveAllClass("BodyClassDefinition")
        # KeepAliveAllClass("BodyClassDeathDefinition")
        # KeepAliveAllClass("BodyHitRegionDefinition")
        # KeepAliveAllClass("CoordinatedEffectDefinition")
        # KeepAliveAllClass("GearboxDialogGroup")
        # KeepAliveAllClass("StanceTypeDefinition")
        # KeepAliveAllClass("TurnDefinition")
        # KeepAliveAllClass("WillowAIDefinition")
        # KeepAliveAllClass("WillowAIPawn")
        # KeepAliveAllClass("WillowAnimDefinition")
        # KeepAliveAllClass("WillowDialogEventTag")
        # # GD_Impacts
        # KeepAliveAllClass("WillowExplosionImpactDefinition")
        # KeepAliveAllClass("WillowImpactDefinition")

    loaded_DLCs.append(DLC)
    
