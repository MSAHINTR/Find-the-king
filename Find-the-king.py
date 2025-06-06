import tkinter as tk
from tkinter import messagebox
import random

BOARD_SIZE = 5

class Cell:
    def __init__(self, value):
        self.value = value  # "K", "💀", or 1-5
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
        self.cards = {1: 5, 2: 3, 3: 2, 4: 1, 5: 1}
        # automatic play order: five 1s, three 2s, two 3s, one 4, one 5
        self.card_sequence = [1] * 5 + [2] * 3 + [3] * 2 + [4] + [5]
        self.card_index = 0
        self.score = 0
        self.history = []

    def draw_next_card(self):
        while self.card_index < len(self.card_sequence):
            card = self.card_sequence[self.card_index]
            self.card_index += 1
            if self.cards.get(card, 0) > 0:
                self.cards[card] -= 1
                return card
        return None

class KraliBulGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kralı Bul")
        self.game_over = False

        self.board = GameBoard()
        self.player = Player()

        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        self.status_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.status_label.grid(row=0, column=0, columnspan=BOARD_SIZE)

        self.card_frame = tk.Frame(self.root)
        self.card_frame.grid(row=1, column=0, columnspan=BOARD_SIZE)

        self.card_buttons = {}
        for idx, num in enumerate([1, 2, 3, 4, 5]):
            btn = tk.Button(
                self.card_frame,
                text=f"{num} ({self.player.cards[num]})",
                width=8,
                state=tk.DISABLED,
            )
            btn.grid(row=0, column=idx, padx=2, pady=3)
            self.card_buttons[num] = btn

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=2, column=0, columnspan=BOARD_SIZE)

        self.cell_buttons = []
        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                b = tk.Button(self.grid_frame, text="?", width=4, height=2,
                              command=lambda x=i, y=j: self.open_cell(x, y), font=("Arial", 18))
                b.grid(row=i, column=j, padx=2, pady=2)
                row.append(b)
            self.cell_buttons.append(row)

        self.history_label = tk.Label(self.root, text="Seçim Geçmişi:", anchor="w", justify="left")
        self.history_label.grid(row=3, column=0, columnspan=BOARD_SIZE, sticky="w")


    def open_cell(self, x, y):
        if self.game_over:
            return
        cell = self.board.board[x][y]
        if cell.opened:
            return

        card = self.player.draw_next_card()
        if card is None:
            messagebox.showinfo("Kart Yok", "Kullanacak kart kalmadı!")
            return
        self.card_buttons[card].config(text=f"{card} ({self.player.cards[card]})")
        cell.opened = True

        result = ""
        color = "white"
        if cell.value == "K":
            if card == 5:
                self.player.score += 10
                result = "Kral'ı doğru kartla buldun! +10 puan!"
                color = "gold"
            else:
                self.player.score -= 5
                result = "Kral'ı yanlış kartla açtın! -5 puan!"
                color = "red"
            self.game_over = True
        elif cell.value == "💀":
            self.player.score -= 5
            result = "Kuru Kafa! -5 puan"
            color = "black"
        elif isinstance(cell.value, int) and cell.value != 0:
            if card > cell.value:
                self.player.score += 1
                result = "+1 puan"
                color = "lightgreen"
            elif card < cell.value:
                self.player.score -= 1
                result = "-1 puan"
                color = "orange"
            else:
                result = "Beraberlik, puan yok"
                color = "lightgray"
        else:
            result = "Nötr hücre"
            color = "white"

        # Buton görünümünü güncelle
        show_val = cell.value if cell.value != 0 else ""
        self.cell_buttons[x][y].config(text=show_val, bg=color, state=tk.DISABLED)

        # Tarihçeye ekle
        self.player.history.append(((x, y), card, cell.value, result))
        self.update_history()

        # İpucu efektleri
        self.show_hints(x, y, card)
        self.update_status()

        if self.game_over or all(v == 0 for v in self.player.cards.values()):
            self.end_game()

    def show_hints(self, x, y, card):
        neighbors = self.board.get_neighbors(x, y)
        hint_cells = []
        for nx, ny, ncell in neighbors:
            if ncell.value == "K" or ncell.value == 5:
                hint_cells.append((nx, ny))
        if hint_cells:
            for nx, ny in hint_cells:
                self.cell_buttons[nx][ny].config(bg="cyan")
            self.root.after(800, lambda: [self.cell_buttons[nx][ny].config(bg="SystemButtonFace")
                                          for nx, ny in hint_cells])
        # 5 numaralı kart ile ek ipucu
        if card == 5:
            neighbor_info = []
            for nx, ny, ncell in neighbors:
                if not ncell.opened:
                    neighbor_info.append(f"({nx+1},{ny+1}): {ncell.value}")
            if neighbor_info:
                messagebox.showinfo("Ekstra İpucu", "Komşu kartlar: " + ", ".join(neighbor_info))

    def update_status(self):
        self.status_label.config(
            text=f"Skor: {self.player.score} | Kalan kartlar: {self.player.cards} "
        )

    def update_history(self):
        lines = ["Seçim Geçmişi:"]
        for (x, y), card, val, res in self.player.history[-5:]:
            lines.append(f"{x+1},{y+1} → Kart:{card} | Hücre:{val} | {res}")
        self.history_label.config(text="\n".join(lines))

    def end_game(self):
        self.game_over = True
        msg = f"Oyun Bitti!\nToplam Skor: {self.player.score}\n"
        if any(cell.value == "K" and cell.opened for row in self.board.board for cell in row):
            msg += "Kral bulundu!"
        else:
            msg += "Kral bulunamadı!"
        messagebox.showinfo("Oyun Sonu", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = KraliBulGUI(root)
    root.mainloop()
