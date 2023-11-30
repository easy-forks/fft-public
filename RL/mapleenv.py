import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time
import copy
import pickle
import random
import numpy as np
from fractions import Fraction
from collections import deque
from collections import defaultdict
from typing import List, Optional, Dict
import maple.character as Character
import maple.enemy as Enemy
import maple.skill as Skill
import maple.maple as Maple
import maple.utils as Utils



log = Utils.log
debug_mode = Utils.debug_mode

class MapleEnv(Maple.Maple):
    """
    MapleEnv is a wrapper around Maple for implementing RL interface
    """
    def __init__(self, character: Character, enemy: Enemy, absorbing_state_time: int) -> None:
        super().__init__(character=character, enemy=enemy)
        self.absorbing_state_time: int = absorbing_state_time
        self.raw_data: Dict[str, any] = defaultdict(dict)
        self.init_state = self.get_state()

    def reset(self):
        self.time: Fraction = 0
        self.character.status = copy.deepcopy(self.character.status_default)
        self.character.make_skills_available()

    def get_time(self) -> Fraction:
        return self.time
    
    def step(self, action: Skill):
        next_state, reward = action.use_skill(self)
        return next_state, reward
    
    def process_event(self):
        reward = 0

        while self.lasting_events:
            closest_event_time = self.lasting_events[0][0]
            if closest_event_time > self.time:
                break
            
            event = self.lasting_events.popleft()
            is_buff = True if type(event[1]) == str else False
            if is_buff:
                _, key, val = event
                self.character.increase_stat(key, val)
                if debug_mode["all"] or debug_mode["time"]:
                    # TODO: Pass skill_name as argument in order to log
                    log(f"Some skill increased {key} by {val} at {self.time} seconds.")
            else:
                # 타격 스킬의 사용은 끝났으나, 남아서 적용되는 효과가 있는 경우
                _, damage, hit, additional_effects = event
                
                originals = []
                for key, val in additional_effects:
                    originals.append((key, self.character.get_stat(key)))
                    self.character.increase_stat(key, val)
                
                attack_reward = damage * hit * self.character.get_damage(self.enemy)
                
                for key, val in originals:
                    self.character.set_stat(key, val)

                reward += attack_reward
                if debug_mode["all"] or debug_mode["time"]:
                    # TODO: Pass skill_name as argument in order to log
                    log(f"Some skill Attacked with damage attack_reward at {self.time} seconds. (Lasting attack)")
        
        return reward

    def add_time(self, increment: Fraction):
        if increment < 0:
            raise ValueError("")
        elif increment == 0:
            return 0
        self.time += increment
        for skill in self.character.skills:
            skill.update_reuse_time(increment)
        reward = self.process_event()
        
        if debug_mode["all"] or debug_mode["time"]:
            log(f"Time increased by {increment} seconds. Current time is {self.time} seconds.", color="red")
        return reward

    def save_raw_data(self, state, action, next_state, reward):
        if action.name not in self.raw_data[state]:
            self.raw_data[state][action.name] = int(reward), next_state

    def get_state(self):
        state = (
            self.character.get_damage_without_enemy(),
            tuple([(skill.name, float(round(skill.reuse_time_left, 2))) for skill in self.character.skills]), # skills and its cooldown
            float(round(self.absorbing_state_time - self.time, 2))
        )
        return state

    def get_random_action(self, actions):
        if actions[0].skill_type == "keydown" and actions[1].skill_type == "stop":
            if random.uniform(0, 1) < 0.9:
                return actions[0]
            else:
                return actions[1]
        return random.choice(actions)
    
    def get_action(self, state, actions, epsilon = 0.1):
        # epsilon-greedy policy
        if random.uniform(0, 1) < epsilon:
            action = random.choice(actions)
            if debug_mode["all"] or debug_mode["action"]:
                log(f"Choosed an action {action.name} by epsilon-greedy policy")
        else:
            state_names = self.raw_data.get(state, {})
            action_names = [action.name for action in actions]
            available_indices = [i for i, action_name in enumerate(state_names.keys()) if action_name in action_names]
            if available_indices:
                available_actions = np.array(list(state_names.keys()))[available_indices]
                q_values = np.array(list(state_names.values()))[available_indices]
                best_indices = np.where(q_values == np.max(q_values))[0]
                best_actions = available_actions[best_indices]
                action = self.get_skill_by_name(random.choice(best_actions), actions)
            else:
                action: Skill = random.choice(actions)
                if debug_mode["all"] or debug_mode["action"]:
                    log(f"Randomly choosed an action {action.name} among actions {[action.name for action in actions]}.", color="blue")
        return action

    def save_file(self):
        saving_begin = time.time()
        pickle_file = copy.deepcopy(self.raw_data)
        for key, value in pickle_file.items():
            if isinstance(value, np.ndarray):
                pickle_file[key] = value.tolist()
        
        filenames = [(pickle_file, "raw_data"), (self.init_state, "init_state")]
        for data, filename in filenames:
            with open(f'{filename}.pickle', 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            saving_end = time.time()
            print("Table Saving:", saving_end - saving_begin, "seconds")
            print(f"Saved {filename}.pickle")
    
    def run_simulation(self, episode_num = 100):
        log("Begin Simulation")
        sim_begin = time.time()

        if debug_mode["all"] or debug_mode["episode"]:
            episode = ""

        for i in range(episode_num):
            if debug_mode["all"] or debug_mode["episode"]:
                log(f"Episode {i} started.")
            self.reset()
            
            while True:
                actions = self.character.get_available_skills()
                state = self.get_state()
                action = self.get_random_action(actions)

                if debug_mode["all"] or debug_mode["episode"]:
                    episode += f"{action.name}\n"
                if debug_mode["all"] or debug_mode["time"]:
                    log(f"using action {action.name} at {self.time} seconds.")
                
                next_state, reward = self.step(action)

                if debug_mode["all"] or debug_mode["damage"]:
                    log(f"Action {action.name} got damage {int(reward):,}")
                if self.time >= self.absorbing_state_time:
                    if debug_mode["all"] or debug_mode["time"]:
                        log(f"{self.time} seconds passed. End of episode.")
                    break
                
                self.save_raw_data(state, action, next_state, reward)
            
            if debug_mode["all"] or debug_mode["episode"]:
                log(f"End of Episode: {episode}")
        sim_end = time.time()
        log("End of Simulation")
        log("Total Simulation:", sim_end - sim_begin, "seconds")
        log("Average Episode:", (sim_end - sim_begin) / episode_num, "seconds")
        
        self.save_file()
