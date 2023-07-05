from copy import deepcopy
MAX_ROW = 20
MAX_COL = 20

class Board:
	max_row, max_col = MAX_ROW, MAX_COL
	def __init__(self, matrix:list[list[int]]) -> None:
		max_r, max_c = len(matrix), len(matrix[0])
		if max_r != self.max_row or max_c != self.max_col:
			raise ValueError("Invalid input!")
		
		self.data = deepcopy(matrix)

	def __getitem__(self, pos:tuple[int, int]):
		r, c = pos
		return self.data[r][c]
	def __setitem__(self, pos:tuple[int, int], v:int):
		r, c = pos
		self.data[r][c] = v

	def __str__(self) -> str:
		vmap = {1:'X', -1:'O', 0:'_'}
		s = ''
		for r in range(self.max_row):
			for c in range(self.max_col):
				value = self[(r,c)]
				s += f'{vmap[value]} '
			s += '\n'
		s += '\n'
		return s

	

if __name__ == "__main__":
	x = [
		[1, 0, 0],
		[0, -1, -1],
		[0, 0, 1],
	]
	b = Board(x)
	print(b)
	b[(2,1)] = 1
	print(b)
	