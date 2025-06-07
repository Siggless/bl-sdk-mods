from unrealsdk import find_class, find_enum, make_struct
from unrealsdk.hooks import Block, Type 
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
from mods_base.options import BoolOption, SpinnerOption
from mods_base import build_mod, hook, get_pc
from typing import Any

_classStatusDef = find_class("StatusEffectDefinition")
STATUS_TYPE = find_enum("EStatusEffectType")
_BehaviorParameters = make_struct("BehaviorParameters")

options = {
    "Never" : 0,
    "No Shield" : 1,
    "Always" : 2,
}
keys = list(options.keys())
_optionsByClass = {
    find_class("WillowPlayerPawn") : SpinnerOption("Player Screams", keys[1], keys, description="When player DOT screams will play from status effects."),
    find_class("WillowAIPawn") : SpinnerOption("Enemy Screams", keys[2], keys, description="When NPC DOT screams will play from status effects."),
}


@hook("GearboxFramework.Behavior_TriggerDialogEvent:TriggerDialogEvent")
def TriggerDialogEvent(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    """
    Fires when a TriggerDialogEvent is applied
    In particular, we want to check StatusEffectDefinition's OnApplication Behavior_TriggerDialogEvent
    """
    if obj.Outer and obj.Outer.Class is _classStatusDef:
        # Don't prevent slag (Status_Amp) and healing effects
        statusType = obj.Outer.StatusEffectType
        if statusType != STATUS_TYPE.STATUS_EFFECT_Amp and statusType != STATUS_TYPE.STATUS_EFFECT_Healing:
            pawn = args.ContextObject
            if pawn.Class in _optionsByClass:
                val = options[_optionsByClass[pawn.Class].value]
                if val == 0:
                    return Block
                elif val == 1:
                    # Block the VO if the shield is not empty
                    if pawn.ShieldArmor and pawn.ShieldArmor.Data and pawn.ShieldArmor.Data.GetCurrentValue() > 0:
                        return Block


@hook("WillowGame.StatusEffectsComponent:StartEffectSound")
def StartEffectSound(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    """
    Triggers repeatedly whilst a status effect is active on a Pawn
    We use this to start the status effect VO when the player's shield breaks, if one is still active
    """
    pawn = obj.Owner
    if pawn.Class in _optionsByClass and options[_optionsByClass[pawn.Class].value] == 1:
        # Check if the shield is depleted - OnShieldDeplete doesn't fire for some reason?
        if pawn.ShieldArmor and pawn.ShieldArmor.Data and pawn.ShieldArmor.Data.GetCurrentValue() <= 0:
            statusDef = obj.GetMostRecentStatusEffect()
            if statusDef and statusDef.StatusEffectType != STATUS_TYPE.STATUS_EFFECT_Amp and statusDef.StatusEffectType != STATUS_TYPE.STATUS_EFFECT_Healing:
                # Play the status effect VO
                dialogBehavior = statusDef.OnApplication[1]  # Assuming that the Behavior_TriggerDialogEvent is always this index
                if dialogBehavior and dialogBehavior.Class.Name == "Behavior_TriggerDialogEvent":
                    dialogBehavior.TriggerDialogEvent(pawn, pawn, None, None, _BehaviorParameters)


build_mod(options=list(_optionsByClass.values()))
