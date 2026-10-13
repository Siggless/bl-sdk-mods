from ue_timers import UnrealTimer
from unrealsdk.logging import dev_warning
from unrealsdk.unreal import UObject
from mods_base import get_pc, Game

from typing import List, Tuple
PopulationFactoryBalancedAIPawn = UObject
PopulationOpportunityDen = UObject
WillowPopulationPoint = UObject
WillowPlayerController = UObject
SpawnItem = Tuple[PopulationFactoryBalancedAIPawn, WillowPopulationPoint, float]

if Game.get_current() == Game.TPS:
    from .TPS.blacklists import FACTORY_EXCLUDED_FROM_ALLEGIANCE_CHANGE
else:
    from .BL2.blacklists import FACTORY_EXCLUDED_FROM_ALLEGIANCE_CHANGE


class Spawner():
    """
    Since in the worst case we will be spawning many enemies from a single spawn point,
     we add a delay between each spawn using another UE Timer.
    """
    
    def __init__(self) -> None:
        self.isSpawning: bool = False
        self.SPAWN_TIMER: UnrealTimer = UnrealTimer(self.SpawnNext)
        self.spawnDen: PopulationOpportunityDen
        self.spawnList: List[SpawnItem] = []
        self.targetPlayer: bool = False


    def StartSpawning(self, spawnDen: PopulationOpportunityDen, spawnList: List[SpawnItem], targetPlayer: bool):
        self.isSpawning = True
        self.spawnDen = spawnDen
        self.spawnList = spawnList
        self.targetPlayer = targetPlayer
        dev_warning("[AmbientSpawns] -----Spawning STARTING-----")
        self.SpawnNext()
    
    
    def StopSpawning(self):
        self.isSpawning = False
        if self.SPAWN_TIMER.is_running():
            self.SPAWN_TIMER.stop()
        dev_warning("[AmbientSpawns] -----Spawning OVER-----")


    def SpawnNext(self):
        (factory, spawn, delay) = self.spawnList.pop(0)
        
        if len(self.spawnList) == 0:
            self.StopSpawning()
        
        if not factory or not spawn:
            return

        # Try not to spawn enemies on top of eachother by adjusting the delay
        if len(self.spawnList) > 0:
            if spawn is self.spawnList[0][1]:
                delay = delay + 3
            if self.SPAWN_TIMER.is_running():
                self.SPAWN_TIMER.update(delay, True)
            else:
                self.SPAWN_TIMER.start(delay, True)
        
        den = self.spawnDen
        
        PC = get_pc()
        gameStage = GetGameStage(PC, den)
        popMaster = PC.GetWillowGlobals().GetPopulationMaster()
        
        if spawn.StretchyActor:
            # Fix up the Helios spawn anim and other orbital ones
            loc = spawn.StretchyActor.Location
            rot = spawn.StretchyActor.Rotation
        else:
            loc = spawn.Location
            rot = spawn.Rotation
        
        # This function ensures that the spawns are destroyed on map change
        spawnedPawn = popMaster.SpawnActorFromOpportunity(
            factory,
            den,
            loc, rot,
            gameStage, 1,
            0, 0,    # Setting oppIndex from GetOpportunityIndex crashes sometimes
            False, False
        )
        
        if not spawnedPawn:
            return
        
        # Play the SpecialMove spawn animation
        spawn.ActorSpawned(spawnedPawn)
        spawnedPawn.MySpawnPoint = spawn    # Orbital drop ground shake and spawn anims
        
        # If it's the Infected Pods then rotate them to try and stop them overlapping in the same point
        if factory.PathName(factory).startswith("GD_Anemone_InfectedPodTendril.Population.PopDef_InfectedPodTendril"):
            rot.Yaw = len(self.spawnList) * 7000
            spawnedPawn.Rotation = rot
        
        # Prevent different allegiance enemies attacking eachother from the same den
        if factory.PathName(factory) not in FACTORY_EXCLUDED_FROM_ALLEGIANCE_CHANGE:
            spawnedPawn.SetAllegiance(den.GetAllegiance())
        
        if mind:= spawnedPawn.MyWillowMind:    # I.E. not a vehicle
            # Set OppIndex for GetPopOpDen, to get the random patrol points working
            mind.PopulationOpportunityIndex = popMaster.GetPopulationOpportunityIndex(den)
            AIComp = mind.GetAIComponent()
            AIComp.MyDen = den

            if self.targetPlayer:
                # Don't affect the combat music on initial target (weird if spawned miles away and can't path)
                if mind.AIClass:
                    preClassThreat = mind.AIClass.CombatMusicTargetingThreat
                    mind.AIClass.CombatMusicTargetingThreat = 0
                
                # Start attacking the player
                AIComp.AddTarget(PC.pawn)
                AIComp.NotifyAttackedBy(PC.pawn)
                
                if mind.AIClass:
                    mind.AIClass.CombatMusicTargetingThreat = preClassThreat # type: ignore
                            
                spawnedPawn.PlayTaunt()


def GetGameStage(PC:WillowPlayerController, den:PopulationOpportunityDen | None = None) -> int:
    stage = 0
    if den:
        rarity = 0
        out = den.GetOpportunityGameStage(stage, rarity)
        if out[0]:
            stage = out[1]
    if stage == 0:
        # From WillowPlayerController.FixupPlaythroughTwo
        mission = PC.MissionPlaythroughs[1].MissionList[0].MissionDef.NextMissionInChain
        if mission:
            awesomeLevel = 0
            out = mission.GameStageRegion.GetRegionGameStage(stage, awesomeLevel)
            if out[0]:
                stage = out[1]
    if stage == 0:
        if PC.pawn:
            stage = PC.pawn.GetGameStage()
        else:
            stage = 1
    return stage
