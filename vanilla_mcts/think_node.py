import random
from math import inf, sqrt, log
from copy import deepcopy
from .board import Board
from .node import Node
class Edge:
	def __init__(self, owner, move:tuple[int,int]) -> None:
		self.owner:InnerNode|ThinkNode = owner
		self.move = move
		self.w, self.n = 0, 0
		self.node:InnerNode = None
	
	@property
	def q(self):
		return self.w/self.n if self.n > 0 else 0

class ThinkNode(Node):
	def __init__(self, board: Board, last_move: tuple[int, int]):
		super().__init__(board, last_move)
		self.edges:list[Edge] = []

	@property
	def isleaf(self):
		return len(self.edges) == 0

	@property
	def best_edge(self) -> Edge:
		self.sum_visits = sum([edge.n for edge in self.edges])

		best, best_ucb = [], -inf
		for edge in self.edges:
			ucb =  self.get_ucb(edge)
			if ucb == best_ucb: best.append(edge)
			elif ucb > best_ucb:
				best = [edge]
				best_ucb = ucb

		return random.choice(best)

	def get_ucb(self, edge:Edge):
		return inf if edge.n == 0 else \
			edge.q + sqrt(2) * sqrt(log(self.sum_visits)/edge.n)

class InnerNode(ThinkNode):
	def __init__(self, parent:Edge):
		board, move = deepcopy(parent.owner.state), parent.move
		board[move] = parent.owner.player
		super().__init__(board, move)

		self.parent = parent
