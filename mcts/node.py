from ._param import C
from math import inf, sqrt, log
import random

class Node:
	def __init__(self, move:tuple[int, int]) -> None:
		self.last_move = move
		self.children:list['Node'] = []
		self.w, self.n = 0.0, 0

	@property
	def q(self):
		return 0 if self.n == 0 else self.w/self.n

	@property
	def isleaf(self):
		return len(self.children) == 0

	@property
	def best_child(self) -> 'Node':
		best, best_ucb = None, -inf
		for child in self.children:
			ucb = self.get_ucb(child)
			if ucb == best_ucb: # -> best != None
				best = random.choice([best, child])

			elif ucb > best_ucb:
				best, best_ucb = child, ucb

		return best

	def get_ucb(self, child:'Node'):
		return inf if child.n == 0 else \
		(1-child.q) + C * sqrt(log(self.n)/child.n)