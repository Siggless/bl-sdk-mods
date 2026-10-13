from typing import List

"""
Blacklists to exclude spawning in boss maps and slaughters,
 and exclude static enemies like turrets.
"""

BLACKLIST_MAPS: List[str] = [
    "menumap",
    "MoonSlaughter_P",
    "MoonShotIntro_P",
    "Spaceport_P",
    "LaserBoss_P",
    "JacksOffice_P",
    "Meriff_P",
    "Digsite_Rk5arena_P",
    "Ma_Deck13_P",
    "Ma_SubBoss_P",
    "Ma_FinalBoss_P",
    "Eridian_slaughter_P"
]
"""Maps where it doesn't make sense to have ambient spawns, or where they cause problems"""

BLACKLIST_POPDEFS: List[str | None] = [
    None,
    "PopDef_SonFlamey",
    "PopDef_UniqueCharger",
    "PopDef_MoonBuggy_Laser_Scav",
    "PopDef_MoonBuggy_Missile_Scav",
    "PopDef_ScavSuicidePsycho_Oscar",
    "PopDef_DanZando",
    "PopDef_Clap_L3K",
    "PopDef_FBCBig_GuardianMinions",    # Final boss arena
    "PopDef_ClapForces_GroundMix_NexQuar",  # Nexus quarantine zone
    "PopDef_ClapTurret",
    "PopDef_ClapTurret_Missile",
]
"""Static enemies or minibosses that aren't caught, or dens that we want to exclude"""

BLACKLIST_ALLEGIANCES = [
    "Allegiance_Player",
    "Allegiance_NPCNeutral",
    "Allegiance_MissionNPC",
    "Allegiance_Proto_Loader_Coward",
    "Allegiance_Proto_Loader_Ally"
]
"""Allegiances for NPCs that we should never spawn (i.e. non-enemies)"""

BLACKLIST_GAME_STAGES: List[str] = [
    "Outlands_B",   # Rabid Adams friendly tork and threshers.
    "MoonSurface_Side_C_Late",  # High level side-quest spawns in Crisis Scar - also affects Captain Chef den
    "Raid",
]
"""To exclude dens that set enemy levels much higher than the player (TPS's Nel fight, BL2's Dexi mobs)"""

POPDEF_PREFIX_EXCLUDED_FROM_FOV_CHECKS = [
    "PopDef_Stalker",
    "PopDef_Thresher",
]
"""Enemies that spawn cloaked so look OK in view"""

FACTORY_EXCLUDED_FROM_ALLEGIANCE_CHANGE = [
    "GD_Population_Scavengers.Balance.Outlaws.PawnBalance_ScavWastelandWalker",
]
"""Enemies whose allegiance is important e.g. Wilhelm needs to match his surveyors"""