"""gui.py - Part 3: Tkinter GUI and gameplay.

Uses ImageProcessor (image_processor.py) and Puzzle (puzzle.py).
Run with:  python main.py
"""

import base64
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2

from image_processor import ImageProcessor
from puzzle import Puzzle


def to_photo(cv_image):
    """Convert an OpenCV image into a Tkinter PhotoImage."""
    ok, buffer = cv2.imencode(".png", cv_image)
    return tk.PhotoImage(data=base64.b64encode(buffer.tobytes()))


class PuzzleApp:
    """The main window. It shows the puzzle and handles all user input."""

    def __init__(self, root):
        self.root = root
        self.root.title("HIT137 Image Puzzle")

        self.processor = ImageProcessor(max_width=480, max_height=480)
        self.puzzle = None
        self.original = None        # prepared original image (OpenCV)
        self.tile_size = 0
        self.selected = None        # position of the selected tile
        self.hint_cells = None      # (position on puzzle, home position)
        self.locked = True          # no input until an image is loaded
        self.photo_left = None
        self.photo_right = None

        self.build_widgets()

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------
    def build_widgets(self):
        top = tk.Frame(self.root, pady=5)
        top.pack()

        tk.Label(top, text="Grid size:").pack(side="left")
        self.grid_var = tk.IntVar(value=3)          # default 3 x 3
        for n in (3, 4, 5):
            tk.Radiobutton(top, text=f"{n} x {n}", variable=self.grid_var,
                           value=n).pack(side="left")

        tk.Button(top, text="Load Image",
                  command=self.load_image).pack(side="left", padx=8)
        self.hint_btn = tk.Button(top, text="Hint", command=self.use_hint,
                                  state="disabled")
        self.hint_btn.pack(side="left", padx=2)
        self.solve_btn = tk.Button(top, text="Solve", command=self.solve,
                                   state="disabled")
        self.solve_btn.pack(side="left", padx=2)

        # Status section: moves, tiles incorrect, hints
        info = tk.Frame(self.root)
        info.pack()
        self.moves_label = tk.Label(info, text="Moves: 0", font=("Arial", 12))
        self.moves_label.pack(side="left", padx=15)
        self.wrong_label = tk.Label(info, text="Tiles incorrect: 0",
                                    font=("Arial", 12))
        self.wrong_label.pack(side="left", padx=15)
        self.hint_label = tk.Label(info, text="Hints left: 3",
                                   font=("Arial", 12))
        self.hint_label.pack(side="left", padx=15)

        # Original (left) and puzzle (right) side by side
        boards = tk.Frame(self.root, padx=10, pady=10)
        boards.pack()
        left = tk.Frame(boards)
        left.pack(side="left", padx=10)
        right = tk.Frame(boards)
        right.pack(side="left", padx=10)
        tk.Label(left, text="Original").pack()
        tk.Label(right, text="Puzzle (click here)").pack()

        self.left_canvas = tk.Canvas(left, width=480, height=480, bg="gray90")
        self.left_canvas.pack()
        self.right_canvas = tk.Canvas(right, width=480, height=480, bg="gray90")
        self.right_canvas.pack()

        tk.Label(self.root, pady=3,
                 text="Left click: select / swap    Right click: rotate 90\u00b0"
                      "    Shift + left click: flip").pack()

        # Mouse bindings (Button-2 is the right button on a Mac)
        self.right_canvas.bind("<Button-1>", self.left_click)
        self.right_canvas.bind("<Shift-Button-1>", self.shift_click)
        self.right_canvas.bind("<Button-3>", self.right_click)
        self.right_canvas.bind("<Button-2>", self.right_click)

    # ------------------------------------------------------------
    # Loading an image
    # ------------------------------------------------------------
    def load_image(self):
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if not path:                       # dialog was cancelled
            return

        grid = self.grid_var.get()
        try:
            image = self.processor.load_image(path)
            prepared = self.processor.prepare_image(image, grid)
            tiles = self.processor.create_tiles(prepared, grid)
            puzzle = Puzzle(tiles, grid)
            puzzle.scramble()
        except Exception as error:
            messagebox.showerror("Error", str(error))
            return

        # Everything worked, so fully reset the round.
        self.puzzle = puzzle
        self.original = prepared
        self.tile_size = prepared.shape[0] // grid
        self.selected = None
        self.hint_cells = None
        self.locked = False
        self.solve_btn.config(state="normal")

        size = self.tile_size * grid
        self.left_canvas.config(width=size, height=size)
        self.right_canvas.config(width=size, height=size)
        self.redraw()

        if self.puzzle.is_solved():        # extremely rare
            self.finish()
            messagebox.showinfo("Puzzle", "This puzzle came out already "
                                          "solved. Please load it again.")

    # ------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------
    def redraw(self):
        """Draw both images and every overlay."""
        p = self.puzzle
        g = p.grid_size
        ts = self.tile_size

        # Left: original image
        self.photo_left = to_photo(self.original)
        self.left_canvas.delete("all")
        self.left_canvas.create_image(0, 0, image=self.photo_left, anchor="nw")

        # Right: puzzle image (tiles reassembled into one picture)
        images = [tile.image for tile in p.tiles]
        self.photo_right = to_photo(self.processor.tiles_to_image(images, g))
        self.right_canvas.delete("all")
        self.right_canvas.create_image(0, 0, image=self.photo_right, anchor="nw")

        # Faint grid
        for i in range(1, g):
            self.right_canvas.create_line(i * ts, 0, i * ts, g * ts,
                                          fill="white", dash=(2, 4))
            self.right_canvas.create_line(0, i * ts, g * ts, i * ts,
                                          fill="white", dash=(2, 4))

        # Green tick in the corner of each correct tile
        for pos in range(g * g):
            if p.tiles[pos].is_correct(pos):
                r, c = divmod(pos, g)
                x, y = (c + 1) * ts - 22, r * ts + 5
                self.right_canvas.create_line(x, y + 9, x + 6, y + 16,
                                              fill="green", width=4)
                self.right_canvas.create_line(x + 6, y + 16, x + 17, y,
                                              fill="green", width=4)

        # Highlight the selected tile with a coloured border
        if self.selected is not None:
            r, c = divmod(self.selected, g)
            self.right_canvas.create_rectangle(
                c * ts + 2, r * ts + 2, (c + 1) * ts - 2, (r + 1) * ts - 2,
                outline="red", width=4)

        # Blue hint circles on both images
        if self.hint_cells is not None:
            self.draw_circle(self.right_canvas, self.hint_cells[0])
            self.draw_circle(self.left_canvas, self.hint_cells[1])

        self.update_status()

    def draw_circle(self, canvas, pos):
        g = self.puzzle.grid_size
        ts = self.tile_size
        r, c = divmod(pos, g)
        cx, cy = c * ts + ts // 2, r * ts + ts // 2
        rad = ts // 3
        canvas.create_oval(cx - rad, cy - rad, cx + rad, cy + rad,
                           outline="blue", width=4)

    def update_status(self):
        p = self.puzzle
        self.moves_label.config(text=f"Moves: {p.moves}")
        self.wrong_label.config(
            text=f"Tiles incorrect: {p.get_incorrect_count()}")
        self.hint_label.config(text=f"Hints left: {p.hints_left()}")
        if self.locked or p.hints_left() <= 0:
            self.hint_btn.config(state="disabled")
        else:
            self.hint_btn.config(state="normal")

    # ------------------------------------------------------------
    # Mouse input
    # ------------------------------------------------------------
    def tile_at(self, event):
        """Tile position under the mouse, or None if outside the image."""
        if self.puzzle is None or self.locked:
            return None
        g = self.puzzle.grid_size
        if event.x < 0 or event.y < 0:
            return None
        col, row = event.x // self.tile_size, event.y // self.tile_size
        if col >= g or row >= g:
            return None
        return row * g + col

    def left_click(self, event):
        pos = self.tile_at(event)
        if pos is None:
            return
        if self.selected is None:              # first tile: select it
            self.selected = pos
            self.redraw()
        elif self.selected == pos:             # same tile again: deselect
            self.selected = None
            self.redraw()
        else:                                  # second tile: swap
            self.puzzle.swap_tiles(self.selected, pos)
            self.selected = None
            self.after_move()

    def right_click(self, event):
        pos = self.tile_at(event)
        if pos is None:
            return
        self.puzzle.rotate_tile(pos, 90)
        self.selected = None
        self.after_move()

    def shift_click(self, event):
        pos = self.tile_at(event)
        if pos is None:
            return
        self.puzzle.flip_tile(pos, "horizontal")
        self.selected = None
        self.after_move()

    def after_move(self):
        """Called after every swap, rotate or flip."""
        self.hint_cells = None                 # blue circles disappear
        self.redraw()
        if self.puzzle.is_solved():
            self.finish()
            messagebox.showinfo(
                "Well done!",
                f"Puzzle complete in {self.puzzle.moves} moves!")

    def finish(self):
        """Lock the puzzle so no more input is accepted."""
        self.locked = True
        self.selected = None
        self.hint_btn.config(state="disabled")

    # ------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------
    def use_hint(self):
        if self.puzzle is None or self.locked:
            return
        hint = self.puzzle.get_hint()
        if hint is None:
            return
        self.hint_cells = hint
        self.redraw()

    def solve(self):
        if self.puzzle is None or self.locked:
            return
        self.puzzle.solve()                    # undo all transformations
        self.hint_cells = None
        self.finish()
        self.redraw()
        messagebox.showinfo("Solved", "The puzzle has been solved.")
