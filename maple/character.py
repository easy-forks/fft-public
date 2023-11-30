from typing import Dict, List, Optional
from fractions import Fraction
import copy
import math
import maple.profession as Profession
import maple.skill as Skill
import maple.job as Job

class Character:
    def __init__(self, level, status, status_fixed, profession = Profession.Profession.DUAL_BLADE, job = Job.Job.THIEF, weapon = 'dagger', skills = Optional["Skill.Skill"]):
        """
        - stats_fixed
        Hyper status, Union raiders, Arcane/Authentic Symobl, Ability
        """
        self.job = job # 'thief'
        self.profession = profession # 'dual_blade'
        self.weapon = weapon # 'dagger'
        self.weapon_constant = 1
        self.level = level
        self.status = status
        self.status_fixed = status_fixed
        self.is_dark_sight = False
        self.skills = skills
        self.skills_default = skills

    def set_skills(self, skills_new: Optional[List["Skill.Skill"]] = None):
        self.skills = skills_new

    def set_initial_skills(self):
        self.skills = self.skills_default

    def set_status_default(self):
        self.status_default = copy.deepcopy(self.status)
    
    def get_available_skills(self):
        if self.skills[0].skill_type == "keydown" and self.skills[1].skill_type == "stop":
            return self.skills
        else:
            return [skill for skill in self.skills if skill.reuse_time_left == 0]
    
    def make_skills_available(self):
        for skill in self.skills:
            skill.reuse_time_left = 0

    def init_status(self, vals):
        for i, key in enumerate(self.character.status.keys()):
            self.character.status[key] = vals[i]

    def cal_status_reflection(self) -> Fraction:
        main_sum, sub_sum = 0, 0
        main_list = [self.job.main_status] if isinstance(self.job.main_status, str) else self.job.main_status
        sub_list = [self.job.sub_status] if isinstance(self.job.sub_status, str) else self.job.sub_status
        for stat in main_list:
            if self.profession == "demon_avenger":
                stat_pure = 90 * self.level + 545
                main_sum += Fraction(stat_pure // 3.5 + 0.8 * self.status[stat]) + self.status_fixed[stat]
            else:
                stat_pure = self.level * 5 + 18
                main_sum += Fraction((stat_pure + self.status[stat]) * (1 + self.status[f"{stat}_p"])) + self.status_fixed[stat]
        for stat in sub_list:
            stat_pure = 4
            sub_sum += Fraction((stat_pure + self.status[stat]) * (1 + self.status[f"{stat}_p"])) + self.status_fixed[stat]
        if self.profession == "demon_avenger":
            return Fraction(main_sum + sub_sum, 100)
        elif self.profession == "xenon":
            return Fraction(main_sum, 100)
        else:
            return Fraction((main_sum * 4 + sub_sum), 100)
    
    def cal_attack_power(self):
        return self.status['attack_power'] * (1 + self.status['attack_power_p'])

    def cal_damage(self):
        return 1 + self.status['damage'] + self.status['boss_damage']

    def cal_final_damage_percent(self):
        return 1 + self.status['final_damage']

    def cal_weapon_constant(self):
        if self.weapon == "claw":
            self.weapon_constant = Fraction(175, 100)
        
        elif self.weapon in ["knuckle", "revoler_gauntlet", "soul_shooter"]:
            self.weapon_constant = Fraction(17, 10)
        
        elif self.weapon in ["gun", "hand_cannon", "energy_sword"]:
            self.weapon_constant = Fraction(15, 10)
        
        elif self.weapon in ["spear", "polearm", "heavy_sword"]:
            self.weapon_constant = Fraction(149, 100)
        
        elif self.weapon == "crossbow":
            self.weapon_constant = Fraction(135, 100)
        
        elif self.weapon in ["two_handed_sword", "two_handed_axe", "two_handed_blunt_weapon", "long_sword"]:
            self.weapon_constant = Fraction(134, 100)
        
        elif self.weapon in ["dagger", "blade", "dual_bowgun", "bow", "kane", "desperado", "chain"]:
            self.weapon_constant = Fraction(13, 10)
        
        elif self.weapon in ["magic_gauntlet", "one_handed_sword", "one_handed_axe", "one_handed_blunt_weapon", "shining_rod"]:
            self.weapon_constant = Fraction(12, 10)
        
        elif self.weapon in ["staff", "wand"]:
            self.weapon_constant = Fraction(10, 10)

        if self.profession == "xenon":
            self.profession_constant = Fraction(875, 1000)
        elif self.profession in ["flame_wizard", "bishop", "arch_mage_ice_lightning", "arch_mage_flame_poison"]:
            self.profession_constant = Fraction(12, 10)
        else:
            self.profession_constant = Fraction(1)
        
        return self.profession_constant * self.weapon_constant
    
    def cal_corrected_proficiency(self):
        return (1 + self.status['weapon_proficiency']) / 2
    
    def cal_corrected_defence_rate(self, enemy_defence_rate, ignore_defences: List[Fraction] = [0]):
        ignore_defence = self.status['ignore_defence']
        for i in ignore_defences:
            ignore_defence += (1 - ignore_defence) * i
        resultant_ignore_defence = 1 - enemy_defence_rate * (1 - ignore_defence)
        return resultant_ignore_defence if resultant_ignore_defence > 0 else 0
    
    def cal_average_critical_damage_percent(self):
        return 1 + (self.status['critical_damage'] + Fraction(35, 100)) * min(self.status['critical_rate'], 1)

    def cal_corrected_elemental_resistance(self, enemy_elemental_resistance = 0.5):
        """
        반감: 0.5, 없음: 0
        """
        return 1 - enemy_elemental_resistance * (1 - self.status['ignore_elemental_tolerance'])

    def get_arc_diff(self, force_req) -> float:
        arc_ratio = [1.5, 1.3, 1.1, 1.0, 0.7, 0.5, 0.3, 0.1]
        damage_ratio = [1.5, 1.3, 1.1, 1.0, 0.8, 0.7, 0.6, 0.3, 0.1]
        
        ratio = self.status['arc_force'] / force_req
        i = 0
        for arc in arc_ratio:
            if ratio >= arc:
                break
            i += 1
        return Fraction(damage_ratio[i])

    def get_aut_diff(self, force_req) -> float:
        aut_diff = [50, 40, 30, 20, 10, 0, -10, -20, -30, -40, -50, -60, -70, -80, -90]
        damage_ratio = [1.25, 1.20, 1.15, 1.10, 1.05, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.1, 0.1, 0.05]
        diff = self.status['aut_force'] - force_req
        i = 0
        for aut in aut_diff:
            if diff >= aut:
                break
            i += 1
        return damage_ratio[i]
    
    def cal_force_difference(self, field_type, force_req):
        if field_type == "arc":
            return self.get_arc_diff(force_req)
        elif field_type == "aut":
            return self.get_aut_diff(force_req)
        else:
            return 1
    
    def cal_level_difference(self, enemy_level):
        diff = min(5, self.level - enemy_level)
        if diff < -5:
            return Fraction(math.ceil(2.5 * (40 + diff)), 100)
        elif -5 < diff < 0:
            correction = [1, 0.98, 0.96, 0.95, 0.93, 0.9]
            return Fraction((110 + diff * 5) * correction[-diff], 100)
        else:
            return Fraction((110 + diff * 2), 100)

    def get_damage(self, enemy):
        level = enemy.level
        field_type = enemy.field_type
        field_force = enemy.field_force
        defence_rate = enemy.defence_rate
        elemental_resistance = enemy.elemental_resistance

        return self.cal_status_reflection() * self.cal_attack_power() * self.cal_damage() * self.cal_final_damage_percent() \
            * self.cal_weapon_constant() * self.cal_corrected_proficiency() * self.cal_corrected_defence_rate(defence_rate) \
            * self.cal_average_critical_damage_percent() * self.cal_corrected_elemental_resistance(elemental_resistance) \
            * self.cal_force_difference(field_type, field_force) * self.cal_level_difference(level)
    
    def get_stat(self, key):
        return self.status.get(key, "")
    
    def set_stat(self, key, value):
        self.status[key] = value
    
    def increase_stat(self, key, value):
        if key in ["ignore_defence", "ignore_elemental_tolerance"]:
            val_for_decrease = 1
            if value < 0:
                val_for_decrease = Fraction(1, 1 + value)
            self.status[key] += (1 - self.status[key]) * value * val_for_decrease
        else:
            self.status[key] += value
            if key in ["STR", "DEX", "INT", "LUK", "attack_power", "arc_force", "aut_force"]:
                self.status[key] //= 1

    def get_damage_without_enemy(self):
        return int(self.cal_status_reflection() * self.cal_attack_power() * self.cal_damage() * self.cal_final_damage_percent() \
            * self.cal_weapon_constant() * self.cal_corrected_proficiency() * self.cal_average_critical_damage_percent())