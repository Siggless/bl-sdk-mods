from unrealsdk import find_class, find_enum, make_struct
from unrealsdk.hooks import Block, Type 
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct
from mods_base.options import BoolOption, SpinnerOption
from mods_base import build_mod, hook, get_pc
from typing import Any

classPart = find_class("WeaponPartDefinition")
classPC = find_class("WillowPlayerController")

_skillsFromWeapons = []

@hook("WillowGame.Behavior_AttributeEffect:ApplyBehaviorToContext")
def ApplyBehaviorToContext(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    bpd = obj.Outer
    part = bpd.Outer
    pawn = args.ContextObject
    if not pawn:
        return
    pc = pawn.Controller
    if part.Class is classPart:
        #print(f"{obj.AttributeEffect} is a weapon skill!")
        global _skillsFromWeapons
        if obj.AttributeEffect not in _skillsFromWeapons:
            _skillsFromWeapons.append(obj.AttributeEffect)


@hook("WillowGame.WillowPlayerController:Behavior_ActivateSkill")
def Behavior_ActivateSkill(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    if args.SkillToActivate in _skillsFromWeapons:
        #print(f"Behavior_ActivateSkill {obj}")
        if not obj.Pawn:    # I.E. in a vehicle
            return
        wep = obj.Pawn.Weapon
        #print(wep)
        mat = wep.WeaponMaterial
        matSight = wep.SightFXCrosshairMaterial
        mat.ClearParameterValues()
        oldCol = make_struct("LinearColor")
        oldCol = mat.GetVectorParameterValue("p_BColorMidtone", oldCol)[1]
        #print(oldCol)
        col = make_struct("LinearColor", R=oldCol.R*10*(1.2-oldCol.R), G=oldCol.G*10*(1-oldCol.G), B=oldCol.B*10*(1.1-oldCol.B), A=oldCol.A)
        #print(col)
        mat.SetVectorParameterValue("p_BColorMidtone", col)
        mat.SetVectorParameterValue("p_ReflectColor", col)
        mat.SetScalarParameterValue("p_ReflectColorScale", 1.3)
        
        oldDecalCol = make_struct("LinearColor")
        oldDecalCol = mat.GetVectorParameterValue("p_DecalColor", oldDecalCol)[1]
        decalCol = make_struct("LinearColor", R=oldDecalCol.R*40, G=oldDecalCol.G*40, B=oldDecalCol.B*40, A=oldCol.A)
        mat.SetVectorParameterValue("p_DecalColor", decalCol)
        mat.SetScalarParameterValue("p_EmissiveScale", 5)


# @hook("WillowGame.WillowPlayerController:Behavior_DeactivateSkill")
# @hook("WillowGame.SkillEffectManager:DeactivateSkill")
@hook("WillowGame.Skill:Deactivate", Type.POST)
def Behavior_DeactivateSkill(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if obj.SkillState != 1 and obj.Definition in _skillsFromWeapons:
        #print(f"{func} {obj}")
        pc = obj.SkillInstigator
        if pc.Class is not classPC or not pc.Pawn:
            return
        wep = pc.Pawn.Weapon
        mat = wep.WeaponMaterial
        mat.ClearParameterValues()


build_mod()
