from copy import deepcopy
from .board import Board

class Node:
	def __init__(self, board:Board, last_move:tuple[int, int]):
		self.state = deepcopy(board)
		self.last_move = last_move
		self.player = -board[last_move] if last_move else 1

	def check_lose(self):
		return self.__check_win_now(self.last_move, -self.player)

	def get_random_moves(self):
		max_row, max_col = Board.max_row, Board.max_col

		if self.last_move is None: # start state
			ru, rd = max_row//2 -1, max_row//2 +1
			cl, cr = max_col//2 -1, max_col//2 +1
			
			return [
				(i, j) for i in range(ru, rd+1) for j in range(cl, cr+1)
			]

		moves:set[tuple[int, int]] = set()

		for r in range(max_row):
			for c in range(max_col):
				if self.state[(r,c)] == 0: continue
				moves = moves | self.__get_point_moves((r,c), 2)

		return list(moves)

	def get_moves(self):
		moves = self.get_random_moves()

		# heuristic
		# if can win now, play it!
		for move in moves:
			if self.__check_win_now(move, self.player): return [move]

		# if opponent can win now, prevent it!
		for move in moves:
			if self.__check_win_now(move, -self.player): return [move]
		
		# if can play 2 ways 4 streak, play it!
		for move in moves:
			result, _ = self.__check_win_next(move, self.player)
			if result: return [move]

		# no special cases
		return moves

	def __get_point_moves(self, pos:tuple[int, int], pad:int):
		r, c = pos
		max_row, max_col = Board.max_row, Board.max_col
		ru, rd = max(r-pad, 0), min(r+pad, max_row-1)
		cl, cr = max(c-pad, 0), min(c+pad, max_col-1)

		return {
			(i, j) for i in range(ru, rd+1) for j in range (cl, cr+1)
			if self.state[(i, j)] == 0
		}

	def __check_win_now(self, move:tuple[int, int], player:int):
		# start state do not lose
		if move is None: return False

		max_row, max_col = Board.max_row, Board.max_col
		streak = 5 if (max_row >=5 and max_col >=5) else 3
		r, c = move

		# check column
		ru, rd = r, r
		while ru-1 > -1 and self.state[ru-1, c] == player: ru -= 1
		while rd+1 < max_row and self.state[rd+1, c] == player: rd += 1
		if rd-ru+1 >= streak: return True

		# check row
		cl, cr = c, c
		while cl-1 > -1 and self.state[r, cl-1] == player: cl -= 1
		while cr+1 < max_col and self.state[r, cr+1] == player: cr += 1
		if cr-cl+1 >= streak: return True

		# check \
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cl-1 > -1 and self.state[ru-1, cl-1] == player:
			ru, cl = ru-1, cl-1
		while rd+1 < max_row and cr+1 < max_col and self.state[rd+1, cr+1] == player:
			rd, cr = rd+1, cr+1
		if rd-ru+1 >= streak: return True

		# check /
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cr+1 < max_col and self.state[ru-1, cr+1] == player:
			ru, cr = ru-1, cr+1
		while rd+1 < max_row and cl-1 > -1 and self.state[rd+1, cl-1] == player:
			rd, cl = rd+1, cl-1
		if rd-ru+1 >= streak: return True

		return False
	
	def __check_win_next(self, move:tuple[int, int], player:int):
		'''
		2-way 4 connects win next move \n
		Return additonal start and end positions if True
		'''
		# start state do not lose
		if move is None: return False

		max_row, max_col = Board.max_row, Board.max_col
		streak = 4 if (max_row >=5 and max_col >=5) else 2
		r, c = move

		# check column
		ru, rd = r, r
		while ru-1 > -1 and self.state[ru-1, c] == player: ru -= 1
		while rd+1 < max_row and self.state[rd+1, c] == player: rd += 1
		if rd-ru+1 == streak:
			if (ru-1 > -1 and rd+1 < max_row) and \
			self.state[(ru-1, c)] == 0 and self.state[(rd+1, c)] == 0:
				return True, ((ru, c), (rd, c))

		# check row
		cl, cr = c, c
		while cl-1 > -1 and self.state[r, cl-1] == player: cl -= 1
		while cr+1 < max_col and self.state[r, cr+1] == player: cr += 1
		if cr-cl+1 == streak:
			if (cl-1 > -1 and cr+1 < max_col) and \
			self.state[(r, cl-1)] == 0 and self.state[(r, cr+1)] == 0:
				return True, ((r, cl), (r, cr))

		# check \
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cl-1 > -1 and self.state[ru-1, cl-1] == player:
			ru, cl = ru-1, cl-1
		while rd+1 < max_row and cr+1 < max_col and self.state[rd+1, cr+1] == player:
			rd, cr = rd+1, cr+1

		if rd-ru+1 == streak:
			if (ru-1 > -1 and cl-1 > -1) and (rd+1 < max_row and cr+1 < max_col) and \
			self.state[(ru-1, cl-1)] == 0 and self.state[(rd+1, cr+1)] == 0:
				return True, ((ru, cl), (rd, cr))

		# check /
		ru, rd, cl, cr = r, r, c, c
		while ru-1 > -1 and cr+1 < max_col and self.state[ru-1, cr+1] == player:
			ru, cr = ru-1, cr+1
		while rd+1 < max_row and cl-1 > -1 and self.state[rd+1, cl-1] == player:
			rd, cl = rd+1, cl-1

		if rd-ru+1 == streak:
			if (ru-1 > -1 and cr+1 < max_col) and (rd+1 < max_row and cl-1 > -1) and \
			self.state[(ru-1, cr+1)] == 0 and self.state[(rd+1, cl-1)] == 0:
				return True, ((ru, cr), (rd, cl))

		return False, None

import numpy as np
if __name__ == "__main__":
	x = np.zeros((Board.max_row, Board.max_col))
	b = Board(x)

	b[(2,8)] = 1
	b[(4,6)] = 1
	b[(5,5)] = 1

	b[(6,6)] = -1
	b[(7,7)] = -1
	b[(8,8)] = -1


	print(b)

	node = Node(b, (5,5))

	moves = node.get_moves()
	print(moves)
