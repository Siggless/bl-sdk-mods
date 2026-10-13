from typing import List

"""
Blacklists to exclude spawning in boss maps and slaughters,
 and exclude static enemies like turrets.
"""

BLACKLIST_MAPS: List[str] = [
    "menumap",
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
]
"""Maps where it doesn't make sense to have ambient spawns, or where they cause problems"""

BLACKLIST_POPDEFS: List[str | None] = [
    None,
    "PopDef_Rakk",  # Having other enemies spawn in the air is just too janky
    "PopDef_RakkMix_Regular",
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
    "PopDef_Orchid_LoaderBUL_Disabled",
    "PopDef_Orchid_LoaderGUN_Disabled",
    "PopDef_Orchid_LoaderHOT_Disabled",
    "PopDef_Orchid_LoaderJunk_Disabled",
    "PopDef_Orchid_LoaderPWR_Disabled",
    "PopDef_Orchid_PirateRadioGuy",
    "PopDef_Iris_RakkMix_Crater",
    "PopDef_Iris_BikeWithMotorMama",
    "PopDef_Iris_RaidMamaSupportBike",
    "PopDef_Iris_BikeWithDriverAndSidecarMix",  # Motor Mama arena sides
    "PopDef_DrifterRaid",
    "PopDef_Treant_StandStill",
    "PopDef_DwarfsDen_StandStill",
    "PopDef_Knight_Archer_StandStill",
    "PopDef_Knight_BadassFireArcher_Standstill",
    "PopDef_SkeletonArcher_StandStill",
    "PopDef_SkeletonArcherMage_StandStill",
    "PopDef_FlamingSkull",
    "PopDef_Skeleton_DeadBrother",
    "PopDef_Mimic",
    "PopDef_Anemone_AutoCannon",
]
"""Static enemies or minibosses that aren't caught, or dens that we want to exclude"""

BLACKLIST_ALLEGIANCES = [
    "Allegiance_Player",
    "Allegiance_NPCNeutral",
    "Allegiance_MissionNPC",
    "Allegiance_Treant_Friendly",
    "Allegiance_Wisp"
]
"""Allegiances for NPCs that we should never spawn (i.e. non-enemies)"""

BLACKLIST_GAME_STAGES: List[str] = [
    "Anemone_RaidBoss",
    "Aster_Raid",
    "Iris_Raid",
    "Orchid_Raid",
    "Sage_Raid",
    "ThresherRaid",
]
"""To exclude dens that set enemy levels much higher than the player (TPS's Nel fight, BL2's Dexi mobs)"""

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
    "GD_Population_Hyperion.Population.PopDef_HyperionMix_Fyrestone:PopulationFactoryBalancedAIPawn_4",  # Is fine, but grouped with soldier for a CustomSpawn
    "GD_Aster_Pop_Golems.Population.PopDef_GolemRock:PopulationFactoryBalancedAIPawn_0",
    "GD_Aster_Pop_Golems.Population.PopDef_Golem_Badass:PopulationFactoryBalancedAIPawn_0",
    "GD_Anemone_Pop_Infected.Population.PopDef_InfectedGolem_Badass:PopulationFactoryBalancedAIPawn_0",
]
"""Enemies whose allegiance is important e.g. Wilhelm needs to match his surveyors"""