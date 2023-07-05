from .board import Board
from .mcts import MCTS
from .node import Node
from .help_node import HelpNode

import tkinter as tk
import tkinter.font as font
from tkinter import messagebox

class TicTacToe:
	def __init__(self, root:tk.Tk) -> None:
		root.bind('<Return>', self.process)

		self.choose_frame = tk.Frame(root)
		self.__init__choose_frame()
		self.choose_frame.pack()

		self.game_frame = tk.Frame(root)

		self.buttons:list[list[tk.Button]] = [
			[None for _ in range(Board.max_col)] for _ in range(Board.max_row)
		]
		for i in range(Board.max_row):
			for j in range(Board.max_col):
				button = tk.Button(
					self.game_frame,
					width=2, height=1,
					command=lambda pos=(i,j):self.click(pos),
				)
				button.grid(row=i, column=j)
				self.buttons[i][j] = button


		self.vmap = {1:'X', -1:'O'}
		self.board = Board()
		self.free_space = Board.max_row*Board.max_col
		self.select_move = None

	def __init__choose_frame(self):
		myfont = font.Font(size=12)
		tk.Button(
			self.choose_frame,
			text='X', font=myfont,
			width=25, height=20,
			command=self.human_first
		).pack(fill=tk.Y, side=tk.LEFT)

		tk.Button(
			self.choose_frame,
			text='O', font=myfont,
			width=25, height=20,
			command=self.bot_first
		).pack(fill=tk.Y, side=tk.LEFT)
		
	def human_first(self):
		self.choose_frame.forget()
		self.game_frame.pack(fill=tk.BOTH)

		self.human_player = 1
		self.bot_player = -1

	def bot_first(self):
		self.choose_frame.forget()
		self.game_frame.pack(fill=tk.BOTH)

		self.human_player = -1
		self.bot_player = 1

		self.bot_play()
		i, j = self.bot_move
		self.buttons[i][j].configure(text=self.vmap[self.bot_player])
		self.board[self.bot_move] = self.bot_player

	def click(self, pos:tuple[int, int]):
		# print(pos)
		if self.select_move:
			r, c = self.select_move
			self.buttons[r][c].configure(text='')

		self.select_move = pos
		r, c = pos
		self.buttons[r][c].configure(text=self.vmap[self.human_player])

	def process(self, _):
		'''Internal process after user press Enter'''
		self.free_space -= 1
		if not self.select_move:
			return messagebox.showerror('Error', 'Please choose your move!')

		self.__disable_buttons()
		self.board[self.select_move] = self.human_player

		# check win for human
		human_result = self.__check_win(self.select_move)
		if human_result == 1:
			messagebox.showinfo('Game end', 'Human wins!')
			return self.reset()
		elif human_result == 0:
			messagebox.showinfo('Game end', 'Draw!')
			return self.reset()
			
		# bot_play here
		self.bot_play()

		i, j = self.bot_move
		self.buttons[i][j].configure(text=self.vmap[self.bot_player])
		self.board[self.bot_move] = self.bot_player

		# check win for bot
		bot_result = self.__check_win(self.bot_move)
		if bot_result == 1:
			messagebox.showinfo('Game end', 'Bot wins!')
			return self.reset()
		elif bot_result == 0:
			messagebox.showinfo('Game end', 'Draw!')
			return self.reset()

		self.select_move = None
		self.__enable_buttons()

	def reset(self):
		self.board = Board()
		self.select_move = None
		self.free_space = Board.max_row*Board.max_col

		for row in self.buttons:
			for button in row:
				button.configure(text='')

		self.__enable_buttons()

		self.game_frame.forget()
		self.choose_frame.pack(fill=tk.BOTH)

	def bot_play(self):
		mcts = MCTS(self.board, self.select_move, depth=6, max_sims=2000)
		mcts.think()
		self.bot_move = mcts.advise().last_move

		self.free_space -= 1

	def __check_win(self, move:tuple[int, int]):
		player = -self.board[move]
		if HelpNode.check_lose(self.board, move, player):
			return 1

		print(self.free_space)
		if self.free_space == 0: return 0

	def __disable_buttons(self):
		for row in self.buttons:
			for button in row:
				button.configure(state=tk.DISABLED)

	def __enable_buttons(self):
		for row in self.buttons:
			for button in row:
				if button['text'] == '': button.configure(state=tk.ACTIVE)
	
if __name__ == "__main__":
	window = tk.Tk()
	window.title('tic tac toe game'.capitalize())
	ttt = TicTacToe(window)
	window.mainloop()