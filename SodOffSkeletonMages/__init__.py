import unrealsdk
import random
from Mods import ModMenu
from Mods.ModMenu import EnabledSaveType, Game, ModTypes, Hook, SDKMod
   
_MAX_FREQUENCY = 30
_MAGE_CLASSNAME:str = "CharClass_Skeleton_Mage"

class SodOffSkeletonMages(SDKMod):
    Name: str = "Sod Off, Skeleton Mages!"
    Author: str = "Siggles"
    Description: str = "Skeleton Mages have less chance to cloak each time they appear. Eventually stops them disappearing."
    Version: str = "1.0.0"
    SupportedGames: Game = Game.BL2 | Game.AoDK
    Types: ModTypes = ModTypes.Gameplay
    SaveEnabledState: EnabledSaveType = EnabledSaveType.LoadOnMainMenu
    
    allowFrequency = 0
    '''1 in X enemy state changes are allowed, the rest are blocked. The bigger this value, the more likely we block the state change'''
    skellyCount: int = 0
    '''Since we are hooking into something that fires often, I want to only do these checks when we know Skellies are present'''


    @Hook("WillowGame.Action_GenericAttack.CanMove")
    def CanMove(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        '''
        This is called within GetDesiredState to decide whether to HoldStill or MoveToTarget. We skip this to return false and always hold still
        I'd like to add an additional condition in here for currently being in the 'Attack' state but IDK how to call IsInState() properly
        '''
        if self.skellyCount>0 and self.allowFrequency>1:
            if caller.MyWillowPawn.AIClass is not None:
                if str(caller.MyWillowPawn.AIClass.Name) == _MAGE_CLASSNAME:
                    randy = random.uniform(0, self.allowFrequency)
                    if randy>1:
                        return False
        return True
  

    @Hook("WillowGame.Action_Burrow.CheckCloaked")
    def BurrowCheckCloaked(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        '''
        Blocking this stops the enemies cloaking, without messing with their action state (so they still move just don't turn invisible)
        '''
        if caller.MyWillowPawn.AIClass is not None:
            if str(caller.MyWillowPawn.AIClass.Name) == _MAGE_CLASSNAME:
                if params.Type==1:  # BodyClassDefinition.ECloakType.CLOAK_AttackAnim
                    if self.allowFrequency < _MAX_FREQUENCY:
                        # Simple function for scaling chances back
                        self.allowFrequency = min(_MAX_FREQUENCY,(self.allowFrequency+0.18)*1.5)
                    else:
                        # If we are at the max frequency, then also stop cloaking altogether
                        return False
        return True


    @Hook("WillowGame.WillowPawn.SetGameStage")
    def SetGameStage(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        '''
        Triggers when an enemy spawns (from PopulationFactoryWillowAIPawn SetupPopulationActor)
        If it's a Skelly Mage, increment our counter so we know when to futz with stuff
        '''
        if caller.AIClass is not None:
            if str(caller.AIClass.Name) == _MAGE_CLASSNAME:
                self.skellyCount = self.skellyCount+1
        return True
    

    @Hook("Engine.Pawn.Destroyed")  # For despawning without dying
    @Hook("WillowGame.WillowAIPawn.Died")
    def Died(self, caller: unrealsdk.UObject, function: unrealsdk.UFunction, params: unrealsdk.FStruct) -> bool:
        '''
        Triggers when an enemy dies
        If a Skelly Mage dies, reset our state change blocker value
        '''
        if self.skellyCount>0:
            if caller.AIClass is not None:
                if str(caller.AIClass.Name) == _MAGE_CLASSNAME:
                    self.allowFrequency = 0
                    self.skellyCount = max(0, self.skellyCount-1)
        return True

### End class SodOffSkeletonMages

instance = SodOffSkeletonMages()
ModMenu.RegisterMod(instance)
