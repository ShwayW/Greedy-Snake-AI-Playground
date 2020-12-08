# Author: Shway Wang
# Date: 2020/12/3
import numpy as np
from rl_agents import *
# Actions of snake:
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
NOTHING = 4

class StateActionValueTable(object):
	def __init__(self, path):
		self.path = path
		self.content = dict()
		self.load_data()

	def addNewStateActionSet(self, cur_state, action_values):
		# action_values is a dictionary of key:action val:values
		self.content[cur_state] = action_values

	def getStateActionValue(self, state, action):
		return self.content[state][action]

	def setStateActionValue(self, state, action, value):
		self.content[state][action] = value

	def deserialize(self, str_vec):
		raw_matrix = str_vec.split(';')
		row_num = len(raw_matrix)
		temp = raw_matrix[0].split(',')
		col_num = len(temp)
		sence_matrix = np.zeros((row_num, col_num))
		for i in range(len(raw_matrix)):
			vec = raw_matrix[i].split(',')
			for j in range(len(vec)):
				sence_matrix[i][j] = int(vec[j])
		return sence_matrix

	def load_data(self):
		with open(self.path, 'r') as f:
			content = dict()
			f_content = f.readline()
			while f_content:
				elements = f_content.split()
				sence_matrix = self.deserialize(elements.pop(0))
				value = dict()
				for i in elements:
					subkey_subvalue = i.split(':')
					realSubkey = int(subkey_subvalue[0])
					value[realSubkey] = float(subkey_subvalue[1])
				content[State(sence_matrix)] = value
				f_content = f.readline()
		self.content = content

	def safe_data(self):
		with open(self.path, 'w') as f:
			for i in self.content:
				line = ''
				line += i.serialize() + ' '
				for j in self.content[i]:
					line += str(j) + ':' + str(self.content[i][j]) + ' '
				f.write(line + '\n')

class State(object):
	def __init__(self, sence_matrix = None):
		if sence_matrix is None:
			self.sence_matrix = np.ones((self.sence_dist, self.sence_dist))
		else:
			self.sence_matrix = sence_matrix

	def __hash__(self):
		return hash(self.serialize())

	def __eq__(self, other):
		if not isinstance(other, State):
			return NotImplemented
		return other.serialize() == self.serialize()

	def __ne__(self, other):
		if not isinstance(other, State):
			return NotImplemented
		return other.serialize() != self.serialize()

	def serialize(self):
		serial = ''
		for i in self.sence_matrix:
			for j in i:
				serial += str(int(j)) + ','
			serial = serial[:-1]
			serial += ';'
		serial = serial[:-1]
		return serial

class RL_Solver(object):
	def __init__(self, alpha = 1, gamma = 0.8, epsilon = 0.1, agent_type = 'q_learning'):
		self.alpha = alpha
		self.gamma = gamma
		self.epsilon = epsilon
		self.savt = StateActionValueTable('./rl_train_result/snake_memory.txt')
		if agent_type == 'q_learning':
			self.agent = Q_Learning_Agent(self.alpha, self.gamma, self.epsilon)
		elif agent_type == 'sarsa':
			self.agent = Sarsa_Agent(self.alpha, self.gamma, self.epsilon)