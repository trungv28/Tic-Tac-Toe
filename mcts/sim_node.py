from .board import Board
from .node import Node
from .help_node import HelpNode
import random

class SimNode:
	def __init__(self, helper:HelpNode, depth:int) -> None:
		self.helper = helper
		self.player = helper.player
		self.depth = depth

		self.children:list[Node] = []

	def simulate(self)->float:
		for i in range(self.depth):
			result = self.__check_result()
			if result is not None: return result
			self.__get_moves()
			self.__update(i)

		# additional sims:
		while True:
			result = self.__check_result()
			if result is not None: return result

			self.__get_moves()
			if len(self.moves) > 1: break
			self.__update()

		# reach here means we end additonal sims -> draw
		return 0.5

	def __check_result(self)->float|None:
		# check endgame!
		if self.helper.local_check_lose():
			return 0 if self.helper.player == self.player else 1

		# check draw
		if not self.helper.possible_moves: return 0.5

		return None

	def __get_moves(self)->float|None:
		advanced_moves = self.helper.get_advanced_moves()
		# print(advanced_moves) if advanced_moves else None
		self.moves = list(self.helper.possible_moves) \
			if not advanced_moves else advanced_moves

	def __update(self, i:int=-1):
		if i == 0:
			self.children += [Node(m) for m in self.moves]
		choice = random.choice(self.moves)

		# change board and possible moves
		self.helper.update(choice)
		# print(self.helper.board)

from ._config import config_board
if __name__ == '__main__':
	b = Board()
	last_move = config_board(b)
	helper = HelpNode(b, last_move)
	snode = SimNode(helper, depth=10)
	print(snode.simulate())
	
