from fractions import Fraction
import maple.character as Character
import maple.enemy as Enemy
import maple.skill as Skill
import RL.mapleenv as MapleEnv

phatom_blow = Skill.ActiveInstantSkill(
    name="Phantom Blow",
    skill_type="instant",
    reuse_time=0,
    pre_delay=0,
    cooldown_reducible=True,
    post_delay=Fraction(57, 100),
    skill_actions=[(Fraction(392, 100), 7, 0)],
    additional_effects=[
        ("ignore_defence", Fraction(33, 100), 0),
        ("ignore_defence", Fraction(20, 100), 0),
        ("damage", Fraction(20, 100), 0),
    ],
)
restraint = Skill.ActiveBuffSkill(
    name="Restraint Ring",
    skill_type="buff",
    reuse_time=180,
    pre_delay=Fraction(0),
    cooldown_reducible=True,
    post_delay=Fraction(27, 100),
    skill_actions=[],
    additional_effects=[("attack_power_p", Fraction(50, 100), Fraction(11, 1))],
)
ready_to_die = Skill.ActiveBuffSkill(
    name="Ready to Die",
    skill_type="buff",
    reuse_time=75,
    pre_delay=Fraction(0),
    cooldown_reducible=True,
    post_delay=Fraction(600, 1000),
    skill_actions=[],
    additional_effects=[("final_damage", Fraction(36, 100), 15)],
)
blade_tornado = Skill.ActiveInstantSkill(
    name="Blade Tornado",
    skill_type="instant",
    reuse_time=12,
    pre_delay=Fraction(90, 1000),
    cooldown_reducible=True,
    post_delay=Fraction(510, 1000),
    skill_actions=[
        (Fraction(1320, 100), 7, Fraction(0, 10)),
        (Fraction(880, 100), 6, Fraction(10, 10)),
        (Fraction(880, 100), 6, Fraction(12, 10)),
        (Fraction(880, 100), 6, Fraction(14, 10)),
        (Fraction(880, 100), 6, Fraction(16, 10)),
        (Fraction(880, 100), 6, Fraction(18, 10)),
        (Fraction(880, 100), 6, Fraction(20, 10))
    ],
    additional_effects=[
        ("ignore_defence", Fraction(100, 100), 0),
    ],
)
karma_fury = Skill.ActiveInstantSkill(
    name="Karma Fury",
    skill_type="instant",
    reuse_time=10,
    pre_delay=Fraction(90, 1000),
    cooldown_reducible=True,
    post_delay=Fraction(510, 1000),
    skill_actions=[
        (Fraction(880, 100), 7, Fraction(0, 100)),
        (Fraction(880, 100), 7, Fraction(21, 100)),
        (Fraction(880, 100), 7, Fraction(42, 100)),
        (Fraction(880, 100), 7, Fraction(63, 100)),
        (Fraction(880, 100), 7, Fraction(84, 100)),
    ],
    additional_effects=[
        ("ignore_defence", Fraction(30, 100), 0),
    ],
)
skills = [
    phatom_blow,
    restraint,
    ready_to_die,
    karma_fury,
    blade_tornado,
]
character = Character.Character(
    level=277,
    status={
        "STR": 1836,
        "DEX": 2771,
        "INT": 4,
        "LUK": 5196,
        "attack_power": 5625,
        "arc_force": 1350,
        "aut_force": 280,
        "STR_p": Fraction(147, 100),
        "DEX_p": Fraction(151, 100),
        "INT_p": Fraction(0, 100),
        "LUK_p": Fraction(428, 100),
        "attack_power_p": Fraction(105, 100),
        "damage": Fraction(59, 100),
        "boss_damage": Fraction(338, 100),
        "final_damage": Fraction(2, 10),
        "weapon_proficiency": Fraction(91, 100),
        "critical_damage": Fraction(751, 1000),
        "critical_rate": Fraction(1, 1),
        "ignore_defence": Fraction(
            8806, 10000
        ),
        "ignore_elemental_tolerance": Fraction(5, 100),
        "cooldown_reduction_rate": Fraction(0, 100),
        "cooldown_reduction_time": 0,
    },
    status_fixed={"STR": 0, "DEX": 0, "INT": 0, "LUK": 13200 + 7400 + 180 + 540 + 1300},
    skills=skills,
)

character.increase_stat(
    "LUK", ((character.level * 5 + 18) * Fraction(16, 100)) // 1
)
character.increase_stat("damage", Fraction(9, 100))
character.increase_stat("damage", Fraction(7, 100))
character.set_status_default()
enemy = Enemy.Enemy()
maple = MapleEnv.MapleEnv(character=character, enemy=enemy, absorbing_state_time=20)
maple.run_simulation(episode_num=1_000)