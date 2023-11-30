from typing import Dict, List, Optional
from collections import defaultdict
import bisect
import maple.character as Character
import RL.mapleenv as MapleEnv

class Skill:
    def __init__(self, name, skill_type, reuse_time, skill_actions, additional_effects, pre_delay, post_delay, cooldown_reducible=True):
        self.name = name
        self.skill_type = skill_type
        self.reuse_time = reuse_time
        self.reuse_time_left = 0
        self.pre_delay = pre_delay
        self.post_delay = post_delay
        self.skill_actions = skill_actions
        self.additional_effects = additional_effects
        self.cooldown_reducible = cooldown_reducible

    def start_reuse_time(self, character: Optional["Character.Character"]):
        if self.reuse_time == 0:
            return
        if not self.cooldown_reducible:
            self.reuse_time_left = self.reuse_time
        else:
            rate_decreased = self.reuse_time * (1 - character.get_stat("cooldown_reduction_rate"))
            rate_decreased = max(1, rate_decreased)
            constant_reduction = character.get_stat("cooldown_reduction_time")
            # TODO: efficient way to check rate_decreased - constant_reduction >= 10
            # Both variables are type float? constant_reduction is type int with non-negative value

            if rate_decreased - constant_reduction < 10:
                constant_reduction -= rate_decreased - 10
                constant_reduction *= 0.5
                rate_decreased = 10
            self.reuse_time_left = rate_decreased - constant_reduction
            self.reuse_time_left = max(1, self.reuse_time_left)

    def update_reuse_time(self, time):
        if self.reuse_time_left > 0:
            self.reuse_time_left -= time
        if self.reuse_time_left < 0:
            self.reuse_time_left = 0

    def use_skill(self, env: Optional["MapleEnv.MapleEnv"]):
        reward = env.add_time(self.pre_delay)

        instant_buffs = []
        originals = defaultdict()
        if self.additional_effects:
            for key, val, duration in self.additional_effects:
                if duration > 0:
                    env.character.increase_stat(key, val)
                    bisect.insort(env.lasting_events, (env.time + duration, key, -val))
                else:
                    if key not in originals:
                        originals[key] = env.character.get_stat(key)
                    instant_buffs.append((key, val))
                    env.character.increase_stat(key, val)
        
        for damage, hit, timing in self.skill_actions:
            if timing > 0:
                if env.time + timing < env.absorbing_state_time:
                    reward += damage * hit * env.character.get_damage(env.enemy)
                else:
                    break
            else:
                reward += damage * hit * env.character.get_damage(env.enemy)

        for key in originals:
            env.character.set_stat(key, originals[key])

        reward += env.add_time(self.post_delay)

        self.start_reuse_time(env.character)
        next_state = env.get_state()
        
        return next_state, reward


class ActiveInstantSkill(Skill):
    def __init__(self, name, skill_type, reuse_time, skill_actions, additional_effects, pre_delay, post_delay, cooldown_reducible):
        super().__init__(name, skill_type, reuse_time, skill_actions, additional_effects, pre_delay, post_delay, cooldown_reducible)


class ActiveKeydownSkill(Skill):
    def __init__(self, name, skill_type, reuse_time, skill_actions, additional_effects, pre_delay, post_delay, cooldown_reducible, keydown_limit, keydown_tick):
        super().__init__(name, skill_type, reuse_time, skill_actions, additional_effects, pre_delay, post_delay, cooldown_reducible)
        self.keydown_limit = keydown_limit
        self.keydown_tick = keydown_tick
        self.previous_skills = []
        self.keydown_pair = keydown_pair
        self.latest_timing = 0

    def use_skill(self, env: Optional["MapleEnv.MapleEnv"]):
        if self.skill_type == "stop" or self.keydown_tick >= self.keydown_limit:
            env.character.skills[0].keydown_tick = 0
            reward = env.add_time(env.character.skills[0].post_delay)
            env.character.set_initial_skills()
            next_state = env.get_state()
            return next_state, reward
        elif self.skill_type == "keydown" and self.keydown_tick == 0:
            env.character.set_skills([self, self.keydown_pair])
            self.latest_timing = 0
        
        instant_buffs = []
        if self.additional_effects:
            for key, val, duration in self.additional_effects:
                if duration > 0:
                    env.character.increase_stat(key, val)
                    bisect.insort(env.lasting_events, (env.time + duration, key, -val, self.name, self.skill_type))
                else:
                    env.character.increase_stat(key, val)
                    instant_buffs.append((key, -val))
        
        damage, hit, timing = self.skill_actions[self.keydown_tick]
        reward = damage * hit * env.character.get_damage(env.enemy)
        self.start_reuse_time(env.character)
        reward += env.add_time(timing - self.latest_timing)
        self.keydown_tick += 1
        self.latest_timing = timing
        
        for key, val in instant_buffs:
            env.character.increase_stat(key, -val)

        next_state = env.get_state()
        
        return next_state, reward
        

class ActiveBuffSkill(Skill):
    def __init__(self, name, skill_type, reuse_time, skill_actions, additional_effects, pre_delay, post_delay, cooldown_reducible):
        super().__init__(name, skill_type, reuse_time, skill_actions, additional_effects, pre_delay, post_delay, cooldown_reducible)

    def use_skill(self, env: Optional["MapleEnv.MapleEnv"]):
        reward = env.add_time(self.pre_delay)

        for key, val, duration in self.additional_effects:
            env.character.increase_stat(key, val)
            bisect.insort(env.lasting_events, (env.time + duration, key, -val))

        self.start_reuse_time(env.character)
        
        reward += env.add_time(self.post_delay)
        next_state = env.get_state()
        
        return next_state, reward

