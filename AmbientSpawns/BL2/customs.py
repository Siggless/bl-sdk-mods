from typing import Dict, List

from ..custom_spawns import Spawn, CustomSpawn, MultiSpawn, PoolSpawn, Tag
from ..level_packages import DLC

CUSTOM_SPAWNS: Dict[DLC, List[Spawn]] = {
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
            CustomSpawn("Friend",Tag.BADASS,                    popDef="GD_Population_Midget.Population.PopDef_MidgetBadass"),
            CustomSpawn("Goliaths",Tag.TOUGH,[1,2,3],[2,2,1],   popDef="GD_Population_Goliath.Population.PopDef_GoliathMix_Regular"),
            CustomSpawn("Big Goliath",Tag.BADASS,               popDef="GD_Population_Goliath.Population.PopDef_GoliathTurret"),
        ]),
        MultiSpawn("BBQ Time",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Pyro",Tag.CHUMP,                   factory="GD_Population_Bandit.Population.PopDef_BanditMix_IceCanyon:PopulationFactoryBalancedAIPawn_4"),
            CustomSpawn("Midgets",Tag.CHUMP,range(2,5),     popDef="GD_Population_Midget.Population.PopDef_FlamingMidget"),
            CustomSpawn("Fireburn Mix",Tag.CHUMP,range(1,4),popDef="GD_Population_Bandit.Population.PopDef_BanditMix_IceCanyon"),
        ]),
        
        PoolSpawn("Bandit Minibosses",Tag.MINIBOSS,customSpawnList=[    # Not allowed where they spawn normally
            CustomSpawn("Doc Mercy",Tag.MINIBOSS,popDef="GD_Population_Nomad.Population.Unique.PopDef_MrMercy", map_blacklist=["frost_p"]),
            CustomSpawn("Mad Mike 'boutta ruin your day",Tag.MINIBOSS,popDef="GD_Population_Nomad.Population.Unique.PopDef_MadMike", map_blacklist=["dam_p"]),
            CustomSpawn("Prospector",Tag.MINIBOSS,popDef="GD_Population_Nomad.Population.Unique.PopDef_Prospector", map_blacklist="tundraexpress_p"),
            MultiSpawn("Assassin Tagteam",Tag.BOSS,customSpawnList=[
                CustomSpawn("Ass Wot",Tag.MINIBOSS,     popDef="GD_Population_Marauder.Population.Unique.PopDef_Assassin1"),
                CustomSpawn("Ass Oney",Tag.MINIBOSS,    popDef="GD_Population_Nomad.Population.Unique.PopDef_Assassin2"),
                CustomSpawn("Ass Reeth",Tag.MINIBOSS,   popDef="GD_Population_Psycho.Population.Unique.PopDef_Assassin3"),
                CustomSpawn("Ass Rouf",Tag.MINIBOSS,    popDef="GD_Population_Rat.Population.Unique.PopDef_Assassin4"),
            ], map_blacklist=["southpawfactory_p"]),
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
        PoolSpawn("Helios ATTACKS!",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Regular Mix",Tag.TOUGH,range(8,15),popDef="GD_Population_Loader.Population.PopDef_LoaderMix_Regular"),
            CustomSpawn("Bunker Mix",Tag.TOUGH,range(6,13),popDef="GD_Population_Loader.Population.PopDef_LoaderMix_BunkerFight"),
        ], spawnPointDef="PopPointDef_OrbitalDrop"),
        MultiSpawn("Helios ATTACKS AGAIN",Tag.TOUGH,customSpawnList=[
            CustomSpawn("RPG",Tag.CHUMP,[2,3],[1,1],    popDef="GD_Population_Loader.Population.PopDef_LoaderRPG"),
            CustomSpawn("SGT",Tag.CHUMP,[2,3],[1,1],    popDef="GD_Population_Loader.Population.PopDef_LoaderSGT"),
            CustomSpawn("WAR",Tag.TOUGH,[1,2],[4,1],    popDef="GD_Population_Loader.Population.PopDef_LoaderWAR"),
        ]),
        CustomSpawn("Lookout! Badass Loaders",Tag.BADASS,[2,3,4],[7,4,1],popDef="GD_Population_Loader.Population.PopDef_LoaderBadass"),
        CustomSpawn("Big Boi Loader",Tag.ULTIMATE_BADASS,[1,2],[4,1],popDef="GD_Population_Loader.Population.PopDef_LoaderSuperBadass"),
        CustomSpawn("EXPlooooosions",Tag.CHUMP,range(5,11),[1,2,3,3,2,2],popDef="GD_Population_Loader.Population.PopDef_LoaderEXP"),
        CustomSpawn("LEEEEROYYYYY",Tag.BOSS,factory="GD_Population_Midget.Population.LootMidget.PopDef_LootMidget_HyperionMix:PopulationFactoryBalancedAIPawn_5",spawnPointDef="None"),
        MultiSpawn("Loaders+Surveyors",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Loaders",Tag.CHUMP,range(3,7),             popDef="GD_Population_Loader.Population.PopDef_LoaderMix_Military"),
            CustomSpawn("Badass Surveyor",Tag.BADASS,[1,2],[2,1],   popDef="GD_Population_Probe.Population.PopDef_ProbeMix_Badass"),
            CustomSpawn("Surveyors",Tag.CHUMP,range(2,5),           popDef="GD_Population_Probe.Population.PopDef_ProbeMix_Regular"),
        ]),
        MultiSpawn("Loaders+Engis",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Loaders",Tag.CHUMP,range(4,7),     popDef="GD_Population_Loader.Population.PopDef_LoaderMix_Regular"),
            CustomSpawn("EngiArms",Tag.CHUMP,range(1,3),    popDef="GD_Population_Engineer.Population.PopDef_EngineerArms"),
            CustomSpawn("EngiFleshy",Tag.CHUMP,range(1,3),  popDef="GD_Population_Engineer.Population.PopDef_Engineer"),
        ]),
        MultiSpawn("BlackOps",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Snipers",Tag.CHUMP,range(2,4),     popDef="GD_Population_Engineer.Population.PopDef_BlackOps"),
            CustomSpawn("Cloakers",Tag.CHUMP,range(2,4),    popDef="GD_Population_Engineer.Population.PopDef_HyperionInfiltrator"),
        ]),
        MultiSpawn("Assault",Tag.TOUGH,customSpawnList=[
            # Soldier needs allegiance to match the turrets so no den change
            CustomSpawn("Soldier",Tag.CHUMP,range(2,4),     popDef="GD_Population_Engineer.Population.PopDef_HyperionSoldier"),
            CustomSpawn("Rockets",Tag.CHUMP,range(1,3),     factory="GD_Population_Hyperion.Population.PopDef_HyperionMix_Fyrestone:PopulationFactoryBalancedAIPawn_4"),
        ]),
        MultiSpawn("Flying enemies are fun",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Jets",Tag.CHUMP,range(3,5),        popDef="GD_Population_Loader.Population.PopDef_LoaderJET"),
            CustomSpawn("Surveyors",Tag.CHUMP,range(2,5),   popDef="GD_Population_Probe.Population.PopDef_ProbeMix_Regular")
        ]),
        CustomSpawn("Wilhelm",Tag.BOSS,factory="GD_Population_Loader.Population.Unique.PopDef_Willhelm:PopulationFactoryBalancedAIPawn_1",spawnPointDef="None",map_blacklist=["tundratrain_p"]),
        
        # Fauna - some just basic mixes to pad so not only custom minibosses
        # Rakk attacks don't work in other maps for some reason
        #CustomSpawn("Release the Rakk!",Tag.CHUMP,[4,8],popDef="GD_Population_Rakk.Population.PopDef_Rakk",spawnPointDef="None"),
        #CustomSpawn("Bullymong Mix",Tag.CHUMP,range(4,7),popDef="GD_Population_PrimalBeast.Population.PopDef_PrimalBeastMix_Ash"),
        MultiSpawn("Thresher Mix",Tag.CHUMP,customSpawnList=[
            CustomSpawn("Threshers",Tag.CHUMP,range(4,7),   popDef="GD_Population_Thresher.Population.PopDef_ThresherMix_Regular"),
            CustomSpawn("Tentacles",Tag.CHUMP,range(4,7),   popDef="GD_Population_Thresher.Population.PopDef_TentacleMix_Regular")
        ]),
        CustomSpawn("Spiderant Mix",Tag.CHUMP,range(4,7),popDef="GD_Population_SpiderAnt.Population.PopDef_SpiderantMix_Regular"),
        CustomSpawn("Sponics",Tag.CHUMP,range(4,10),factory="GD_Population_SpiderAnt.Population.PopDef_SpiderantMix_Regular:PopulationFactoryBalancedAIPawn_2"),
        PoolSpawn("Stalker Mix",Tag.TOUGH,numPicks=4,customSpawnList=[
            CustomSpawn("Stalker",Tag.CHUMP,[1,2],          popDef="GD_Population_Stalker.Population.PopDef_Stalker"),
            CustomSpawn("Badass",Tag.BADASS,[1],            popDef="GD_Population_Stalker.Population.PopDef_StalkerBadass"),
            CustomSpawn("Ambush",Tag.ULTIMATE_BADASS,[1],   popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Ambush"),
            CustomSpawn("Cyclone",Tag.TOUGH,[1,2],         popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Cyclone"),
            CustomSpawn("Stalker",Tag.CHUMP,[1,2],          popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Needle"),
            CustomSpawn("Spring",Tag.CHUMP,[1,2],           popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Spring"),
        ], customSpawnWeights=[3,1,1,4,3,3]),
        
        CustomSpawn("Skag Mix",Tag.CHUMP,range(4,7),popDef="GD_Population_Skag.Population.PopDef_SkagMix_Regular"),
        MultiSpawn("Skag Ma & Pa",Tag.ULTIMATE_BADASS,customSpawnList=[
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
        CustomSpawn("Surprise Stalker",Tag.CHUMP,range(2,4),popDef="GD_Population_Stalker.Population.PopDef_StalkerMix_Cyclone",spawnPointDef="None"),
        CustomSpawn("Surprise Thresher",Tag.CHUMP,range(2,4),popDef="GD_Population_Thresher.Population.PopDef_ThresherMix_Regular",spawnPointDef="None"),
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
            CustomSpawn("Cursed",Tag.TOUGH,    popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateCursed"),
            CustomSpawn("Grenadier",Tag.CHUMP,  popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateGrenadier"),
            CustomSpawn("Hunter",Tag.CHUMP,     popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateHunter"),
            CustomSpawn("Marauder",Tag.CHUMP,   popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateMarauder"),
            CustomSpawn("Ninja",Tag.CHUMP,      popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PirateNinja"),
            CustomSpawn("Psycho",Tag.CHUMP,     popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_PiratePsycho"),
        ], customSpawnWeights=[2,3,5,5,5,5,5]),
        MultiSpawn("Large Lads",Tag.TOUGH,customSpawnList=[
            PoolSpawn("Large Lad",Tag.BADASS,customSpawnList=[
                CustomSpawn("Anchorman",Tag.BADASS, popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_AnchorMan"),
                CustomSpawn("Minelayer",Tag.BADASS, factory="GD_Orchid_Pop_Pirates.MapPopulations.PopDef_Orchid_SpireMix:PopulationFactoryBalancedAIPawn_14"),

            ]),
            PoolSpawn("Not-so-large Lads",Tag.TOUGH,numPicks=3,customSpawnList=[
                CustomSpawn("Whaler",Tag.TOUGH,    factory="GD_Orchid_Pop_Pirates.MapPopulations.PopDef_Orchid_SpireMix:PopulationFactoryBalancedAIPawn_12"),
                CustomSpawn("Buccaneer",Tag.TOUGH, popDef="GD_Orchid_Pop_Pirates.Population.PopDef_Orchid_SwordMan"),
            ])
        ]),
        MultiSpawn("Would you kindly harvest this midget",Tag.MINIBOSS,customSpawnList=[
            CustomSpawn("Mr Bubbles",Tag.MINIBOSS,  popDef="GD_Orchid_Pop_BubblesLilSis.Population.PopDef_Orchid_Bubbles"),
            CustomSpawn("Little Sis",Tag.MINIBOSS,  popDef="GD_Orchid_Pop_BubblesLilSis.Population.PopDef_Orchid_LittleSis"),
        ], map_blacklist=["orchid_spire_p"]),
        MultiSpawn("Scarlett Crew",Tag.ULTIMATE_BADASS,customSpawnList=[
            CustomSpawn("Lt. White",Tag.BADASS,         popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Orchid_PirateHenchman"),
            CustomSpawn("Lt. Hoffman",Tag.BADASS,       popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Orchid_PirateHenchman2"),
            CustomSpawn("Crew",Tag.TOUGH,range(1,4),   popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Betrayal_Mix"),
            CustomSpawn("Ninjas",Tag.TOUGH,range(1,3), popDef="GD_Orchid_Pop_ScarlettCrew.Population.PopDef_Orchid_ScarlettNinja"),
        ], map_blacklist=["orchid_spire_p"])
    ],
    
    DLC.Torgue: [
        CustomSpawn("Torgue Loaders",Tag.TOUGH,range(3,7),popDef="GD_Iris_Population_Loader.Population.PopDef_Iris_LoaderMix_Forge"),
        MultiSpawn("Arena Goliath & Friends",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Goliath",Tag.TOUGH,[1,2],[2,1],   popDef="GD_Iris_Population_Goliath.Population.PopDef_Iris_ArenaGoliath"),
            CustomSpawn("Psychos",Tag.CHUMP,range(0,2),     popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerMidget_Torgue"),
            CustomSpawn("Midgets",Tag.CHUMP,range(1,3),     popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BikerPsycho_Torgue"),
        ]),
        MultiSpawn("Momma's Gang",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Enforcer",Tag.TOUGH,[1,2],[2,1],  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBiker_Angels"),
            CustomSpawn("Angel Mix",Tag.TOUGH,range(2,6),  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Gang_AngelsMix"),
        ]),
        MultiSpawn("Burner Gang",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Enforcer",Tag.TOUGH,[1,2],[2,1],  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBiker_Dragon"),
            CustomSpawn("Demon Mix",Tag.TOUGH,range(2,6),  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Gang_DragonMix"),
        ]),
        MultiSpawn("Torgue Gang",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Enforcer",Tag.TOUGH,[1,2],[2,1],  popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_BigBiker_Torgue"),
            CustomSpawn("Torgue Mix",Tag.TOUGH,range(2,6), popDef="GD_Iris_Population_Biker.Gangs.PopDef_Iris_Biker_Gang_TorgueMix"),
        ]),
    ],
    
    DLC.Hammerlock: [
        CustomSpawn("Elite Savages",Tag.ULTIMATE_BADASS,[2,3,4],[1,2,2],popDef="GD_Sage_Pop_Natives.Population.PopDef_Native_Elite"),
        CustomSpawn("Spore Pinata Party",Tag.CHUMP,[3,4,5],popDef="GD_Sage_Pop_Spore.Population.PopDef_Sage_GiantSpore_Mix",spawnPointDef="None"),
        MultiSpawn("Surprise Scaylions",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Champion",Tag.BADASS,      popDef="GD_Sage_Pop_Scaylion.Population.PopDef_Sage_ScaylionMix_Champion",spawnPointDef="None"),
            CustomSpawn("Mix",Tag.CHUMP,range(2,5), popDef="GD_Sage_Pop_Scaylion.Population.PopDef_Sage_ScaylionMix_Regular",spawnPointDef="None"),
        ], spawnPointDef="None"),
        MultiSpawn("Surprise Boraks",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Badass",Tag.BADASS,        popDef="GD_Sage_Pop_Rhino.Population.PopDef_RhinoMix_Badass",spawnPointDef="None"),
            CustomSpawn("Baby",Tag.CHUMP,range(2,5),popDef="GD_Sage_Pop_Rhino.Population.PopDef_Sage_RhinoBaby",spawnPointDef="None"),
        ], spawnPointDef="None")
    ],
    
    DLC.DragonKeep: [
        # Orcs
        CustomSpawn("Handsome Tower ATTACKS!",Tag.TOUGH,range(6,15),popDef="GD_Aster_Pop_Orcs.Population.PopDef_OrcsDen_Regular",spawnPointDef="PopPointDef_Orc_OrbitalDrop"),
        CustomSpawn("Orcsplooooosions",Tag.CHUMP,range(5,11),[1,2,3,3,2,2],popDef="GD_Aster_Pop_Orcs.Population.PopDef_OrcsDen_Kamikaze"),
        MultiSpawn("Orc Warlord Party",Tag.ULTIMATE_BADASS,customSpawnList=[
            PoolSpawn("Warlord",Tag.ULTIMATE_BADASS,customSpawnList=[
                #CustomSpawn("Grug",Tag.ULTIMATE_BADASS,popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_WarlordGrug"),
                CustomSpawn("Slog",Tag.ULTIMATE_BADASS,popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_WarlordSlog"),
                CustomSpawn("Turge",Tag.ULTIMATE_BADASS,popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_WarlordTurge")
            ]),
            CustomSpawn("Grunts",Tag.CHUMP,range(2,6),popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_Grunt"),
            CustomSpawn("Bashers",Tag.CHUMP,range(1,4),popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orc_Basher"),
            CustomSpawn("Zerkers",Tag.TOUGH,range(0,3),popDef="GD_Aster_Pop_Orcs.Population.PopDef_Orczerker"),
        ]),
        # Spiders
        MultiSpawn("Arachne Hunting Party",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Reapers",Tag.TOUGH,range(4,8),    popDef="GD_Aster_Pop_Spiders.Population.PopDef_Arachne"),
            CustomSpawn("Minions",Tag.CHUMP,range(4,8),     popDef="GD_Aster_Pop_Spiders.Population.PopDef_SpiderDen_Regular")
        ]),
        # CBA load Dark Forest and fix stumpy materials just for this
        #CustomSpawn("Pixie",Tag.BOSS,popDef="GD_Aster_Pop_Wisp.Population.PopDef_Aster_Wisp",spawnPointDef="None"),
        # Knights
        MultiSpawn("Target Practise",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Badass Archer",Tag.BADASS,popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_BadassFireArcher"),
            CustomSpawn("Archers",Tag.CHUMP,range(2,5),popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_Archer")
        ]),
        MultiSpawn("Paladins",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Paladins",Tag.TOUGH,[3],popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_Paladin"),
            CustomSpawn("Chumps",Tag.CHUMP,range(3,7),popDef="GD_Aster_Pop_Knights.Population.PopDef_KnightsDen_Regular")
        ]),
        CustomSpawn("It's time to CLEAN THE FLOOR WITH YOU",Tag.BOSS,range(5,11),popDef="GD_Aster_Pop_Knights.Population.PopDef_Knight_Broomstick",spawnPointDef="None"),
        # Skeletons
        MultiSpawn("Immortals",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Immortal",Tag.TOUGH,[3],popDef="GD_Aster_Pop_Skeletons.Population.PopDef_SkeletonImmortal"),
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
        ], map_blacklist="dead_forest_p"),
        # Wizards
        CustomSpawn("Wizards",Tag.TOUGH,[2,3],[3,1],popDef="GD_Aster_Pop_Wizards.Population.PopDef_WizardsDen_Regular"),
        CustomSpawn("AbracaMAGIC",Tag.BADASS,popDef="GD_Aster_Pop_Wizards.Population.PopDef_WizardsDen_Badass"),
        # MultiSpawn("Familial Reconciliation",Tag.MINIBOSS,customSpawnList=[
        #     CustomSpawn("Edgar",Tag.MINIBOSS,popDef="GD_Aster_Pop_Wizards.Population.PopDef_Wizard_DeadBrotherEdgar"),
        #     CustomSpawn("Simon",Tag.MINIBOSS,popDef="GD_Aster_Pop_Wizards.Population.PopDef_Wizard_DeadBrotherSimon"),
        # ]),
        # Mines
        CustomSpawn("Dwarfzerkers",Tag.CHUMP,range(4,7),popDef="GD_Aster_Pop_Dwarves.Population.PopDef_Dwarfzerker"),
        MultiSpawn("Golem Wranglers",Tag.TOUGH,customSpawnList=[
            PoolSpawn("Golem Choice",Tag.TOUGH,customSpawnList=[
                CustomSpawn("Golem",Tag.TOUGH,         popDef="GD_Aster_Pop_Golems.Population.PopDef_GolemRock",spawnPointDef="None"),
                CustomSpawn("Badass Golem",Tag.BADASS,  popDef="GD_Aster_Pop_Golems.Population.PopDef_Golem_Badass",spawnPointDef="None"),
            ], customSpawnWeights=[2,1], spawnPointDef="None"),
            CustomSpawn("Dwarfs",Tag.CHUMP,range(3,6),  popDef="GD_Aster_Pop_Dwarves.Population.PopDef_DwarfsDen_Regular",spawnPointDef="None"),
            CustomSpawn("Badass Dwarf",Tag.BADASS,[0,1],popDef="GD_Aster_Pop_Dwarves.Population.PopDef_Dwarf_Badass",spawnPointDef="None")
        ], spawnPointDef="None"),
        CustomSpawn("Flying Golems",Tag.TOUGH,range(2,5),popDef="GD_Aster_Pop_Golems.Population.PopDef_GolemFlying"),
        CustomSpawn("Maxibillion",Tag.MINIBOSS,popDef="GD_Aster_Pop_Golems.Population.PopDef_GolemFlying_Maxibillion"),
    ],
    
    DLC.FFS: [
        CustomSpawn("Sanctuary ATTACKS!",Tag.TOUGH,range(4,11),popDef="GD_Anemone_InfectedPodTendril.Population.PopDef_InfectedPodTendril",spawnPointDef="PopPointDef_OrbitalDrop_Infection_Test"),
        MultiSpawn("Golem Skag Walking Service",Tag.TOUGH,customSpawnList=[
            CustomSpawn("Golem",Tag.BADASS,popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedGolem_Badass",spawnPointDef="None"),
            CustomSpawn("Skags",Tag.CHUMP,range(3,6),popDef="GD_Anemone_Pop_WildLife.Population.PopDef_Infected_SkagMIX",spawnPointDef="None"),
        ], spawnPointDef="None"),
        PoolSpawn("Sentient Mutating Funguys In My Grill",Tag.TOUGH,numPicks=4,customSpawnList=[
            CustomSpawn("Bruisers",Tag.TOUGH,[1,2],    popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedBruiser"),
            CustomSpawn("Psychos",Tag.CHUMP,[1,2],      popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedCurse"),
            CustomSpawn("Suiciders",Tag.CHUMP,[1,2],    popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedCurse"),
            CustomSpawn("Midgets",Tag.CHUMP,[1,2],      popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedMidget"),
            CustomSpawn("Goliath",Tag.TOUGH,[1],       popDef="GD_Anemone_Pop_Infected.Population.PopDef_InfectedGoliath"),
        ], customSpawnWeights=[3,3,2,3,1]),
        PoolSpawn("New Pandora Chumps",Tag.TOUGH,numPicks=4,customSpawnList=[
            CustomSpawn("Flamer",Tag.CHUMP,[1,2],       factory="GD_Anemone_Pop_NP.Population.PopDef_NewPandoraMix_Basic:PopulationFactoryBalancedAIPawn_4"),
            CustomSpawn("Commander",Tag.TOUGH,[1,2],   popDef="GD_Anemone_Pop_NP.Population.PopDef_NP_Commander"),
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
        ], map_blacklist=["olddust_p"]),
        CustomSpawn("Cassius",Tag.BOSS,popDef="GD_Anemone_Pop_Cassius.GD_Anemone_PopDef_Cassius",spawnPointDef="None",map_blacklist=["ResearchCenter_P"]),
        
        CustomSpawn("Surprise Infected Pods",Tag.TOUGH,range(3,8),popDef="GD_Anemone_InfectedPodTendril.Population.PopDef_InfectedPodTendril",spawnPointDef="None"),
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
        ], map_blacklist=["hunger_p"]),
        PoolSpawn("Love Thresher",Tag.MINIBOSS,customSpawnList=[
            CustomSpawn("Blue",Tag.BADASS,     popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherBlue", spawnPointDef="None"),
            CustomSpawn("Green",Tag.TOUGH,    popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherGreen", spawnPointDef="None"),
            CustomSpawn("Orange",Tag.BOSS,     popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherOrange", spawnPointDef="None"),
            CustomSpawn("Purple",Tag.MINIBOSS, popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherPurple", spawnPointDef="None"),
            CustomSpawn("White",Tag.CHUMP,     popDef="GD_Nast_ThresherShared.Population.PopDef_Nast_ThresherWhite", spawnPointDef="None"),
        ], map_blacklist=["Distillery_P"], spawnPointDef="None"),
        MultiSpawn("Crabworms",Tag.CHUMP,customSpawnList=[
            CustomSpawn("Craboid",Tag.CHUMP,range(0,3),     popDef="GD_Population_Crabworms.Population.PopDef_Craboid"),
            CustomSpawn("CraboidGiant",Tag.TOUGH,[0,1],    popDef="GD_Population_Crabworms.Population.PopDef_CraboidGiant"),
            CustomSpawn("Crabworm",Tag.CHUMP,range(1,4),    popDef="GD_Population_Crabworms.Population.PopDef_Crabworm"),
            CustomSpawn("Crawthumper",Tag.CHUMP,range(0,4), popDef="GD_Population_Crabworms.Population.PopDef_CrawThumper"),
        ])
    ],
    
    DLC.Digistruct: [
    ]
}
