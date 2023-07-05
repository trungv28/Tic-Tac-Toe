from ._param import MAX_COL, MAX_ROW
class Board:
	max_row, max_col = MAX_ROW, MAX_COL
	def __init__(self):
		self.data = [
			[0 for _ in range(Board.max_col)]
			for _ in range(Board.max_row)
		]

	def __getitem__(self, pos:tuple[int, int]):
		r, c = pos
		return self.data[r][c]

	def __setitem__(self, pos:tuple[int, int], v:int):
		r, c = pos
		self.data[r][c] = v

	def __str__(self) -> str:
		vmap = {1:'X', -1:'O', 0:'-'}
		s = ''
		for i in range(Board.max_row):
			for j in range(Board.max_col):
				s += str(vmap[self[(i,j)]]) + ' '
			s += '\n'
		return s

if __name__ == "__main__":
	b = Board()
	b[(5,6)] = 1
 
	print(b)