from .node import Node
from .board import Board
from .mcts import MCTS
import numpy as np
class Game:
	def __init__(self) -> None:
		x = np.zeros((Board.max_row, Board.max_col))
		self.board = Board(x)

		self.human_player = int(input("Please choose your player: (-1 for O), (1 for X):"))
		self.last_move = None

	def valid_move(self, move:tuple[int, int]):
		r, c = move
		if r < -1 or r > self.board.max_row: return False
		if c < -1 or c > self.board.max_col: return False
		if self.board[move] != 0: return False

		return True
		
	def human_phase(self):
		r, c = input('Enter your move: ').split()
		human_move = (int(r), int(c))
		if not self.valid_move(human_move):
			raise ValueError("Invalid move")
		
		self.board[human_move] = self.human_player
		print(self.board)
		node = Node(self.board, human_move)

		if node.check_lose(): return self.human_player
		if not node.get_moves(): return 0

		self.last_move = human_move

	def bot_phase(self):
		sims_per = 100
		mcts = MCTS(self.board, self.last_move, sims_per) 
		mcts.search()

		bot_move = mcts.advise().move
		self.board[bot_move] = -self.human_player

		print(self.board)
		node = Node(self.board, bot_move)

		if node.check_lose(): return -self.human_player
		if not node.get_moves(): return 0

		self.last_move = bot_move

	def play(self):
		r = None
		print(self.board)
		while True:
			if self.human_player == 1:
				r = self.human_phase()
				if r is not None: return r

				r = self.bot_phase()
				if r is not None: return r

			else:
				r = self.bot_phase()
				if r is not None: return r

				r = self.human_phase()
				if r is not None: return r


game = Game()
result = game.play()
if result == game.human_player:
	print("Human wins")
elif result == 0:
	print("Draw")
else:
	print("Bot wins")


				



