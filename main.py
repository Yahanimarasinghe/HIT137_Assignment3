"""main.py - starts the HIT137 Image Puzzle application."""

import tkinter as tk

from gui import PuzzleApp


if __name__ == "__main__":
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()
