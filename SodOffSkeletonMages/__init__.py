from unrealsdk import find_class, logging
from unrealsdk.hooks import Block, Type
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct, WeakPointer
from mods_base import build_mod, hook, BoolOption
from typing import Any
import random

optionPreventCloaking = BoolOption("Prevent Cloaking", False, description="Whether eventually, a Skelly Mage will stop cloaking altogether when moving.")

_MAX_FREQUENCY = 25
_AIPAWN_CLASS = find_class("WillowAIPawn")
_MAGE_AICLASS: WeakPointer = WeakPointer(None)

_skellyFrequencies: dict[int, tuple[bool, float, bool]] = {}
'''
Tuple [cloaked, frequency, blocked]
1 in X enemy state changes are allowed, the rest are blocked. The bigger the frequency value, the more likely we block the state change.
Since we are hooking into something that fires often, I want to only do these checks when we know Skellies are present.
So these hooks are disabled by default, and only enabled whilst this dict has items.
'''

@hook("WillowGame.WillowPawn:SetGameStage")
def SetGameStage(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    '''
    Triggers when an enemy spawns (from PopulationFactoryWillowAIPawn SetupPopulationActor)
    If it's a Skelly Mage, add to our dict, and enable hooks to start futzing with stuff
    '''
    if obj.Class is _AIPAWN_CLASS:
        global _skellyFrequencies, _MAGE_AICLASS
        if _MAGE_AICLASS() is None and obj.AIClass.Name == "CharClass_Skeleton_Mage":
            _MAGE_AICLASS = WeakPointer(obj.AIClass)
        if obj.AIClass is _MAGE_AICLASS():
            if len(_skellyFrequencies) == 0:
                logging.dev_warning("First skelly spawned!")
                CheckStateTransition.enable()
                BurrowCheckCloaked.enable()
                Died.enable()
            _skellyFrequencies[obj.InternalIndex] = (False, 0, False)


@hook("WillowGame.Action_GenericAttack:CanMove")
def CheckStateTransition(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    '''
    This is called within GetDesiredState to decide whether to HoldStill or MoveToTarget. We skip this to return false and always hold still
    '''
    pawn = obj.MyWillowPawn
    if pawn.Class is _AIPAWN_CLASS and pawn.AIClass is _MAGE_AICLASS():
        global _skellyFrequencies
        data = _skellyFrequencies[pawn.InternalIndex]
        if not data[0]:
            if data[2]:
                return Block


@hook("WillowGame.Action_Burrow:CheckCloaked")
def BurrowCheckCloaked(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    '''
    Blocking this stops the enemies cloaking, without messing with their action state (so they still move just don't turn invisible)
    '''
    pawn = obj.MyWillowPawn
    if pawn.Class is _AIPAWN_CLASS and pawn.AIClass is _MAGE_AICLASS():
        global _skellyFrequencies
        freq = _skellyFrequencies[pawn.InternalIndex][1]
        
        if args.Type == 1:  # BodyClassDefinition.ECloakType.CLOAK_AttackAnim
            if freq < _MAX_FREQUENCY:
                # Simple function for scaling chances back
                freq = min(_MAX_FREQUENCY,(freq + 0.18) * 1.5)
            _skellyFrequencies[pawn.InternalIndex] = (True, freq, False)
            
            if freq >= _MAX_FREQUENCY and optionPreventCloaking.value:
                # If we are at the max frequency, then also stop cloaking altogether
                return Block
            
        else:
            blockMoves: bool = random.uniform(0, freq) >= 1
            _skellyFrequencies[pawn.InternalIndex] = (False, freq, blockMoves)


@hook("Engine.Pawn:Destroyed")  # For despawning without dying - including level change
@hook("WillowGame.WillowAIPawn:Died")
def Died(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    '''
    Triggers when an enemy dies
    If a Skelly Mage dies, remove from our dict, and disable hooks if there are no more alive
    '''
    global _skellyFrequencies
    skellyCount = len(_skellyFrequencies)
    if skellyCount > 0:
        if obj.Class is _AIPAWN_CLASS and obj.AIClass is _MAGE_AICLASS():
            if obj.InternalIndex in _skellyFrequencies:
                _skellyFrequencies.pop(obj.InternalIndex)
                skellyCount = skellyCount - 1
                if skellyCount == 0:
                    logging.dev_warning("Last skelly died!")
                    CheckStateTransition.disable()
                    BurrowCheckCloaked.disable()
                    #Died.disable() # Can't disable own function? Whatever just leave this on


build_mod(hooks=[SetGameStage])
