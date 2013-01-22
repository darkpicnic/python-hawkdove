#!/usr/bin/python
from random import choice, randint
import time

STARTING_DOVES = 100
STARTING_HAWKS = 100
STARTING_POPULATION = STARTING_HAWKS + STARTING_DOVES

ROUNDS = 100
STARTING_ENERGY = 100;

MIN_FOOD_PER_ROUND = 20
MAX_FOOD_PER_ROUND = 70

ENERGY_REQUIRED_FOR_REPRODUCTION = 250
ENERGY_LOSS_PER_ROUND = 2
ENERGY_COST_OF_BLUFFING = 10
ENERGY_LOSS_FROM_FIGHTING = 200
ENERGY_REQUIRED_FOR_LIVING = 20

STATUS_ACTIVE = "active"
STATUS_ASLEEP = "asleep"

TYPE_HAWK = "hawk"
TYPE_DOVE = "dove"

agents = []

# Graph stuff
graph_hawk_points = []
graph_dove_points = []

# Profiling


class Agent:
 	id = 0
	agent_type = None
	status = STATUS_ACTIVE
	energy = STARTING_ENERGY


def main():
	init()

	current_round = 1
	death_count = 0
	dead_hawks  = 0
	dead_doves  = 0
	breed_count = 0
	main_tic = time.clock()

	while current_round <= ROUNDS and len(agents) > 2:
		tic = time.clock()
		awakenAgents()
		food = getFood()

		# This could be optimized further by creating a list every time
		# that only has active agents, so it isn't iterating over entire list every time
		while True:
			agent, nemesis = getRandomAgents()
			if agent is None or nemesis is None: break
			compete(agent, nemesis, food)

		# Energy cost of 'living'
		for agent in agents:
			agent.energy += ENERGY_LOSS_PER_ROUND

		round_dead_hawks, round_dead_doves = cull()
		round_hawk_babies, round_dove_babies = breed()
		death_count += (round_dead_hawks + round_dead_doves)
		breed_count += (round_hawk_babies + round_dove_babies)


		toc = time.clock()

		print("ROUND %d" % current_round)
		print("Food produced          : %d" % food)
		print("Population             : Hawks-> %d, Doves-> %d" % (getAgentCountByType(TYPE_HAWK), getAgentCountByType(TYPE_DOVE)))
		print("Dead hawks             : %d" % round_dead_hawks)
		print("Dead doves             : %d" % round_dead_doves)
		print("Hawk babies            : %s" % round_hawk_babies)
		print("Dove babies            : %s" % round_dove_babies)
		print("Hawks                  : %s" % getPercByType(TYPE_HAWK))
		print("Doves                  : %s" % getPercByType(TYPE_DOVE))
		print("----")
		print("Round Processing time  : %s" % getTimeFormatted(toc - tic))
		print("Elapsed time           : %s\n" % getTimeFormatted(time.clock() - main_tic))

		# Plot
		graph_hawk_points.append(getAgentCountByType(TYPE_HAWK))
		graph_dove_points.append(getAgentCountByType(TYPE_DOVE))

		current_round += 1


	main_toc = time.clock()

	print("=============================================================")
	print("Total dead agents      : %d" % death_count)
	print("Total breeding agents  : %d" % breed_count)
	print("Total rounds completed : %d" % (current_round - 1))
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


def getAvgFromList(list):
	return float( sum(list) / len(list) )


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


def getRandomAgents():
	nemesis = None
	active_agents = list(generateAgentsByStatus(STATUS_ACTIVE))
	if len(active_agents) < 2:
		return None, None
	max_index = len(active_agents) - 1
	agent = active_agents[ randint(0, max_index) ]
	while nemesis is None:
		n = active_agents[ randint(0, max_index) ]
		if n is not agent:
			nemesis = n

	return agent, nemesis


def awakenAgents():
	for agent in agents:
		agent.status = STATUS_ACTIVE


def generateAgentsByType(agent_type):
	for agent in agents:
		if agent.agent_type == agent_type:
			yield agent


def generateAgentsByStatus(status):
	for agent in agents:
		if agent.status == status:
			yield agent


def getEnergyFromFood(food):
	return food # 1 to 1


def getAgentCountByStatus(status):
	count = len( list(generateAgentsByStatus(status)) )
	return count


def getAgentCountByType(agent_type):
	return len( list(generateAgentsByType(agent_type)) )


def compete(agent, nemesis, food):
	winner = choice([agent, nemesis])
	loser = agent if (winner is nemesis) else nemesis

	if agent.agent_type == TYPE_HAWK and nemesis.agent_type == TYPE_HAWK:
		# Random winner chosen, loser gets injured, winner gets food
		winner.energy += getEnergyFromFood(food)
		loser.energy  -= ENERGY_LOSS_FROM_FIGHTING

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
		if agent.energy > ENERGY_REQUIRED_FOR_REPRODUCTION:
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

try:
	from pylab import *
except ImportError:
	exit()
else:
	plot(graph_dove_points)
	plot(graph_hawk_points)
	show()