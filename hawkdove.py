#!/usr/bin/python
from random import choice, randint
import time

STARTING_DOVES = 50
STARTING_HAWKS = 1
STARTING_POPULATION = STARTING_HAWKS + STARTING_DOVES

ROUNDS = 100
STARTING_ENERGY = 100;

REPRODUCTION_THRESHOLD = 200
ENERGY_PER_ROUND = 2

MIN_FOOD_PER_ROUND = 20
MAX_FOOD_PER_ROUND = 100
ENERGY_COST_OF_BLUFFING = 10
INJURY_FROM_FIGHTING = 120
ENERGY_REQUIRED_FOR_LIVING = 20

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


def main():
	init()

	current_round = 0
	death_count = 0
	dead_hawks  = 0
	dead_doves  = 0
	breed_count = 0
	main_tic = time.clock()

	while current_round < ROUNDS and len(agents) > 2:
		tic = time.clock()
		awakenAgents()
		food = getFood()

		while getAgentCountByStatus(STATUS_ACTIVE) > 2:
			agent = getRandomAgent()
			nemesis = getRandomAgent(agent)
			compete(agent, nemesis, food)

		# Energy cost of 'living'
		for agent in agents:
			agent.energy += ENERGY_PER_ROUND

		round_dead_hawks, round_dead_doves = cull()
		round_hawk_babies, round_dove_babies = breed()
		death_count += (round_dead_hawks + round_dead_doves)
		breed_count += (round_hawk_babies + round_dove_babies)


		toc = time.clock()

		print("ROUND %d" % current_round)
		print("Food produced: %d" % food)
		print("Population: Hawks-> %d, Doves-> %d" % (getAgentCountByType(TYPE_HAWK), getAgentCountByType(TYPE_DOVE)))
		print("Hawk babies: %s" % round_hawk_babies)
		print("Dove babies: %s" % round_dove_babies)
		print("Hawks: %s" % getPercByType(TYPE_HAWK))
		print("Doves: %s" % getPercByType(TYPE_DOVE))
		print("Processing time        : %s\n" % getTimeFormatted(toc - tic))

		current_round += 1


	main_toc = time.clock()

	print("=============================================================")
	print("Total dead agents      : %d" % death_count)
	print("Total breeding agents  : %d" % breed_count)
	print("Total rounds completed : %d" % current_round)
	print("Total population size  : %s" % len(agents))
	print("Hawks                  : %s" % getPercByType(TYPE_HAWK))
	print("Doves                  : %s" % getPercByType(TYPE_DOVE))
	print("Processing time        : %s" % getTimeFormatted(main_toc - main_tic))
	print("=============================================================")



def init():

	for x in xrange(0,STARTING_DOVES):
		a = Agent()
		a.agent_type = TYPE_DOVE
		agents.append(a)

	for x2 in xrange(0,STARTING_HAWKS):
		a2 = Agent()
		a2.agent_type = TYPE_HAWK
		agents.append(a2)


def getTimeFormatted(seconds):
	m, s = divmod(seconds, 60)
	return "%02d:%02d" % (m, s)	


def getFood():
	return randint(MIN_FOOD_PER_ROUND, MAX_FOOD_PER_ROUND)


def getPercByType(agent_type):
	perc = float(getAgentCountByType(agent_type)) / float(len(agents))
	return '{percent:.2%}'.format(percent=perc)


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


def getAgentCountByStatus(status):
	return len( [a for a in agents if a.status == status] )


def getAgentCountByType(agent_type):
	return len([agent for agent in agents if agent.agent_type == agent_type])


def getNemesis(agent):
	nemesis = None
	while nemesis is None:
		random_agent = agents[randint(0, len(agents))]
		if random_agent is not agent and random_agent.status == STATUS_ACTIVE:
			nemesis = random_agent

	return nemesis


def compete(agent, nemesis, food):
	winner = choice([agent, nemesis])
	loser = agent if (winner is nemesis) else nemesis

	if agent.agent_type == TYPE_HAWK and nemesis.agent_type == TYPE_HAWK:
		# Random winner chosen, loser gets injured, winner gets food
		winner.energy += getEnergyFromFood(food)
		loser.energy  -= INJURY_FROM_FIGHTING

	if agent.agent_type == TYPE_HAWK and nemesis.agent_type == TYPE_DOVE:
		agent.energy += getEnergyFromFood(food)
		nemesis.energy -= ENERGY_COST_OF_BLUFFING

	if agent.agent_type == TYPE_DOVE and nemesis.agent_type == TYPE_HAWK:
		nemesis.energy += getEnergyFromFood(food)
		agent.energy -= ENERGY_COST_OF_BLUFFING

	if agent.agent_type == TYPE_DOVE and nemesis.agent_type == TYPE_DOVE:
		winner.energy += getEnergyFromFood(food)
		loser.energy  -= ENERGY_COST_OF_BLUFFING

	nemesis.status = agent.status = STATUS_ASLEEP


def getNewAgent(agent_type, starting_energy=STARTING_ENERGY, status=STATUS_ASLEEP):
	agent = Agent()
	agent.agent_type = agent_type
	agent.status = status
	agent.energy = starting_energy
	return agent


def breed():
	"""
	If agent can breed, it halves its energy and produces 
	two babies with starting energy (parent energy / 2)
	"""
	hawk_babies = 0
	dove_babies = 0
	for agent in agents:
		if agent.energy > REPRODUCTION_THRESHOLD:
			baby_agent_a = getNewAgent(agent.agent_type, (agent.energy/2))
			baby_agent_b = getNewAgent(agent.agent_type, (agent.energy/2))
			agents.append(baby_agent_b)
			agents.append(baby_agent_a)
			agent.energy /= 2
			if agent.agent_type == TYPE_DOVE: dove_babies += 2
			if agent.agent_type == TYPE_HAWK: hawk_babies += 2

	return hawk_babies, dove_babies


def cull():
	dead_hawks = 0
	dead_doves = 0
	for index, agent in enumerate(agents):
		if agent.energy < ENERGY_REQUIRED_FOR_LIVING:
			if agent.agent_type == TYPE_DOVE: dead_doves += 1
			if agent.agent_type == TYPE_HAWK: dead_hawks += 1
			del agents[index]

	return dead_hawks, dead_doves


main()
