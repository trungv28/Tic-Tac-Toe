import random
from copy import deepcopy
from time import sleep

from .board import Board
from .node import Node

class SimulateNode(Node):
	def __init__(self, brother:Node):
		board, move = brother.state, brother.last_move
		super().__init__(board, move)
		
	def simulate(self):
		original_player = self.player
		while True:
			moves = self.get_moves()
			if not moves: return 0.5 # no more moves mean draw
			move = random.choice(moves)

			self.state[move] = self.player
			# print(self.state)
			self.last_move = move
			self.player = -self.player

			if self.check_lose():
				return 0 if self.player == original_player else 1

import numpy as np

if __name__ == "__main__":
	x = np.zeros((Board.max_row, Board.max_col))
	b = Board(x)

	w, n = 0, 0
	for i in range(10):
		node = Node(b, None)
		sn = SimulateNode(node)
		w += sn.simulate()
		n += 1
		print(w, n)