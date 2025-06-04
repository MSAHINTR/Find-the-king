import random

BOARD_SIZE = 5

class Cell:
    def __init__(self, value):
        self.value = value  # "K", "💀", 1-5, or 0 (nötr)
        self.opened = False

class GameBoard:
    def __init__(self):
        self.board = [[Cell(0) for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.setup_board()

    def setup_board(self):
        values = [1, 2, 3, 4, 5] * 2 + ["K"] + ["💀"] * 3 + [0] * 9  # 25 hücre
        random.shuffle(values)
        idx = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.board[i][j].value = values[idx]
                idx += 1

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    neighbors.append((nx, ny, self.board[nx][ny]))
        return neighbors

class Player:
    def __init__(self):
        self.cards = {1: 2, 2: 2, 3: 2, 4: 2, 5: 2}
        self.score = 0
        self.history = []

