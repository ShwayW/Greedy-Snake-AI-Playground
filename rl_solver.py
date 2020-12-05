# Author: Shway Wang
# Date: 2020/12/3
import numpy as np
from rl_agents import *
# Actions of snake:
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
class StateActionValueTable(object):
	def __init__(self, path):
		self.path = path
		self.content = dict()
		#self.load_data()

	def addNewStateActionSet(self, cur_state, action_values):
		# action_values is a dictionary of key:action val:values
		self.content[cur_state] = action_values

	def getStateActionValue(self, state, action):
		return self.content[state][action]

	def setStateActionValue(self, state, action, value):
		self.content[state][action] = value

	def serialize(self, sence_dist, sence_matrix):
		serial = ''
		serial += str(sence_dist) + ';'
		for i in sence_matrix:
			serial += i
		return serial

	def deserialize(self, pair):
		# the pair is the key, and is of the form:
		# sence_dist(scalar);sence_vec(matrix)
		sence_dist, sence_vec = pair.split(';')
		sence_dist = int(sence_dist)
		for i in range(0, len(sence_vec), sence_dist):
			for j in range(i, i + sence_dist):
				pass
		return 

	def load_data(self):
		with open(self.path, 'r') as f:
			content = dict()
			f_content = f.readline()
			while f_content:
				elements = f_content.split()
				sence_dist, sence_matrix = self.deserialize(elements.pop(0))
				value = {}
				for i in elements:
					subkey_subvalue = i.split(':')
					realSubkey = int(subkey_subvalue[0])
					value[realSubkey] = float(subkey_subvalue[1])
				content[(sence_dist, sence_matrix)] = value
				f_content = f.readline()
		self.content = content

	def safe_data(self):
		with open(self.path, 'w') as f:
			for i in self.content:
				line = ''
				line += self.serialize(i[0], i[1]) + ' '
				for j in self.content[i]:
					line += str(j) + ':' + str(self.content[i][j]) + ' '
				f.write(line + '\n')

class State(object):
	def __init__(self, sence_dist = 10, sence_matrix = None):
		self.sence_dist = sence_dist
		if sence_matrix is None:
			self.sence_matrix = np.ones((self.sence_dist, self.sence_dist))
		else:
			self.sence_matrix = sence_matrix

class RL_Solver(object):
	def __init__(self, alpha = 1, gamma = 0.5, epsilon = 0.1, agent_type = 'q_learning'):
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon
		self.savt = StateActionValueTable('./rl_train_result/snake_memory.txt')
		if agent_type == 'q_learning':
			self.agent = Q_Learning_Agent(self.alpha, self.gamma, self.epsilon)
		elif agent_type == 'sarsa':
			self.agent = Sarsa(self.alpha, self.gamma, self.epsilon)