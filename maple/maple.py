import maple.character as Character
import maple.enemy as Enemy
import maple.skill as Skill
from fractions import Fraction
from collections import deque
from typing import List, Optional

class Maple:
    def __init__(self, character: Character, enemy: Enemy.Enemy):
        self.character: Character.Character = character
        self.enemy: Enemy.Enemy = enemy
        self.instant_events: List[tuple[str, Fraction, Fraction, str]] = []
        self.lasting_events: deque[tuple[int, str, Fraction, str]] = deque([])
        self.time = Fraction(0)
        
        # TODO: key: [state][skill_name], value: total damage
        self.skill_cache = {}

    def get_skill_damage(self, skill: Skill, action_idx: int):
        skill_damage_p, hits, timing = skill.skill_actions[action_idx]
        return self.character.get_damage(self.enemy) * skill_damage_p * hits, timing
    
    def add_event(self, *args):
        self.instant_events.append(self.time, args)

    def get_skill_by_name(self, name, skill_list):
        for skill in skill_list:
            if skill.name == name:
                return skill
        return None
