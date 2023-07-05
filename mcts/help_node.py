from .board import Board
from copy import deepcopy

class HelpNode:
	def __init__(self, original_board: Board, last_move:tuple[int, int]):
		self.board = deepcopy(original_board)
		self.player = -original_board[last_move] if last_move else 1
		self.last_move = last_move
		self.possible_moves = self.get_random_moves()

		# revert() purpose
		self.original_board = deepcopy(original_board)
		self.original_player = self.player
		self.initial_move = last_move
		self.available_moves = deepcopy(self.possible_moves)

	def revert(self):
		self.board = deepcopy(self.original_board)
		self.player = self.original_player
		self.last_move = self.initial_move
		self.possible_moves = deepcopy(self.available_moves)

	def get_random_moves(self):
		if not self.last_move:
			ru, rd = Board.max_row//2 -1, Board.max_row//2 +1
			cl, cr = Board.max_col//2 -1, Board.max_col//2 +1
			return {(i,j) for i in range(ru, rd+1) for j in range(cl, cr+1)}

		moves:set[tuple[int, int]] = set()
		for i in range(Board.max_row):
			for j in range(Board.max_col):
				if self.board[(i,j)] == 0: continue
				moves |= self.get_point_moves(pos=(i,j))
		return moves

	def get_point_moves(self, pos:tuple[int, int]):
		if self.board[pos] == 0:
			raise ValueError("Nothing to get moves!")

		r, c = pos
		ru, rd = max(r-2, 0), min(r+2, Board.max_row-1)
		cl, cr = max(c-2, 0), min(c+2, Board.max_col-1)

		return {
			(i,j) for i in range(ru, rd+1) for j in range(cl, cr+1)
			if self.board[(i,j)] == 0
		}

	def update(self, move:tuple[int, int]):
		self.board[move] = self.player
		self.player *= -1
		self.last_move = move

		self.possible_moves.remove(move)
		self.possible_moves |= self.get_point_moves(move)

	def local_check_lose(self):
		return HelpNode.check_lose(self.board, self.last_move, self.player)

	def get_advanced_moves(self):
		for move in self.possible_moves:
			if HelpNode.check_lose(self.board, move, -self.player): return [move]

		for move in self.possible_moves:
			if HelpNode.check_lose(self.board, move, self.player): return [move]

		for move in self.possible_moves:
			if HelpNode.check_lose_next(self.board, move, -self.player): return [move]

		return None

	@staticmethod
	def check_lose(state:Board, move:tuple[int, int], player) :
		'''Return True if player lose after last move'''

		# start state do not lose
		if move is None: return False

		max_row, max_col = Board.max_row, Board.max_col
		streak = 5 if (max_row >=5 and max_col >=5) else 3
		r, c = move
		opp = -player

		# check column
		ru, rd = r, r
		while ru-1 > -1 and state[(ru-1, c)] == opp: ru -= 1
		while rd+1 < max_row and state[(rd+1, c)] == opp: rd += 1
		if rd-ru+1 >= streak: return True

		# check row
		cl, cr = c, c
		while cl-1 > -1 and state[(r, cl-1)] == opp: cl -= 1
		while cr+1 < max_col and state[(r, cr+1)] == opp: cr += 1
		if cr-cl+1 >= streak: return True

		# check \
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cl-1 > -1 and state[(ru-1, cl-1)] == opp:
			ru, cl = ru-1, cl-1
		while rd+1 < max_row and cr+1 < max_col and state[(rd+1, cr+1)] == opp:
			rd, cr = rd+1, cr+1
		if rd-ru+1 >= streak: return True

		# check /
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cr+1 < max_col and state[(ru-1, cr+1)] == opp:
			ru, cr = ru-1, cr+1
		while rd+1 < max_row and cl-1 > -1 and state[(rd+1, cl-1)] == opp:
			rd, cl = rd+1, cl-1
		if rd-ru+1 >= streak: return True

		return False

	@staticmethod
	def check_lose_next(state:Board, move:tuple[int, int], player) :

		# start state do not lose
		if move is None: return False

		max_row, max_col = Board.max_row, Board.max_col
		streak = 4 if (max_row >=5 and max_col >=5) else 2
		r, c = move
		opp = -player

		# check column
		ru, rd = r, r
		while ru-1 > -1 and state[(ru-1, c)] == opp: ru -= 1
		while rd+1 < max_row and state[(rd+1, c)] == opp: rd += 1
		if rd-ru+1 >= streak:
			if (ru-1 > -1 and rd+1 < max_row) and \
			(state[(ru-1, c)] == 0 and state[(rd+1, c)] == 0):
				return True

		# check row
		cl, cr = c, c
		while cl-1 > -1 and state[(r, cl-1)] == opp: cl -= 1
		while cr+1 < max_col and state[(r, cr+1)] == opp: cr += 1
		if cr-cl+1 >= streak:
			if (cl-1 > -1 and cr+1 < max_row) and \
			(state[(r, cl-1)] == 0 and state[(r, cr+1)] == 0):
				return True

		# check \
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cl-1 > -1 and state[(ru-1, cl-1)] == opp:
			ru, cl = ru-1, cl-1
		while rd+1 < max_row and cr+1 < max_col and state[(rd+1, cr+1)] == opp:
			rd, cr = rd+1, cr+1
		if rd-ru+1 >= streak:
			if (ru-1 > -1 and cl-1 > -1 and rd+1 < max_row and cr+1 < max_col) \
			and (state[(ru-1, cl-1)] == 0 and state[((rd+1, cr+1))] == 0):
				return True

		# check /
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cr+1 < max_col and state[(ru-1, cr+1)] == opp:
			ru, cr = ru-1, cr+1
		while rd+1 < max_row and cl-1 > -1 and state[(rd+1, cl-1)] == opp:
			rd, cl = rd+1, cl-1
		if rd-ru+1 >= streak:
			if (ru-1 > -1 and cl-1 > -1 and rd+1 < max_row and cr+1 < max_col) \
			and (state[(ru-1, cr+1)] == 0 and state[((rd+1, cl-1))] == 0):
				return True

		return False

from ._config import config_board
if __name__ == "__main__":
	b = Board()
	last_move = config_board(b)
	player = b[last_move] if last_move else 1
	print(b)
	print(HelpNode.check_lose_next(b, (5,8), -1))





	