from .board import Board
from .node import Node
from .help_node import HelpNode
from .sim_node import SimNode
import random

class MCTS:
	def __init__(self, board:Board, last_move:tuple[int, int],
					depth=0, max_sims=1):

		self.helper = HelpNode(board, last_move)

		self.depth = depth if depth > 0 else Board.max_row*Board.max_col
		self.max_sims = max_sims

		self.root = Node(last_move)
		self.chosen_nodes:list[Node] = []

	def advise(self)->Node|None:
		if len(self.root.children) == 0: return None
		if len(self.root.children) == 1: return self.root.children[0]

		best, most_visited = None, 0
		for child in self.root.children:
			if child.n == most_visited:
				best = random.choice([best, child])
			elif child.n > most_visited:
				best, most_visited = child, child.n

		return best

	def think(self):
		# for root node
		self.search()
		if len(self.root.children) <= 1: return

		for i in range(self.max_sims):
			# print(f'sim no.{i+1}:')
			self.search()

	def search(self):
		self.helper.revert()
		self.chosen_nodes.clear()
		self.select()
		value = self.evaluate()
		self.backprop(value)

	def select(self):
		node = self.root
		while not node.isleaf:
			node = node.best_child
			self.helper.update(node.last_move)
			self.chosen_nodes.append(node)

	def evaluate(self):
		sim_node = SimNode(self.helper, self.depth)
		value = sim_node.simulate()

		selected_node = self.chosen_nodes[-1] \
				if self.chosen_nodes else self.root
		selected_node.children += sim_node.children

		return value

	def backprop(self, value:int):
		n = len(self.chosen_nodes)
		for i in range(n):
			node = self.chosen_nodes[i]

			node.w += value if (n-i)%2 == 1 else 1-value
			node.n += 1

		self.root.w += value if n%2 == 0 else 1-value
		self.root.n += 1

from ._config import config_board
from time import time
if __name__ == '__main__':
	b = Board()
	last_move = config_board(b)

	mcts = MCTS(b, last_move, depth=4, max_sims=1000)
	print(b)
	start = time()
	mcts.think()
	end = time()
	print(f'total time:{end-start}')
	print(mcts.advise().last_move)