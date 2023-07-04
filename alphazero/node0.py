import random
from copy import deepcopy
from math import sqrt, inf
import numpy as np
import torch
from .helper import get_device
from ..vanilla_mcts.node import Node
from ..vanilla_mcts.board import Board
class Edge0:
	def __init__(self, owner, move:tuple[int,int], p:float) -> None:
		self.owner:ThinkNode0|InnerNode0 = owner
		self.move = move
		self.w, self.n = 0.0, 0
		self.p = p
		self.node:InnerNode0 = None
	
	@property
	def q(self):
		return self.w/self.n if self.n > 0 else 0

	def __str__(self) -> str:
		s = ''
		s += f'Move:{self.move}\n'
		s += f'Wins:{self.q}, Visits:{self.n}, Prob:{self.p}\n'
		return s

class ThinkNode0(Node):
	def __init__(self, board: Board, last_move: tuple[int, int]):
		super().__init__(board, last_move)
		self.edges:list[Edge0] = []
		self.value = None

	@property
	def isleaf(self):
		return len(self.edges) == 0

	@property
	def sum_visits(self):
		return sum([edge.n for edge in self.edges])

	@property
	def best_edge(self)->Edge0:
		best, best_ucb = None, -inf
		for e in self.edges:
			ucb = self.get_ucb(e)
			if ucb > best_ucb:
				best, best_ucb = e, ucb
			elif ucb == best_ucb:
				keep = random.choice([True, False])
				if not keep: best = e
		return best

	@property
	def tensor_input(self):
		device = get_device()
		# neutral_state = self.player * self.state.data
		# input_state = torch.tensor(
		# 	np.stack((
		# 		neutral_state == 1, 
		# 		neutral_state == -1, 
		# 		neutral_state == 0), axis=0).astype(float),
		# 	dtype = torch.float32, device=device)

		x = np.zeros((Board.max_row, Board.max_col)) # ones
		y = np.zeros((Board.max_row, Board.max_col)) # negative ones
		z = np.zeros((Board.max_row, Board.max_col)) # zeros

		for r in range(Board.max_row):
			for c in range(Board.max_col):
				if self.player*self.state[(r,c)] == 1:
					x[r,c] = 1
				elif self.player*self.state[(r,c)] == -1:
					y[r,c] = 1
				else:
					z[r,c] = 1
		input_state = torch.tensor(
			np.stack((x,y,z), axis=0), dtype=torch.float32, device=device
		)
		return input_state.unsqueeze(0)

	def get_ucb(self, edge:Edge0):
		C = 2
		sum_visits = self.sum_visits
		return edge.q + C * edge.p * sqrt(sum_visits)/(edge.n+1)

	def calculate_policies(self):
		t = 0.5
		sum_visits = self.sum_visits
		self.policies = [edge.n**(1/t)/sum_visits**(1/t) for edge in self.edges]
	
	@property
	def full_policies(self):
		'''create full list of policies from sparse self.policies'''
		max_row, max_col = self.state.max_row, self.state.max_col
		full_p = [0 for _ in range(max_row*max_col)]
		for edge, policy in zip(self.edges, self.policies):
			r, c = edge.move
			index = r * max_col + c
			full_p[index] = policy

		return full_p

class InnerNode0(ThinkNode0):
	def __init__(self, parent:Edge0):
		board, move = deepcopy(parent.owner.state), parent.move
		board[move] = parent.owner.player
		super().__init__(board, move)

		self.parent = parent

from multiprocessing import Pool
if __name__ == "__main__":
	b = np.zeros((Board.max_row, Board.max_col))
	b = Board(b)
	b[(0,5)] = 1
	b[(1,1)] = 1
	b[(2,2)] = 1
	b[(2,3)] = 1
	b[(3,1)] = 1
	b[(3,3)] = 1
	b[(3,4)] = 1
	b[(4,0)] = 1
	b[(4,1)] = 1
	b[(4,4)] = 1
	b[(4,6)] = 1
	b[(5,2)] = 1
	b[(5,7)] = 1
	b[(6,4)] = 1
	b[(7,4)] = 1
	b[(7,7)] = 1
	b[(7,8)] = 1
	b[(8,1)] = 1
	b[(8,3)] = 1
	b[(8,8)] = 1
	b[(9,2)] = 1
	b[(9,5)] = 1
	b[(9,8)] = 1

	b[(1,3)] = -1
	b[(3,5)] = -1
	b[(4,7)] = -1
	b[(5,1)] = -1
	b[(5,4)] = -1
	b[(6,1)] = -1
	b[(6,3)] = -1
	b[(6,6)] = -1
	b[(7,0)] = -1
	b[(7,1)] = -1
	b[(7,2)] = -1
	b[(7,3)] = -1
	b[(7,5)] = -1
	b[(7,6)] = -1
	b[(8,0)] = -1
	b[(8,2)] = -1
	b[(8,4)] = -1
	b[(8,5)] = -1
	b[(9,4)] = -1
	b[(9,6)] = -1
	b[(9,7)] = -1
	b[(9,9)] = -1

	node = ThinkNode0(b, (9,8))

	print(node.state.__str__())
	print(node.tensor_input.shape)
