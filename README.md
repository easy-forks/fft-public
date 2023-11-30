# Reinforcement Learning for [Maplestory](https://maplestory.nexon.com)

This repository aims proof of concept for reinforcement learning in Maplestory, which includes Maplestory game development and RL algorithm development.
It might be hard to understand if you are not familiar with Maplestory.

## Why Maplestory?

RPG games ought to be a suitable environment for RL because they have a lot of states and actions, so finding the optimal policy is challenging.
However, it is hard to find a suitable environment for RL because it is hard to implement the environment itself.
For this reason, Maplestory is the familiar one.

## Problem Description

For a given set of skills, what is the sequence that maximizes overall damage within the time limit?

# Environment

## Reward

Reward $R(s,a)$ is the damage dealt to the enemy from state $s$ by action $a$. Action is the skill used in the current state $s$.

## Action 

Action $a$ is the skill that is used in the current state $s$.

## State 

State $s$ includes all damage-related information, such as stat(STR, DEX, INT, LUK) and defense rate ignorance. State also has skills with its cooldown time and remaining simulation time.

It is natural that state also includes information on the enemy, but we are dealing with a single, non-interactive enemy. Since the goal of the current stage is proof of concept, we are not getting deeper right now.


## Transition $T(s,a,s')$

In the current stage, the transition is deterministic. If you use skill $a$ in state $s$, you will get to state $s'$. However, introducing the "reuse cooldown time initialization" concept can make the transition stochastic. However, as mentioned earlier, it is an optional feature for the current stage.

# Algorithm

## Q-Learning

Q-learning is a model-free reinforcement learning algorithm that learns the optimal policy by updating the Q-value table.

## Value Iteration

By simplifying the Bellman equation considering the deterministic transition, we can get the value iteration equation as follows.

$$
Q(s,a) = R(s,a) + \gamma V(s')
$$

# Application

## Equivalent 


# Future Work

## Environment Advancement

### Interactive Enemy

### Client Based Simulation

## Performance Improvement

### Parallelization
