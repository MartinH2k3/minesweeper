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

    def auto_flag_simple(self):
        flagged: int = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.revealed[i][j]:
                    flagged_count = 0
                    hidden_neighbors = []
                    for p in Point(i, j).neighbors(True):
                        if p.within(self.board):
                            if p in self.flags: flagged_count += 1
                            elif not self.revealed[p.x][p.y]: hidden_neighbors.append(p)
                    if len(hidden_neighbors) == self.board[i][j] - flagged_count:
                        for p in hidden_neighbors:
                            self.flag(p)
                            flagged += 1
        return flagged

    def auto_reveal_simple(self):
        revealed = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.revealed[i][j]:
                    flagged_count = 0
                    hidden_neighbors = []
                    for p in Point(i, j).neighbors(True):
                        if p.within(self.board):
                            if p in self.flags: flagged_count += 1
                            elif not self.revealed[p.x][p.y]: hidden_neighbors.append(p)
                    if self.board[i][j] == flagged_count:
                        for p in hidden_neighbors:
                            self.reveal(p)
                            revealed += 1
        return revealed

    def auto_solve_simple(self):
        flagged = self.auto_flag_simple()
        revealed = self.auto_reveal_simple()
        while flagged + revealed:
            flagged = self.auto_flag_simple()
            revealed = self.auto_reveal_simple()
        return flagged + revealed

    def auto_solve_advanced(self):
        """
            Identify islands bordering unrevealed fields and do partial backtracking
            to find forced flags or reveals.
            Returns number of cells changed (flagged or revealed).
        """
        frontier = self._get_frontier()
        islands = self._get_islands(frontier)
        total_changed = 0
        for island in islands:
            constraints = self._get_constraints_for_island(island)
            changed = self._process_island_with_backtracking(island, constraints)
            total_changed += changed

        return total_changed

    def _get_frontier(self):
        frontier = []
        for i in range(self.size):
            for j in range(self.size):
                if not self.revealed[i][j] and Point(i, j) not in self.flags:
                    # Check if it's adjacent to any revealed cell
                    for p in Point(i, j).neighbors(True):
                        if p.within(self.board) and self.revealed[p.x][p.y]:
                            frontier.append(Point(i, j))
                            break
        return frontier

    def _get_islands(self, frontier):
        frontier_set = set(frontier)  # for quick 'in' checks
        visited = set()
        islands = []

        def dfs(start):
            stack = [start]
            island = set()
            while stack:
                cell = stack.pop()
                if cell in visited:
                    continue
                visited.add(cell)
                island.add(cell)
                # check neighbors that are in frontier
                for nb in cell.neighbors(True):
                    if nb in frontier_set and nb not in visited:
                        stack.append(nb)
            return island

        for cell in frontier:
            if cell not in visited:
                island = dfs(cell)
                islands.append(island)

        return islands

    def _get_constraints_for_island(self, island):
        """
        Return a list of constraints.
        Each constraint is (hidden_cells_list, required_mines).
        """
        island_constraints = []
        used_constraints = set()

        for cell in island:
            for nb in cell.neighbors(True):
                if nb.within(self.board) and self.revealed[nb.x][nb.y]:
                    if nb not in used_constraints:
                        used_constraints.add(nb)
                        # Now build the constraint
                        hidden_list = []
                        flagged_count = 0
                        required_mines = self.board[nb.x][nb.y]  # the number on that revealed cell
                        for n2 in nb.neighbors(True):
                            if n2.within(self.board):
                                if n2 in self.flags:
                                    flagged_count += 1
                                elif not self.revealed[n2.x][n2.y]:
                                    hidden_list.append(n2)
                        required_mines -= flagged_count
                        island_constraints.append((hidden_list, required_mines))

        return island_constraints

    def _process_island_with_backtracking(self, island, constraints):
        """
        1) Build a list of island cells (variables).
        2) Enumerate all solutions that satisfy 'constraints'.
        3) For each cell, check if it's always a mine or always safe.
        4) Flag or reveal accordingly.
        Return how many cells changed.
        """
        island_cells = list(island)
        n = len(island_cells)
        valid_solutions = []

        # We'll store partial assignments in a list of 0/1, same order as island_cells
        assignment = [0] * n

        def backtrack(index):
            if index == n:
                # Check constraints
                if self._check_constraints(assignment, island_cells, constraints):
                    valid_solutions.append(assignment[:])  # copy
                return

            # Option 1: cell is not a mine
            assignment[index] = 0
            # quick prune check - optional advanced logic
            if self._partial_ok(assignment, index, island_cells, constraints):
                backtrack(index + 1)

            # Option 2: cell is a mine
            assignment[index] = 1
            # prune check again
            if self._partial_ok(assignment, index, island_cells, constraints):
                backtrack(index + 1)

        backtrack(0)

        if not valid_solutions:
            # No valid solutions found => no forced moves
            return 0

        # For each cell, check if it's always 1 or always 0
        changed = 0
        for i, cell in enumerate(island_cells):
            all_1 = all(sol[i] == 1 for sol in valid_solutions)
            all_0 = all(sol[i] == 0 for sol in valid_solutions)
            if all_1 and cell not in self.flags:
                self.flag(cell)
                changed += 1
            elif all_0 and not self.revealed[cell.x][cell.y] and cell not in self.flags:
                self.reveal(cell)
                changed += 1
        return changed

    def _check_constraints(self, assignment, island_cells, constraints):
        assign_map = {}
        for i, c in enumerate(island_cells):
            assign_map[c] = assignment[i]
        for f in self.flags:
            assign_map[f] = 1

        for (hidden_list, needed) in constraints:
            count = 0
            for h in hidden_list:
                if h in assign_map:
                    count += assign_map[h]  # either 0 or 1
                # if h not in assign_map => assume 0 or interpret differently
            if count != needed:
                return False
        return True

    def _partial_ok(self, assignment, index, island_cells, constraints):
        # For a quick check, see if any constraint is exceeded so far
        assign_map = {}
        for i, c in enumerate(island_cells):
            if i <= index:
                assign_map[c] = assignment[i]
        for f in self.flags:
            assign_map[f] = 1

        for (hidden_list, needed) in constraints:
            assigned_sum = 0
            unknown = 0
            for h in hidden_list:
                if h in assign_map:
                    assigned_sum += assign_map[h]
                else:
                    unknown += 1
            if assigned_sum > needed:
                return False
            if assigned_sum + unknown < needed:
                return False
        return True

    def auto_solve(self):
        while sum(sum(i) for i in self.revealed) + self.mine_count < self.size**2:
            changed_simple = self.auto_solve_simple()
            changed_advanced = self.auto_solve_advanced()
            if changed_simple + changed_advanced == 0:
                # No more progress
                break


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
        self.hint_button = tk.Button(
            self.root, text="Hint",
            font=("Helvetica", 12),
            command=lambda: (self.board.auto_solve(), self.update_ui())
        )
        self.hint_button.grid(row=self.size + 1, column=1, columnspan=self.size)
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
        self.board.flags.clear()
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