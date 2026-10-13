from typing import List

MEGAMIX_SUBSTITUTION_POOLS: List[List[str]] = [
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
        "GD_Population_Psycho.Population.PopDef_PsychoMix_Regular:PopulationFactoryBalancedAIPawn_32",
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
        "GD_Population_Nomad.Population.PopDef_NomadMix_Regular:PopulationFactoryBalancedAIPawn_3",
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
    [   # Crystalisk with Blue Crystalisk
        "GD_Population_Crystalisk.Population.PopDef_CrystaliskMix_Regular:PopulationFactoryBalancedAIPawn_1",
        "GD_Orchid_Pop_Crystalisk.Population.PopDef_Orchid_CrystaliskAqua:PopulationFactoryBalancedAIPawn_1",
    ]
]