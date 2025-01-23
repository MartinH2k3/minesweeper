from point import Point
import random

class Board:
    def __init__(self, size: int, mine_count: int):
        self.size = size
        self.mine_count = mine_count
        self.board: list[list[int]] = [[0] * size for _ in range(size)]
        self.revealed: list[list[bool]] = [[False] * size for _ in range(size)]
        self._generate_mines()

    def _generate_mines(self):
        mines = random.sample(range(self.size ** 2), self.mine_count)
        for mine in mines:
            self.board[mine // self.size][mine % self.size] = -1
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != -1:
                    self.board[i][j] = self._count_adjacent_mines(Point(i, j))

    def _is_mine(self, point: Point):
        return self.board[point.x][point.y] == -1

    def _count_adjacent_mines(self, point: Point):
        count = 0
        for p in point.neighbors(True):
            if p.within(self.board) and self._is_mine(p):
                count += 1
        return count

    def _reveal(self, point: Point):
        if not point.within(self.board) or self.revealed[point.x][point.y]:
            return
        self.revealed[point.x][point.y] = True
        if self.board[point.x][point.y] == 0:
            for p in point.neighbors(True):
                self._reveal(p)