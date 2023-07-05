import string
from copy import deepcopy # Create a new copy of an object with its own unique memory space
import numpy as np
from ..vanilla_mcts.board import Board

alphabet = list(string.ascii_uppercase) # Create a list of all uppercase letters from A-Z

class TBoard():
	def __init__(self, width, height, winstreak):
		self.width = width
		self.height = height
		self.winstreak = winstreak
		self.reset()
	
	def reset(self): # resets the board to be empty
		self.board = [ ['*' for x in range(self.width+2)] for y in range(self.height+2) ]
		for x in range(1,self.width + 1):
			for y in range(1,self.height + 1):
				self.board[x][y] = ' '

	def set_move(self, pos, player): # sets a move onto the board
		self.board[pos[1]][pos[0]] = player

	def possible_moves(self): # returns list of all empty cells' (x, y)
		moves = [] # Create an empty list of moves to store the positions of the empty cells

		for y, row in enumerate(self.board): # the enumerate return both the index of the row and the row itself
			for x, cell in enumerate(row): ## the enumerate return both the index of the cell and the cell itself
				if cell == ' ':
					moves.append((x, y)) # If the cell is empty, its position is added to the moves list

		return moves # Return list moves
	
	def near_moves(self): # find the possible moves close to the existing ones
		moves = self.possible_moves() # Get list of all possible moves (all empty cells on the board)
		impossible_moves = [] # Store the position of all filled cells
		near_moves = [] # Store the positions of the empty cells that close to the filled ones
		for y, row in enumerate(self.board):
			for x, cell in enumerate(row):
				if cell != ' ' and cell != '*': # If cell is filled
					impossible_moves.append((x, y)) # Added to impossible_moves
		min_height = min(move[0] for move in impossible_moves) # Min height among all filled cells
		max_height = max(move[0] for move in impossible_moves) # Min height among all filled cells
		min_width = min(move[1] for move in impossible_moves) # Min width among all filled cells
		max_width = max(move[1] for move in impossible_moves) # Max width among all filled cells
		for move in moves: # Loop in all empty cells
			if move[0] in range(min_height-2, max_height+3) and move[1] in range(min_width-2, max_width+3): # Find empty cells in range 2
				near_moves.append((move[0], move[1]))
		return near_moves

		


	
	def gameover(self): # returns True if board is full or either player has won
		return len(self.possible_moves()) == 0 or self.iswin('X') or self.iswin('O')

	def iswin(self, player): # checks if a given player has won
		for y in range(1, self.height-self.winstreak+2): # check \ diagonals
			for x in range(1, self.width-self.winstreak+2):
				if all([self.board[y+i][x+i] == player for i in range(self.winstreak)]): # checks if all cells in a row have the player's peg
					return True
		
		for y in range(self.winstreak, self.height + 1): # check / diagonals
			for x in range(1, self.width-self.winstreak+2):
				if all([self.board[y-i][x+i] == player for i in range(self.winstreak)]):
					return True
		
		for y in range(1, self.height + 1): # check horizontals
			for x in range(1, self.width-self.winstreak+2):
				if all([self.board[y][x+i] == player for i in range(self.winstreak)]):
					return True
		
		for y in range(1, self.height-self.winstreak+2): # check verticals
			for x in range(1, self.width + 1):
				if all([self.board[y-i][x] == player for i in range(self.winstreak)]):
					return True

		return False
	
	def good_move(self, player, other_player):
		def count_in_range(moves):
			count = 0
			for move in moves:
				if move == player: count += 1
				elif move == other_player: count -= 1
			return count

		block = [other_player, '*']
		score = 0
		check_condition = True

		for y in range(1, self.height - self.winstreak + 3):  # check \ diagonals
			for x in range(1, self.width - self.winstreak + 3):
				if all([self.board[y + i][x + i] == player for i in range(self.winstreak - 1)]) \
						and not (self.board[y - 1][x - 1] in block or self.board[y + self.winstreak -1][x + self.winstreak -1] in block):
					score += 3.1
					check_condition = False

		if check_condition == True:            
			for y in range(1, self.height - self.winstreak + 3):  # check \ diagonals
				for x in range(1, self.width - self.winstreak + 3):
					if all([self.board[y + i][x + i] == player for i in range(self.winstreak - 1)]) \
							and not (self.board[y - 1][x - 1] in block and self.board[y + self.winstreak -1][x + self.winstreak -1] in block):
						score += 2.1
						check_condition = False

		if check_condition == True:            
			for y in range(1, self.height - self.winstreak + 3):  # check \ diagonals
				for x in range(1, self.width - self.winstreak + 3):
					if count_in_range([self.board[y + i][x + i] for i in range(self.winstreak - 1)]) == 3 \
							and not (self.board[y - 1][x - 1] in block or self.board[y + self.winstreak -1][x + self.winstreak -1] in block):
						score += 1
						check_condition = False

		if check_condition == True:
			for y in range(1, self.height - self.winstreak + 4):  # check \ diagonals
				for x in range(1, self.width - self.winstreak + 4):
					if all([self.board[y + i][x + i] == player for i in range(self.winstreak - 2)]) \
							and not (self.board[y - 1][x - 1] in block or self.board[y + self.winstreak - 2][x + self.winstreak - 2] in block):
						score += 1
						check_condition = False

		if check_condition == True:
			for y in range(1, self.height - self.winstreak + 5):  # check \ diagonals
				for x in range(1, self.width - self.winstreak + 5):
					if all([self.board[y + i][x + i] == player for i in range(self.winstreak - 3)]) \
							and not (self.board[y - 1][x - 1] in block or self.board[y + self.winstreak - 3][x + self.winstreak - 3] in block):
						score += 0.2

		check_conditon = True
		for y in range(self.winstreak - 1, self.height + 1):  # check / diagonals
			for x in range(1, self.width - self.winstreak + 3):
				if all([self.board[y - i][x + i] == player for i in range(self.winstreak-1)]) \
						and not (self.board[y + 1][x - 1] in block or self.board[y - self.winstreak + 1][x + self.winstreak - 1] in block):
					score += 3.1
					check_condition = False

		if check_condition == True:
			for y in range(self.winstreak - 1, self.height + 1):  # check / diagonals
				for x in range(1, self.width - self.winstreak + 3):
					if all([self.board[y - i][x + i] == player for i in range(self.winstreak-1)]) \
							and not (self.board[y + 1][x - 1] in block and self.board[y - self.winstreak + 1][x + self.winstreak - 1] in block):
						score += 2.1
						check_condition = False

		if check_condition == True:
			for y in range(self.winstreak - 1, self.height + 1):  # check / diagonals
				for x in range(1, self.width - self.winstreak + 3):
					if count_in_range([self.board[y - i][x + i] for i in range(self.winstreak-1)]) == 3 \
							and not (self.board[y + 1][x - 1] in block or self.board[y - self.winstreak + 1][x + self.winstreak - 1] in block):
						score += 1
						check_condition = False

		if check_condition == True:
			for y in range(self.winstreak - 2, self.height + 1):  # check / diagonals
				for x in range(1, self.width - self.winstreak + 4):
					if all([self.board[y - i][x + i] == player for i in range(self.winstreak - 2)]) \
							and not (self.board[y + 1][x - 1] in block or self.board[y - self.winstreak + 2][x + self.winstreak - 2] in block):
						score += 1
						check_condition = False

		if check_conditon == True:
			for y in range(self.winstreak - 3, self.height +1):  # check / diagonals
				for x in range(1, self.width - self.winstreak + 5):
					if all([self.board[y - i][x + i] == player for i in range(self.winstreak - 3)]) \
							and not (self.board[y + 1][x - 1] in block or self.board[y - self.winstreak + 3][x + self.winstreak - 3] in block):
						score += 0.2

		check_condition = True
		for y in range(1, self.height + 1):  # check horizontals
			for x in range(1, self.width - self.winstreak + 3):
				if all([self.board[y][x + i] == player for i in range(self.winstreak -1)]) \
						and not (self.board[y][x - 1] in block or self.board[y][x + self.winstreak -1] in block):
					score += 3.1
					check_condition = False

		if check_condition == True:
			for y in range(1, self.height + 1):  # check horizontals
				for x in range(1, self.width - self.winstreak + 3):
					if all([self.board[y][x + i] == player for i in range(self.winstreak -1)]) \
							and not (self.board[y][x - 1] in block and self.board[y][x + self.winstreak -1] in block):
						score += 2.1
						check_condition = False

		if check_condition == True:
			for y in range(1, self.height + 1):  # check horizontals
				for x in range(1, self.width - self.winstreak + 3):
					if count_in_range([self.board[y][x + i] for i in range(self.winstreak -1)]) == 3\
							and not (self.board[y][x - 1] in block or self.board[y][x + self.winstreak -1] in block):
						score += 1
						check_condition = False
		
		if check_condition == True:
			for y in range(1, self.height + 1):  # check horizontals
				for x in range(1, self.width - self.winstreak + 4):
					if all([self.board[y][x + i] == player for i in range(self.winstreak - 2)]) \
							and not (self.board[y][x - 1] in block or self.board[y][x + self.winstreak - 2] in block):
						score += 1
						check_condition = False

		if check_condition == True:
			for y in range(1, self.height +1):  # check horizontals
				for x in range(1, self.width - self.winstreak + 5):
					if all([self.board[y][x + i] == player for i in range(self.winstreak - 3)]) \
							and not (self.board[y][x - 1] in block or self.board[y][x + self.winstreak - 3] in block):
						score += 0.2

		check_condition = True
		for y in range(1, self.height - self.winstreak + 3):  # check verticals
			for x in range(1, self.width + 1):
				if all([self.board[y - i][x] == player for i in range(self.winstreak-1)]) \
						and not (self.board[y + 1][x] in block or self.board[y - self.winstreak - 1][x] in block):
					score += 3.1
					check_condition = False

		if check_condition == True:            
			for y in range(1, self.height - self.winstreak + 3):  # check verticals
				for x in range(1, self.width + 1):
					if all([self.board[y - i][x] == player for i in range(self.winstreak-1)]) \
							and not (self.board[y + 1][x] in block and self.board[y - self.winstreak - 1][x] in block):
						score += 2.1
						check_condition = False

		if check_condition == True:            
			for y in range(1, self.height - self.winstreak + 3):  # check verticals
				for x in range(1, self.width + 1):
					if count_in_range([self.board[y - i][x]  for i in range(self.winstreak-1)]) == 3 \
							and not (self.board[y + 1][x] in block or self.board[y - self.winstreak - 1][x] in block):
						score += 1
						check_condition = False

		if check_condition == True:
			for y in range(self.height - self.winstreak + 4):  # check verticals
				for x in range(1, self.width + 1):
					if all([self.board[y - i][x] == player for i in range(self.winstreak - 2)]) \
							and not (self.board[y + 1][x] in block or self.board[y - self.winstreak + 2][x] in block):
						score += 1
						check_condition = False

		if check_condition == True:
			for y in range(1, self.height - self.winstreak + 5):  # check verticals
				for x in range(1, self.width + 1):
					if all([self.board[y - i][x] == player for i in range(self.winstreak - 3)]) \
							and not (self.board[y + 1][x] in block or self.board[y - self.winstreak + 3][x] in block):
						score += 0.2
		return score
	def evaluate(self, player):
		other_player = 'O' if player == 'X' else 'X'
		score = 0
		score += self.good_move(player, other_player)
		score -= self.good_move(other_player, player)*1.5

		if self.iswin(player):
			return 10
		elif self.iswin(other_player):
			return -10
		
		else:
			return score
	
	def render(self): # displays to terminal

		print(f"  {'   '.join([str((i+1)%10) for i in range(self.width)])}")

		for index, row in enumerate(self.board):
			if index == 0: continue
			if index == self.height+1: break
			print(f"{str(index%10)} {' | '.join(row[1:-1])}")
			if index < self.height:
				print(" "+ '-'*(self.width*4-1))
	
	def convert_to_binh_board(self):
		binh_board = [[0 for _ in range(self.height)] for _ in range(self.width)]
		for i in range(1, self.height+1):
			for j in range(1, self.width+1):
				if self.board[i][j] == 'X': binh_board[i-1][j-1] = 1
				elif self.board[i][j] == 'O': binh_board[i-1][j-1] = -1
		return binh_board

				



if __name__ == '__main__':
	board = TBoard(10, 10, 5)
	board.set_move((5,5), player = 'X')
	print(board.board)
	binh_board = board.convert_to_binh_board()
	bboard = Board(binh_board)
	print(bboard)