from typing import Dict, List

from ..custom_spawns import Spawn, CustomSpawn, MultiSpawn, PoolSpawn, Tag
from ..level_packages import DLC

CUSTOM_SPAWNS: Dict[DLC, List[Spawn]] = {
    DLC.TPS: [
        CustomSpawn("Shy Shuggy",Tag.TOUGH,popDef="GD_Population_HiveFlyer.Population.PopDef_HiveMind",spawnPointDef="PopDef_HiveFlyerRodunk"),
        PoolSpawn("Badass Shuggy",Tag.BADASS,customSpawnList=[
            CustomSpawn("Fire",Tag.BADASS,popDef="GD_Population_HiveFlyer.Population.PopDef_BadassHive"),
            CustomSpawn("Cryo",Tag.BADASS,popDef="GD_Population_HiveFlyer.Population.PopDef_GiantCryoHive"),
        ]),
        
        MultiSpawn("An actually-fun amount of Kraggons",Tag.CHUMP,customSpawnList=[
            PoolSpawn("Pebbles",Tag.CHUMP,numPicks=3,customSpawnList=[
                CustomSpawn("Rock",Tag.CHUMP,[2,3], popDef="GD_Cork_Population_EleBeast.Population.PopDef_FrostBeast_Small"),
                CustomSpawn("Frost",Tag.CHUMP,[2,3],popDef="GD_Cork_Population_EleBeast.Population.PopDef_Frostbeast_Mini"),
            ]),
            PoolSpawn("Kraggon",Tag.CHUMP,numPicks=2,customSpawnList=[
                CustomSpawn("Rock",Tag.CHUMP,[1,2], popDef="GD_Cork_Population_EleBeast.Population.PopDef_ElementalBeast"),
                CustomSpawn("Frost",Tag.CHUMP,[1,2],popDef="GD_Cork_Population_EleBeast.Population.PopDef_FrostBeast"),
            ]),
        ]),
        CustomSpawn("Kraggon Badass",Tag.BADASS,popDef="GD_Cork_Population_EleBeast.Population.PopDef_ElementalSpitterBadass"),
        PoolSpawn("Kraggon Family Tree",Tag.BADASS,numPicks=3,customSpawnList=[
            CustomSpawn("Charger",Tag.BADASS,   popDef="GD_Cork_Population_EleBeast.Population.PopDef_ElementalCharger"),
            CustomSpawn("Immolator",Tag.TOUGH, popDef="GD_Cork_Population_EleBeast.Population.PopDef_ElementalSpitter"),
            CustomSpawn("Avalanche",Tag.TOUGH, popDef="GD_Cork_Population_EleBeast.Population.PopDef_FrostBeast"),
            CustomSpawn("Eruptor",Tag.BADASS,   popDef="GD_Cork_Population_EleBeast.Population.PopDef_ElementalMama"),
        ]),
        PoolSpawn("Kraggon-zilla",Tag.BOSS,customSpawnList=[
            CustomSpawn("Volcantis",Tag.BOSS,   popDef="GD_Cork_Population_EleBeast.Population.PopDef_Lavazilla"),
            CustomSpawn("Odjurymir",Tag.BOSS,   popDef="GD_Cork_Population_EleBeast.Population.PopDef_Frostzilla"),
            CustomSpawn("Iwajira",Tag.BOSS,     popDef="GD_Cork_Population_EleBeast.Population.PopDef_Rockzilla"),
            CustomSpawn("Phonic",Tag.MINIBOSS,  popDef="GD_Cork_Population_EleBeast.Population.PopDef_ElementalPhonic"),
        ]),
        
        MultiSpawn("Rocketmen",Tag.CHUMP,customSpawnList=[
            CustomSpawn("Suiciders",Tag.CHUMP,range(3,7),   popDef="GD_Population_Scavengers.Population.PopDef_ScavSuicidePsycho"),
            CustomSpawn("Oscar",Tag.CHUMP,[0,1],[2,1],      popDef="GD_Population_Scavengers.Population.PopDef_ScavSuicidePsycho_Oscar"),
        ]),
        PoolSpawn("Spacemen",Tag.BADASS,numPicks=3,customSpawnList=[
            CustomSpawn("Badass",Tag.BADASS,    popDef="GD_Population_Scavengers.Population.PopDef_BadassSpaceman"),
            CustomSpawn("Armored",Tag.BADASS,   popDef="GD_Population_Scavengers.Population.PopDef_ScavCombatSpaceman"),
            #CustomSpawn("Midget",Tag.MEDIUM,    popDef="GD_Population_Scavengers.Population.PopDef_ScavMidgetSpaceman"),
            CustomSpawn("Midget",Tag.TOUGH,    factory="GD_Population_Scavengers.Mixes.PopDef_ScavGroundMix_Spacemen:PopulationFactoryBalancedAIPawn_19"),
            CustomSpawn("Ground",Tag.TOUGH,    popDef="GD_Population_Scavengers.Population.PopDef_ScavNomad"),
        ],customSpawnWeights=[1,3,4,2]),
        MultiSpawn("Welcome to the Darkside",Tag.BADASS,customSpawnList=[
            CustomSpawn("Acolytes",Tag.CHUMP,numSpawns=range(4,8),popDef="GD_Population_Scavengers.Mixes.PopDef_ScavGroundMix_Darksiders"),
            PoolSpawn("Badass Bandit",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Fair Diknum",Tag.MINIBOSS,[0,1],[2,3], popDef="GD_Population_Darksiders.Population.PopDef_DarksiderBadassPsycho"),
                CustomSpawn("Wally Wrong",Tag.MINIBOSS,[0,1],[2,3], popDef="GD_Population_Darksiders.Population.PopDef_BadassDarksiderBandit"),
                CustomSpawn("Magma Rivers",Tag.MINIBOSS,[0,1],[2,3],popDef="GD_Population_Darksiders.Population.PopDef_LittleDarksiderBadassBandit"),
            ]),
        ]),
        
        MultiSpawn("Lost Legion Squad",Tag.TOUGH,customSpawnList=[
            PoolSpawn("Leader",Tag.BADASS,customSpawnList=[
                CustomSpawn("Bob",Tag.MINIBOSS,     popDef="GD_Population_Dahl.Population.PopDef_DahlMarine_CentralTerm"),
                CustomSpawn("Sergeant",Tag.TOUGH,  popDef="GD_Population_Dahl.Population.PopDef_DahlSergeant"),
                CustomSpawn("Badass",Tag.BADASS,    popDef="GD_Population_Dahl.Population.PopDef_BadassDahlMarine"),
            ]),
            CustomSpawn("Squaddies",Tag.CHUMP,numSpawns=range(5,8),popDef="GD_Population_Dahl.Population.PopDef_DahlMix_NoPowerSuits"),
        ],map_blacklist=["innercore_p"]),
        
        MultiSpawn("Boils",Tag.CHUMP,customSpawnList=[
            CustomSpawn("Boils",Tag.CHUMP,range(3,6),  popDef="GD_Population_Boils.Population.PopDef_BoilMix_All"),
            CustomSpawn("Guards",Tag.CHUMP,range(3,6), popDef="GD_Population_Boils.Population.PopDef_HypRatMix"),
        ]),
        
        # Holodome enemies are just going in the base game...
        PoolSpawn("Power Suits",Tag.BADASS,customSpawnList=[
            CustomSpawn("Scav",Tag.BADASS,range(1,4),[3,3,1],   popDef="GD_Population_Scavengers.Population.PopDef_ScavPowerSuit"),
            CustomSpawn("Dahl",Tag.BADASS,range(1,4),[3,3,1],   popDef="GD_Population_Dahl.Squads.PopDef_PowerSuitMix_Laser"),
            CustomSpawn("Eternal",Tag.BADASS,range(1,4),[3,3,1],popDef="GD_Pet_Population_Dahl.Mixes.PopDef_Mix_EternalPowersuits"),
        ]),
        CustomSpawn("This is Pondorous, man...",Tag.BADASS,range(2,5),[3,3,1],popDef="GD_Pet_Population_Guardians.Population.PopDef_GuardianPondor"),
        MultiSpawn("Eridian Incursion",Tag.BADASS,customSpawnList=[
            PoolSpawn("Bosses",Tag.MINIBOSS,customSpawnList=[
                CustomSpawn("Opha Superior",Tag.MINIBOSS,[0,1], popDef="GD_Population_Eridian_OphaBoss.Population.PopDef_Eridian_OphaBoss"),
                CustomSpawn("Virtuous Opha",Tag.BADASS,         popDef="GD_Population_Eridian_Opha.Population.PopDef_Opha_BadAss"),
            ]),
            PoolSpawn("Badasses",Tag.BADASS,numPicks=2,customSpawnList=[
                CustomSpawn("Elder Opha",Tag.BADASS,        popDef="GD_Population_Eridian_Opha.Population.PopDef_Opha_Heavy"),
                CustomSpawn("Virutous Opha",Tag.BADASS,     popDef="GD_Population_Guardians.Opha.Population.PopDef_Virtuous_Opha"),
                CustomSpawn("Cheru",Tag.BADASS,[1,2],       popDef="GD_Population_Guardians.Cheru.Population.PopDef_Cheru_BadAss"),
                CustomSpawn("Sara",Tag.BADASS,[1,2],        popDef="GD_Population_Guardians.Sera.Population.PopDef_Sara_Badass"),
                CustomSpawn("Arch Guardian",Tag.BADASS,     popDef="GD_Population_Guardians.Sera.Population.PopDef_Arch_Guardian"),
                CustomSpawn("Pondor",Tag.BADASS,[1,2],[1,2],popDef="GD_Pet_Population_Guardians.Population.PopDef_GuardianPondor"),
            ]),
            PoolSpawn("Chumps",Tag.CHUMP,customSpawnList=[
                CustomSpawn("Cheru",Tag.CHUMP,range(3,6),   popDef="GD_Population_Guardians.Cheru.Population.PopDef_Cheru"),
                CustomSpawn("Reaper",Tag.CHUMP,range(3,5),  popDef="GD_Population_Guardians.Cheru.Population.PopDef_Guardian_Reaper"),
                CustomSpawn("Wraith",Tag.CHUMP,range(3,5),  popDef="GD_Population_Guardians.Cheru.Population.PopDef_Guardian_Wraith"),
                CustomSpawn("Sara",Tag.CHUMP,range(3,6),    popDef="GD_Population_Guardians.Sera.Population.PopDef_Sara"),
            ]),
        ])
    ],
    DLC.Claptastic: [
        MultiSpawn("Release the DAWGS",Tag.CHUMP,customSpawnList=[
            CustomSpawn("Puppy",Tag.CHUMP,range(4,9),   popDef="GD_Ma_Pop_ClaptrapForces.Population.PopDef_ClapPuppy"),
            CustomSpawn("Dawg",Tag.CHUMP,[1,2],[3,1],   popDef="GD_Ma_Pop_ClaptrapForces.Population.PopDef_ClapDawg"),
            CustomSpawn("Badass",Tag.BADASS,[0,1],      popDef="GD_Ma_Pop_ClaptrapForces.Population.PopDef_BadassClapDawg"),
        ]),
        MultiSpawn("Tassitrons",Tag.TOUGH,customSpawnList=[
            CustomSpawn("BlackOps",Tag.CHUMP,range(1,4),    popDef="GD_Ma_Pop_Engineer.Population.PopDef_BlackOps"),
            CustomSpawn("Engineer",Tag.CHUMP,range(2,5),    popDef="GD_Ma_Pop_Engineer.Population.PopDef_Engineer"),
            CustomSpawn("EngineerArms",Tag.CHUMP,range(2,5),popDef="GD_Ma_Pop_Engineer.Population.PopDef_EngineerArms"),
        ]),
        CustomSpawn("ShadowClone",Tag.MINIBOSS,range(3,6),  popDef="GD_Ma_Pop_ClaptrapForces.Population.Uniques.PopDef_ShadowClone_Eos"),
    ],
}
