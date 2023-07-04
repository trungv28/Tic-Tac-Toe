from .vanilla_mcts.board import Board, MAX_ROW, MAX_COL
from .vanilla_mcts.mcts import MCTS
from .vanilla_mcts.node import Node

from .alphazero.mcts0 import MCTS0
from .alphazero.model import NeuralNetwork
from .alphazero.helper import get_device

import torch
import tkinter as tk
import tkinter.font as font
from tkinter import messagebox
import numpy as np

class TicTacToe:
	def __init__(self, root:tk.Tk) -> None:
		root.bind('<Return>', self.process)

		self.choose_frame = tk.Frame(root)
		self.__init__choose_frame()
		self.choose_frame.pack()

		self.game_frame = tk.Frame(root)

		self.buttons:list[list[tk.Button]] = [
			[None for _ in range(MAX_COL)] for _ in range(MAX_ROW)
		]
		for i in range(MAX_ROW):
			for j in range(MAX_COL):
				button = tk.Button(
					self.game_frame,
					width=2, height=1,
					command=lambda pos=(i,j):self.click(pos),
				)
				button.grid(row=i, column=j)
				self.buttons[i][j] = button


		self.vmap = {1:'X', -1:'O'}
		self.board = Board(np.zeros((MAX_ROW, MAX_COL)))
		self.select_move = None

		# nn_args = {
		# 	'num_filter': 32,
		# 	'filter_size': 3,
		# 	'hidden_size': 128, # for policy head
		# 	'num_block': 9 # for resnet (should be 19 or 39)
		# }
		# self.model = NeuralNetwork(nn_args, get_device())
		# path = './runs/iteration_7.pt'
		# self.model.load_state_dict(torch.load(path))

	def __init__choose_frame(self):
		myfont = font.Font(size=15)
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
		self.board = Board(np.zeros((MAX_ROW, MAX_COL)))
		self.select_move = None

		for row in self.buttons:
			for button in row:
				button.configure(text='')

		self.__enable_buttons()

		self.game_frame.forget()
		self.choose_frame.pack(fill=tk.BOTH)

	def bot_play(self):
		sims_per, max_sims = 100, 1000
		mcts = MCTS(self.board, self.select_move, sims_per, max_sims)
		mcts.search()
		self.bot_move = mcts.advise().move

		# mcts = MCTS0(self.board, self.select_move, self.model, sims_per, max_sims)
		# mcts.search()
		# self.bot_move = mcts.advise().move

	def __check_win(self, move:tuple[int, int]):
		node = Node(self.board, move)
		if node.check_lose():
			return 1

		if not node.get_moves():
			return 0

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