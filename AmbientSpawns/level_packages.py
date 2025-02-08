import enum
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
    Holodome = enum.auto()


CURRENT_GAME = ModMenu.Game.GetCurrent()
BaseDLC = DLC.TPS if CURRENT_GAME is ModMenu.Game.TPS else DLC.BL2

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
        DLC.Claptastic: [
            "GD_Ma_",
            "GD_Marigold",
        ],
        DLC.Holodome: [
            "GD_EridianSlaughter",
        ]
    }
}[CURRENT_GAME]
"""Lists of outer prefixes to get the DLC that an object is from using those."""


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
            "MoonSlaughter_P",
            "Spaceport_P",
            "ComFacility_P",
            "InnerCore_P",
            "LaserBoss_P",
            "MoonShotIntro_P",
            "CentralTerminal_P",
            "JacksOffice_P",
            "Laser_P",
            "Meriff_P",
            "Digsite_Rk5arena_P",
            "Outlands_P2",
            "Outlands_P",
            "Wreck_P",
            "Deadsurface_P",
            "RandDFacility_P",
            "Moonsurface_P",
            "StantonsLiver_P",
            "Sublevel13_P",
            "DahlFactory_P",
            "DahlFactory_Boss",
            "Moon_P",
            "Access_P",
            "InnerHull_P",
            "Digsite_P",
        ],
        DLC.Claptastic: [
            "Ma_LeftCluster_P",
            "Ma_RightCluster_P",
            "Ma_SubBoss_P",
            "Ma_Deck13_P",
            "Ma_FinalBoss_P",
            "Ma_Motherboard_P",
            "Ma_Nexus_P",
            "Ma_Subconscious_P",
        ],
        DLC.Holodome: [
            "Eridian_Slaughter_P",
        ],
    },
}[CURRENT_GAME]

# I could just load all _P, _Dynamic, and _Combat packages to make sure we get everything.
# But I don't really want to load the entire game at once, so being selective here.
combat_packages_by_DLC = {
    DLC.BL2: [
        # Need to load the _P packages first to make sure BodyTags and stuff are found
        "BanditSlaughter_P",
        "BanditSlaughter_Combat",
        "CreatureSlaughter_P",
        "CreatureSlaughter_Dynamic",
        "RobotSlaughter_P",
        "RobotSlaughter_Dynamic",
        
        # Extra non-Combats we need for missing bits i.e. minibosses
        "Caverns_P",                    # Creepers
        "Cove_Dynamic",                 # MidgetBadass
        "Dam_Dynamic",                  # Marauder
        "Ice_P"                         # Vehicle textures, bone/horn textures
        "Ice_Dynamic",                  # Nomad Pyro
        "Fridge_Dynamic",               # Laney
        "Frost_Dynamic",                # Mr Mercy, Bad Maw, Nomad Badass
        #"Grass_Lynchwood_P"             # Cowboy hat texture
        #"Grass_Lynchwood_Dynamic",      # Marshals, Deputy, Sheriff
        # "HyperionCity_Dynamic",         # ProbeMix_Badass, Foreman
        "SouthpawFactory_Dynamic",      # Assassins
        "TundraTrain_Dynamic",          # Wilhelm

        "Ash_Combat",                   # Rock Bullymongs
        # "BanditSlaughter_Combat",
        # "Boss_Cliffs_Combat",
        "Boss_Cliffs_CombatLoader",     # Loader Bunker Mix
        # "Boss_Volcano_Combat",
        # "Boss_Volcano_Combat_Monster",  # Volcanic Rakk
        # "CraterLake_Combat",
        # "CreatureSlaughter_Combat",
        "Dam_Combat",                   # Mad Mike
        # "DamTop_Combat",
        "FinalBossAscent_Combat",       # HyperionInfiltrator
        # "Fridge_Combat",
        "Fyrestone_Combat",             # Loader Militar Mix
        "Grass_Cliffs_Combat",          # HyperionSoldier
        # "Grass_Combat",
        "Grass_Lynchwood_Combat",       # Miners, Skag Riders
        "IceCanyon_Combat",             # Flame Bandits
        # "Interlude_Combat",
        # "Outwash_Combat",
        "PandoraPark_Combat",           # Stalkers
        # "Sanctuary_Hole_Combat",
        # "SouthernShelf_Combat",
        "Stockade_Combat",              # Junk Loader
        "ThresherRaid_P",               # Terry
        "TundraExpress_Combat",         # Prospector
        # "VOGChamber_Combat",
        
    ],
    DLC.Torgue: [
        # "Iris_Hub_Combat",
        "Iris_DL3_P",                   # Forge Loaders
        "Iris_DL1_Battle",              # Arena Gangs
        #"Iris_Hub2_Combat",            # Monster Truck
        "Iris_DL2_Combat",              # Badass Biker Psycho
        #"Iris_DL2_Interior_Combat",
        #"Iris_DL1_TAS_Combat"
    ],
    DLC.Scarlett: [
        "Orchid_Refinery_Combat",       # ARR Loader
        "Orchid_OasisTown_Combat",      # NoBeard, Pirate Cursed
        "Orchid_Caves_Combat",          # Blue Crystalisks, Pirates
        "Orchid_Spire_P",               # Big Pirates, Mr Bubbles
        "Orchid_Spire_Dynamic",         # Scarlett Crew
        "Orchid_ShipGraveyard_Combat",  # Anchorman
        "Orchid_SaltFlats_Combat"       # Pirate Grenadier
        #"Orchid_WormBelly_Dynamic",     # Rakk Hive, Worms
    ],
    DLC.Hammerlock: [
        #"Sage_Cliffs_Combat",       # Elite Savages - but broken need something else, whatevs
        "Sage_PowerStation_P",
        "Sage_PowerStation_Combat",
        #"Sage_RockForest_Combat",
        #"Sage_Underground_Combat",
    ],
    DLC.DragonKeep: [
        "TempleSlaughter_P",        # Materials for knights
        "TempleSlaughter_Combat",
        "Dead_Forest_Combat",
        #"Docks_Combat",
        "Dungeon_Combat",
        #"Dungeon_Mission",          # Dead Brothers
        #"DungeonRaid_Combat",
        "Mines_Combat",
        "Mines_Dynamic",            # Flying Golem
        "Mines_Mission",            # Maxibillion, Broomstick
        #"CastleExterior_Combat",
        #"CastleKeep_Combat",
        #"Dark_Forest_P",            # Materials for treants
        #"Dark_Forest_Combat"
    ],
    DLC.Headhunters: [
        "Xmas_Combat",              # Snow Bandits
        "Xmas_Dynamic",             # Snow Psychos
        "Hunger_Boss",              # Tributes
        "Hunger_Dynamic",           # Incinerator Tribute
        "Hunger_Mission_1",         # ButcherBoss1-3, RatChef, Tributes
        "Hunger_Mission_2",         # Engineer Tributes
        "Hunger_Mission_3",         # ButcherBoss2-3, ButcherMidget
        #"Pumpkin_Patch_Combat",
        "Distillery_Dynamic",       # Special Threshers
        "Distillery_Mission",       # Hodunks and Zafords
        "Easter_Combat"             # Crabworms, Tropical Varkids
    ],
    DLC.FFS: [
        "BackBurner_P",             # Infected materials
        "BackBurner_Mission_Main",  # Infected materials
        "ResearchCenter_MissionMain",
        "ResearchCenter_MissionSide",
        "OldDust_Lair",             # Infected Bandits
        "OldDust_LD",               # Infected Goliath, Curse
        "OldDust_Mission_Main",
        "OldDust_Mission_Side",
        "Sandworm_Encounters",          # Infected Golem Badass
        "Sandworm_Mission_Side",
        "Helios_Mission_Main",
        "Helios_Mission_Side",
    ],
    DLC.Digistruct: [
        "TestingZone_Combat"
    ],
    DLC.TPS: [
        # NOTE Broken Textures:
        # Moon_Combat/Wreck_Combat breaks wall texture
        # Moon_SideMissions breaks floor texture
        
        # Eridians first to prevent broken Cheru/Opha FX
        "Eridian_slaughter_P",      # Wormhole generator
        "Eridian_slaughter_Combat", # Guardians and Eridians but different PopDefs than base game.
        "11B_Facility_A_Combat",    # Fanatics, Zealots, Guardians
        "InnerCore_combat00",       # Eridians
        "InnerCore_OPHATitleCard",  # Opha Superior
        
        # Moon_ first to prevent broken wall texture
        "Moon_Combat",              # Darksiders, Hives, ScavBadassBandit, ScavengerMix_Regular, Oscar
        #"Moon_SideMissions",        # Badass Hives - but breaks a floor texture, and they can only spawn in the map with this already loaded anyway.
        "Moonsurface_P",            # Kraggon Eruptor material
        "Moonsurface_Combat",       # Rock Kraggons, Zillas, Phonic, GrandsonFlamey
        #"MoonSlaughter_P",
        #"MoonSlaughter_Combat",     # GroundMix, RegularMix, BadassSpaceman, ScavNomad
        
        "Outlands_P",               # Spaceman Assets
        "Outlands_Combat",          # Ice Kraggons Small, SpitterBadass, CombatSpaceman
        "Outlands_P2",              # Tork Assets
        "Outlands_Combat2",         # Scav Jetriders, JetpackMix, WastelandWalker, Blowflys
        #"Wreck_P",                  # Spaceman Assets
        #"Wreck_Combat",             # BadassSpaceman, BadassBanditMidget, EliteBandit, Midget, SuicidePsycho
        "DahlFactory_P"             # Tork Assets
        "DahlFactory_Dynamic",      # Scav Rider Powersuit, Tork Assets
        "DahlFactory_Combat",       # ScavengerBandit_Jetpack, Scav Nomad, ScavPsychoMidget
        "DahlFactory_BossDynamic",  # Scav Powersuit, Bots
        
        "CentralTerminal_Dynamic",  # Bob, Dahl
        "RandDFacility_Dynamic",    # Badass Marine, Stalkers
        "InnerHull_P",              # Boil and Rat BodyTags
        "InnerHull_Combat",         # BoilMix, HypRatMix, Dahl, Jetfighters
        #"InnerHull_Mission",        # Boils, Rats, Lazlo
        "Laser_Dynamic",            # Power suits
        
    ],
    DLC.Claptastic: [
        "Ma_LeftCluster_P",         # Bandit and Missile FX
        "Ma_LeftCluster_Combat",    # Tassitrons
        "Ma_Subconscious_P",        # VI Clapdog FX
        "Ma_Subconscious_Game",     # Very Insecure Forces
        "Ma_SubBoss_Game",          # Everything else
        "Ma_FinalBoss_Game",        # Shadowtrap Clone, EOS
    ]
}


def GetCurrentDLC(PC) -> str:
    map_name = PC.WorldInfo.GetStreamingPersistentMapName()
    for DLC in levels_by_DLC:
        if map_name.lower() in [x.lower() for x in levels_by_DLC[DLC]]:
            return DLC
    return None


kept_alive_objects_by_class_name: dict = {}

def KeepAliveAllClass(class_name: str):
    objects = unrealsdk.FindAll(class_name)
    for object in objects:
        unrealsdk.KeepAlive(object)
    kept_alive_objects_by_class_name[class_name] = objects


def UnKeepAliveAllClass(class_name: str):
    objects = kept_alive_objects_by_class_name.pop(class_name)
    for object in objects:
        object.ObjectFlags.A &= ~0x4000     # Remove KeepAlive


loaded_DLCs = []

def LoadLevelSpawnObjects(DLC: DLC):
    global loaded_DLCs
    if DLC in loaded_DLCs:
        #Log(f"DLC {DLC.name} levels are already loaded!")
        return
    
    for package_name in combat_packages_by_DLC[DLC]:
        unrealsdk.LoadPackage(package_name)
        KeepAliveAllClass("WillowPopulationDefinition")
        KeepAliveAllClass("PopulationFactoryBalancedAIPawn")
        
        #unrealsdk.GetEngine().GetCurrentWorldInfo().ForceGarbageCollection(True)

    loaded_DLCs.append(DLC)
    
    
def UnloadLevelSpawnObjects():
    global loaded_DLCs
    if loaded_DLCs:
        UnKeepAliveAllClass("WillowPopulationDefinition")
        UnKeepAliveAllClass("PopulationFactoryBalancedAIPawn")
        loaded_DLCs = []
