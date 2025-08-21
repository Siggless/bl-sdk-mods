from unrealsdk import find_class, find_enum, find_object, make_struct
from unrealsdk.hooks import Block, Type 
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct, WeakPointer
from mods_base import build_mod, hook, get_pc, Game
from typing import Any

classPart = find_class("WeaponPartDefinition")
classPawn = find_class("WillowPlayerPawn")
classPC = find_class("WillowPlayerController")

_weaponSkills: dict = {}
_skillDefNames = {
    Game.BL2:[
        "GD_Weap_SniperRifles.Skills.Skill_Morningstar:BehaviorProviderDefinition_0.Behavior_AttributeEffect_0.SkillDefinition_0"
    ],
    Game.TPS:[]
}[Game.get_current()]
# for s in _skillDefNames:
#     _skillsFromWeapons.append(find_object("SkillDefinition", s))
#     #print(f"{s} is a pre-defined weapon skill!")
_skillsFromWeapons = [find_object("SkillDefinition", s) for s in _skillDefNames]
    

class WeaponSkillData:
    """Tracks each skill triggered from a weapon (including stacks), by skill definition, and alters the material if there are any active"""
    def __init__(self, weapon) -> None:
        self.weapon:WeakPointer = WeakPointer(weapon)
        self.stacksPerSkill:dict[UObject, int] = {}    # SkillDef, StackCount
        
        self.OGCol = make_struct("LinearColor")
        self.OGCol = weapon.WeaponMaterial.GetVectorParameterValue("p_BColorMidtone", self.OGCol)[1]
        self.OGDecalCol = make_struct("LinearColor")
        self.OGDecalCol = weapon.WeaponMaterial.GetVectorParameterValue("p_DecalColor", self.OGDecalCol)[1]
        
        oldCol = self.OGCol
        oldDecalCol = self.OGDecalCol
        baseCol = make_struct("LinearColor", R=oldCol.R*10*(1.2-oldCol.R), G=oldCol.G*10*(1-oldCol.G), B=oldCol.B*10*(1.1-oldCol.B), A=oldCol.A)
        refCol = make_struct("LinearColor", R=max(baseCol.R,1), G=max(baseCol.G,1), B=max(baseCol.B,1), A=baseCol.A)
        decalCol = make_struct("LinearColor", R=oldDecalCol.R*40, G=oldDecalCol.G*40, B=oldDecalCol.B*40, A=oldDecalCol.A)
        self.baseCol = baseCol
        self.refCol = refCol
        self.decalCol = decalCol
    
    def AddSkill(self, skill):
        if skill in self.stacksPerSkill:
            # We're just adding a stack
            self.stacksPerSkill[skill] = self.stacksPerSkill[skill] + 1
        else:
            # We're activating the skill (first stack if stacking)
            self.stacksPerSkill[skill] = 1
            self.ApplyEffect()
            
    def RemoveSkill(self, skill):
        if skill in self.stacksPerSkill:
            stacks = self.stacksPerSkill[skill]
            stacks = stacks - 1
            self.stacksPerSkill[skill] = stacks
            if stacks <= 0:
                self.stacksPerSkill.pop(skill)
                self.RemoveEffect()
                if not self.stacksPerSkill:
                    _weaponSkills.pop(self.weapon())
                    
    def ApplyEffect(self):
        if not (wep:=self.weapon()):
            return
        mat = wep.WeaponMaterial
        matSight = wep.SightFXCrosshairMaterial
        #print(self.baseCol)
        mat.SetVectorParameterValue("p_BColorMidtone", self.baseCol)
        mat.SetVectorParameterValue("p_ReflectColor", self.refCol)
        mat.SetScalarParameterValue("p_ReflectColorScale", 1.3)
        
        mat.SetVectorParameterValue("p_DecalColor", self.decalCol)
        mat.SetScalarParameterValue("p_EmissiveScale", 5)
    
    def RemoveEffect(self):
        if not (wep:=self.weapon()):
            return
        mat = wep.WeaponMaterial
        mat.ClearParameterValues()
        

@hook("WillowGame.Behavior_AttributeEffect:ApplyBehaviorToContext")
def ApplyBehaviorToContext(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    bpd = obj.Outer
    outer = bpd.Outer
    if not args.ContextObject:
        return
    if outer.Class is classPart:
        global _skillsFromWeapons
        skillDef = obj.AttributeEffect
        #print(f"{skillDef} is a weapon skill!")
        if skillDef not in _skillsFromWeapons:
            _skillsFromWeapons.append(skillDef)


# @hook("WillowGame.Skill:Activate")
@hook("WillowGame.WillowPlayerController:Behavior_ActivateSkill")
def Behavior_ActivateSkill(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    if args.SkillToActivate in _skillsFromWeapons:
        #print(f"Behavior_ActivateSkill {obj}")
        if not obj.Pawn:    # I.E. in a vehicle
            return
        if not (wep := obj.Pawn.Weapon):
            return
        if wep not in _weaponSkills:
            _weaponSkills[wep] = WeaponSkillData(wep)
        wepSkills = _weaponSkills[wep]
        wepSkills.AddSkill(args.SkillToActivate)


# @hook("WillowGame.WillowPlayerController:Behavior_DeactivateSkill")
# @hook("WillowGame.SkillEffectManager:DeactivateSkill")
@hook("WillowGame.Skill:Deactivate", Type.POST)
def Behavior_DeactivateSkill(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if obj.SkillState != 1 and obj.Definition in _skillsFromWeapons:
        #print(f"{func}")
        skill = obj.Definition
        for data in [*_weaponSkills.values()]:
            if skill in data.stacksPerSkill:
                data.RemoveSkill(skill)


build_mod()
