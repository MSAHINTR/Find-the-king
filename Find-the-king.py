import tkinter as tk
from tkinter import messagebox
import random

BOARD_SIZE = 5
# Board distribution: seven 1s, five 2s, five 3s, four 4s, three 5s and one king
INITIAL_VALUES = [1] * 7 + [2] * 5 + [3] * 5 + [4] * 4 + [5] * 3 + ["K"]

class Cell:
    def __init__(self, value):
        self.value = value  # "K" or 1-5
        self.opened = False
        self.revealed = False

class GameBoard:
    def __init__(self):
        self.board = [[Cell(0) for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.setup_board()

    def setup_board(self):
        values = INITIAL_VALUES.copy()
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
        self.cards = {1: 5, 2: 3, 3: 2, 4: 1, 5: 1, "K": 1}
        # automatic play order: five 1s, three 2s, two 3s, one 4, one 5, one king card
        self.card_sequence = [1] * 5 + [2] * 3 + [3] * 2 + [4] + [5] + ["K"]
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
        self.five_hints = {}
        self.no_five_cells = set()
        self.completed_rows = set()
        self.completed_cols = set()
        self.completed_diagonals = set()

        self.create_widgets()
        self.update_status()

    def create_widgets(self):
        self.status_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.status_label.grid(row=0, column=0, columnspan=BOARD_SIZE)

        self.card_frame = tk.Frame(self.root)
        self.card_frame.grid(row=1, column=0, columnspan=BOARD_SIZE)

        self.card_buttons = {}
        for idx, num in enumerate([1, 2, 3, 4, 5, "K"]):
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
                b = tk.Button(
                    self.grid_frame,
                    text="?",
                    width=5,
                    height=2,
                    command=lambda x=i, y=j: self.open_cell(x, y),
                    font=("Arial", 20)
                )
                b.grid(row=i, column=j, padx=2, pady=2)
                row.append(b)
            self.cell_buttons.append(row)

        self.history_label = tk.Label(self.root, text="Seçim Geçmişi:", anchor="w", justify="left")

        self.history_label.grid(row=3, column=0, columnspan=BOARD_SIZE, sticky="w")

        # side panel for discovered cards and predictions
        self.side_frame = tk.Frame(self.root)
        self.side_frame.grid(row=0, column=BOARD_SIZE, rowspan=5, padx=5, sticky="n")

        tk.Label(self.side_frame, text="Bulunanlar").pack()
        self.found_frame = tk.Frame(self.side_frame)
        self.found_frame.pack()
        self.found_labels = []
        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                lbl = tk.Label(
                    self.found_frame,
                    text="?",
                    width=4,
                    height=2,
                    relief=tk.SUNKEN,
                    font=("Arial", 14)
                )
                lbl.grid(row=i, column=j, padx=1, pady=1)
                row.append(lbl)
            self.found_labels.append(row)

        tk.Label(self.side_frame, text="Tahminler").pack(pady=(10, 0))
        self.pred_frame = tk.Frame(self.side_frame)
        self.pred_frame.pack()
        self.pred_labels = []
        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                lbl = tk.Label(
                    self.pred_frame,
                    text="?",
                    width=4,
                    height=2,
                    relief=tk.SUNKEN,
                    font=("Arial", 12)
                )
                lbl.grid(row=i, column=j, padx=1, pady=1)
                row.append(lbl)
            self.pred_labels.append(row)

        self.update_predictions()


    def open_cell(self, x, y):
        if self.game_over:
            return
        cell = self.board.board[x][y]
        if cell.opened or cell.revealed:
            return

        card = self.player.draw_next_card()
        if card is None:
            messagebox.showinfo("Kart Yok", "Kullanacak kart kalmadı!")
            return
        # A large card closes the cell again; equal or smaller cards stay open
        if card in self.card_buttons:
            self.card_buttons[card].config(text=f"{card} ({self.player.cards[card]})")
        cell.opened = True
        cell.revealed = True

        neighbors = self.board.get_neighbors(x, y)
        has_five_neighbor = any(ncell.value == 5 for _, _, ncell in neighbors)
        self.five_hints[(x, y)] = has_five_neighbor
        if not has_five_neighbor:
            for nx, ny, _ in neighbors:
                if not self.board.board[nx][ny].revealed:
                    self.no_five_cells.add((nx, ny))
        else:
            for (hx, hy), hint in self.five_hints.items():
                if not hint:
                    nf = {(nx, ny) for nx, ny, _ in self.board.get_neighbors(hx, hy)}
                    cur = {(nx, ny) for nx, ny, _ in neighbors}
                    for cx, cy in nf & cur:
                        if not self.board.board[cx][cy].revealed:
                            self.no_five_cells.add((cx, cy))

        result = ""
        color = "white"
        reuse = False
        close_delay = None
        show_val = cell.value

        if cell.value == "K":
            if card == "K":
                if self.player.card_index == len(self.player.card_sequence) and all(v == 0 for v in self.player.cards.values()):
                    self.player.score += 300
                    result = "Son hamlede kralı buldun! +300 puan"
                else:
                    self.player.score += 150
                    result = "Kral kartıyla kralı buldun! +150 puan"
            else:
                result = "Kralı buldun, puan yok"
            color = "white"
            show_val = "K"
            close_delay = 1000
        elif isinstance(cell.value, int):
            if card < 5 and self.player.cards.get(5, 0) > 0 and has_five_neighbor:
                result = "Kart yandı"
                color = "red"
            elif card == 5:
                if has_five_neighbor:
                    result = "5 kartı yandı"
                    color = "red"
                else:
                    self.player.score += 50
                    result = "5 kartı başarılı! +50 puan"
                    color = "lightgreen"
                # 5 kartı her durumda harcanır
            elif card < cell.value:
                result = "Kart küçük, puan yok"
                color = "orange"
            elif card == cell.value:
                # equal value keeps the cell open
                self.player.score += 10
                result = "+10 puan"
                color = "lightblue"
            else:  # card > cell.value
                # larger card closes again and allows reuse
                self.player.score += 10
                result = "+10 puan"
                color = "lightgreen"
                reuse = True
                close_delay = 1000
        
        self.cell_buttons[x][y].config(text=show_val, bg=color, state=tk.DISABLED)
        self.found_labels[x][y].config(text=cell.value)

        # Tarihçeye ekle
        self.player.history.append(((x, y), card, cell.value, result))
        self.update_history()

        # İpucu efektleri (kral için efekt uygulanmaz)
        if cell.value != "K":
            self.show_hints(x, y, card)

        self.update_predictions()
        self.check_bonus()

        if reuse:
            self.player.cards[card] += 1
            self.player.card_index -= 1
            if card in self.card_buttons:
                self.card_buttons[card].config(text=f"{card} ({self.player.cards[card]})")

        if close_delay is not None:
            self.root.after(close_delay, lambda: self.close_cell(x, y))

        self.update_status()

        if self.game_over or all(v == 0 for v in self.player.cards.values()):
            self.end_game()

    def close_cell(self, x, y):
        cell = self.board.board[x][y]
        cell.opened = False
        self.cell_buttons[x][y].config(text="?", bg="SystemButtonFace", state=tk.NORMAL)
        self.update_predictions()
        self.check_bonus()

    def show_hints(self, x, y, card):
        neighbors = self.board.get_neighbors(x, y)
        hint_cells = []
        any_five = any(ncell.value == 5 for _, _, ncell in neighbors)
        if any_five:
            hint_cells = list({(nx, ny) for nx, ny, _ in neighbors} | set(hint_cells))
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

    def update_predictions(self):
        """Refresh the lower panel showing guessed values.

        Cells noted in ``no_five_cells`` never display the value ``5`` unless no
        other option exists. Predictions are otherwise random and independent of
        the remaining deck to keep the logic simple.
        """

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell = self.board.board[i][j]
                if cell.revealed:
                    val = cell.value
                else:
                    if (i, j) in self.no_five_cells:
                        choices = [1, 2, 3, 4]
                    else:
                        choices = [1, 2, 3, 4, 5]
                    val = random.choice(choices)
                self.pred_labels[i][j].config(text=val)

    def check_bonus(self):
        # check rows
        for i in range(BOARD_SIZE):
            if i not in self.completed_rows and all(self.board.board[i][j].opened for j in range(BOARD_SIZE)):
                self.completed_rows.add(i)
                self.player.score += 20
        # check columns
        for j in range(BOARD_SIZE):
            if j not in self.completed_cols and all(self.board.board[i][j].opened for i in range(BOARD_SIZE)):
                self.completed_cols.add(j)
                self.player.score += 20
        # check diagonals
        if "main" not in self.completed_diagonals and all(self.board.board[i][i].opened for i in range(BOARD_SIZE)):
            self.completed_diagonals.add("main")
            self.player.score += 100
        if "anti" not in self.completed_diagonals and all(self.board.board[i][BOARD_SIZE-1-i].opened for i in range(BOARD_SIZE)):
            self.completed_diagonals.add("anti")
            self.player.score += 100

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
