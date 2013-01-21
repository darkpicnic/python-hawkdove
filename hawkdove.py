#!/usr/bin/python

from random import choice, randint
import time

STARTING_DOVES = 10000
STARTING_HAWKS = 20
STARTING_POPULATION = STARTING_HAWKS + STARTING_DOVES

ROUNDS = 1000
STARTING_ENERGY = 40;

REPRODUCTION_THRESHOLD = 70

FOOD_PER_ROUND = 10
ENERGY_COST_OF_BLUFFING = 10
INJURY_FROM_FIGHTING = 10
DEATH_FROM_INJURY = 50
ENERGY_REQUIRED_FOR_LIVING = 15

STATUS_ACTIVE = "active"
STATUS_ASLEEP = "asleep"
STATUS_DEAD   = "dead"

TYPE_HAWK = "hawk"
TYPE_DOVE = "dove"

agents = []


class Agent:
 	id = 0
	agent_type = None
	status = STATUS_ACTIVE
	energy = STARTING_ENERGY
	injury = 0


def main():
	init()

	current_round = 0
	death_count = 0
	breed_count = 0
	tic = time.clock()

	while current_round < ROUNDS and len(agents) > 2:
		awakenAgents()
		while getAgentCountByStatus(STATUS_ACTIVE) > 2:
			agent = getRandomAgent()
			nemesis = getRandomAgent(agent)
			compete(agent, nemesis)

		round_death_count = cull()
		round_breed_count = breed()
		death_count += round_death_count
		breed_count += round_breed_count

		print("ROUND %d" % current_round)
		print("Population: Hawks-> %d, Doves-> %d" % (getAgentCountByType(TYPE_HAWK), getAgentCountByType(TYPE_DOVE)))
		print("Dead this round: %d" % round_death_count)
		print("Bred this round: %d" % round_breed_count)

		current_round += 1


	toc = time.clock()
	print("=============================================================")
	print("Total dead agents      : %d" % death_count)
	print("Total breeding agents  : %d" % breed_count)
	print("Total rounds completed : %d" % current_round)
	print("Total population size  : %s" % len(agents))
	print("Processing time        : %s" % (toc - tic))



def init():

	for x in xrange(0,STARTING_DOVES):
		a = Agent()
		a.agent_type = TYPE_DOVE
		agents.append(a)

	for x2 in xrange(0,STARTING_HAWKS):
		a2 = Agent()
		a2.agent_type = TYPE_HAWK
		agents.append(a2)


def getAliveAgentsCount():
	return getAgentCountByStatus(STATUS_ACTIVE) + getAgentCountByStatus(STATUS_ASLEEP)

def getRandomAgent(excluded_agent=None):
	active_agents = [agent for agent in agents if agent.status == STATUS_ACTIVE]
	if excluded_agent is not None:
		active_agents = [agent for agent in agents if agent is not excluded_agent]

	return choice(active_agents)


def awakenAgents():
	for agent in agents:
		agent.status = STATUS_ACTIVE


def getEnergyFromFood(food):
	return food / 2


def getAgentCountByType(agent_type):
	return len([agent for agent in agents if agent.agent_type == agent_type])

def getNemesis(agent):
	nemesis = None
	while nemesis is None:
		random_agent = agents[randint(0, len(agents))]
		if random_agent is not agent and random_agent.status is STATUS_ACTIVE:
			nemesis = random_agent

	return nemesis


def getAgentCountByStatus(status):
	count = 0
	for agent in agents:
		if agent.status == status:
			count += 1

	return count


def compete(agent, nemesis):
	agent_list = [agent, nemesis]
	winner = choice(agent_list)
	loser = agent if (winner is nemesis) else nemesis

	if agent.agent_type == TYPE_HAWK and nemesis.agent_type == TYPE_HAWK:
		# Random winner chosen, loser gets injured, winner gets food
		winner.energy += getEnergyFromFood(FOOD_PER_ROUND)
		loser.injury  += INJURY_FROM_FIGHTING

	if agent.agent_type == TYPE_HAWK and nemesis.agent_type == TYPE_DOVE:
		agent.energy += getEnergyFromFood(FOOD_PER_ROUND)
		nemesis.energy -= ENERGY_COST_OF_BLUFFING

	if agent.agent_type == TYPE_DOVE and nemesis.agent_type == TYPE_HAWK:
		nemesis.energy += getEnergyFromFood(FOOD_PER_ROUND)
		agent.energy -= ENERGY_COST_OF_BLUFFING

	if agent.agent_type == TYPE_DOVE and nemesis.agent_type == TYPE_DOVE:
		winner.energy += getEnergyFromFood(FOOD_PER_ROUND)
		loser.energy  -= ENERGY_COST_OF_BLUFFING

	nemesis.status = agent.status = STATUS_ASLEEP


def getNewAgent(agent_type, starting_energy=STARTING_ENERGY, status=STATUS_ASLEEP):
	agent = Agent()
	agent.agent_type = agent_type
	agent.status = status
	agent.energy = starting_energy
	return agent


def breed():
	breed_count = 0
	for agent in agents:
		if agent.energy > REPRODUCTION_THRESHOLD:
			baby_agent_a = getNewAgent(agent.agent_type, (agent.energy/2))
			baby_agent_b = getNewAgent(agent.agent_type, (agent.energy/2))
			agents.append(baby_agent_b)
			agents.append(baby_agent_a)
			agent.energy /= 2
			breed_count += 1

	return breed_count

def cull():
	death_count = 0
	for index, agent in enumerate(agents):
		if agent.injury >= DEATH_FROM_INJURY or agent.energy < ENERGY_REQUIRED_FOR_LIVING:
			death_count += 1
			del agents[index]

	return death_count


main()
