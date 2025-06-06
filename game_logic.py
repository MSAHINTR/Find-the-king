import random

BOARD_SIZE = 5

class Cell:
    def __init__(self, value):
        self.value = value
        self.opened = False

class GameBoard:
    def __init__(self):
        self.board = [[Cell(0) for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.setup_board()

    def setup_board(self):
        values = (
            [1] * 7 +
            [2] * 4 +
            [3] * 4 +
            [4] * 4 +
            [5] * 3 +
            ["K"] +
            ["💀"] * 2
        )
        random.shuffle(values)
        idx = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.board[i][j].value = values[idx]
                idx += 1
