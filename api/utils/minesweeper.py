from api.utils.point import Point
import random
import tkinter as tk

class Board:
    def __init__(self, size: int, mine_count: int):
        self.size = size
        self.mine_count = mine_count
        self.remaining_mines = mine_count
        self.board: list[list[int]] = [[0] * size for _ in range(size)]
        self.revealed: list[list[bool]] = [[False] * size for _ in range(size)]
        self.flags: set[Point] = set()
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

    def reveal(self, point: Point):
        if not point.within(self.board) or self.revealed[point.x][point.y] or point in self.flags:
            return False
        self.revealed[point.x][point.y] = True
        if self.board[point.x][point.y] == 0:
            for p in point.neighbors(True):
                self.reveal(p)

        return self.board[point.x][point.y] == -1

    def flag(self, point: Point):
        if not point.within(self.board) or self.revealed[point.x][point.y]:
            return
        if point in self.flags:
            self.flags.remove(point)
            self.remaining_mines += 1
            return
        self.flags.add(point)
        self.remaining_mines -= 1

    def won(self) -> bool:
        return sum(sum(i) for i in self.revealed) + self.mine_count == self.size**2

    def __str__(self):
        output = ""
        for i in range(self.size):
            for j in range(self.size):
                if self.revealed[i][j]:
                    if Point(i, j) in self.flags:
                        output += "F"
                    else:
                        output += str(self.board[i][j])
                else:
                    output += "_"
            output += "\n"
        return output


class MinesweeperGUI:
    def __init__(self, root: tk.Tk, size: int = 25, mine_count: int = 80):
        self.root = root
        self.root.title("Minesweeper")

        self.size = size
        self.mine_count = mine_count

        # Create the game board model
        self.board = Board(size, mine_count)

        # Create a 2D array of buttons
        self.buttons: list[list[tk.Button]] = []

        for x in range(size):
            row_of_buttons = []
            for y in range(size):
                btn = tk.Button(
                    self.root,
                    width=3,
                    height=1,
                    font=("Helvetica", 12, "bold"),
                    command=lambda r=x, c=y: self.on_left_click(r, c)
                )
                # Bind right-click for flagging
                btn.bind("<Button-3>", lambda e, r=x, c=y: self.on_right_click(r, c))

                btn.grid(row=x, column=y, padx=0, pady=0)
                row_of_buttons.append(btn)
            self.buttons.append(row_of_buttons)

        self.base_status_label_config = {"font": ("Helvetica", 14, "normal"), "fg": "black"}
        self.status_label = tk.Label(self.root, text=f"Mines left: {self.board.remaining_mines}", **self.base_status_label_config)
        self.status_label.grid(row=size, column=0, columnspan=size)
        self.play_again_button = None

    def on_left_click(self, row: int, col: int):
        """Reveal the cell on left-click."""
        hit_mine = self.board.reveal(Point(row, col))
        self.update_ui()

        if hit_mine:
            self.game_over(False)
        if self.board.won():
            self.game_over(True)

    def on_right_click(self, row: int, col: int):
        """Flag or unflag on right-click."""
        self.board.flag(Point(row, col))
        self.update_ui()

    def update_ui(self):
        """Update all buttons based on current board state."""
        color_map = {
            0: "gray",
            1: "blue",
            2: "green",
            3: "red",
            4: "navy",
            5: "maroon",
            6: "turquoise",
            7: "black",
            8: "gray"
        }

        for x in range(self.board.size):
            for y in range(self.board.size):
                btn = self.buttons[x][y]
                p = Point(x, y)

                if p in self.board.flags:
                    btn.config(text="F", bg="yellow", fg="black")
                elif self.board.revealed[x][y]:
                    val = self.board.board[x][y]
                    if val == -1:
                        btn.config(text="*", bg="red")
                    else:
                        btn.config(text=str(val) if val > 0 else " ", bg="lightgray", fg=color_map[val])
                else:
                    btn.config(text="", bg="SystemButtonFace")

        self.status_label.config(text=f"Mines left: {self.board.remaining_mines}")

        # If a "Play Again" button was there from a previous game, remove it
        if self.play_again_button:
            self.play_again_button.destroy()
            self.play_again_button = None

    def game_over(self, won: bool):
        """Handle end of game."""
        # Reveal all cells
        for x in range(self.board.size):
            for y in range(self.board.size):
                self.board.revealed[x][y] = True
        self.update_ui()
        self.status_label.config(
            text="You win!" if won else "Boom! You hit a mine.",
            fg="green" if won else "red",
            font=("Helvetica", 20, "bold"))
        # Disable all buttons
        for x in range(self.board.size):
            for y in range(self.board.size):
                self.buttons[x][y].config(state="disabled")
        self.play_again_button = tk.Button(
            self.root, text="Play Again",
            font=("Helvetica", 12),
            command=self.restart_game
        )
        self.play_again_button.grid(row=self.size + 1, column=0, columnspan=self.size)

    def restart_game(self):
        self.board = Board(self.size, self.mine_count)
        self.update_ui()
        self.status_label.configure(**self.base_status_label_config)
        for x in range(self.board.size):
            for y in range(self.board.size):
                self.buttons[x][y].config(state="normal")