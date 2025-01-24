import utils
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    gui = utils.minesweeper.MinesweeperGUI(root)

    root.mainloop()