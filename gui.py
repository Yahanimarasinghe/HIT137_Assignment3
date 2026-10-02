import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import ImageTk, ImageDraw

from image_processor import ImageProcessor
from puzzle import Puzzle


class PuzzleGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("HIT137 IMAGE PUZZLE")

        # Window size
        self.root.geometry("980x650")
        self.root.resizable(False, False)

        # =====================================================
        # IMAGE PROCESSOR
        # =====================================================

        self.processor = ImageProcessor(
            max_width=400,
            max_height=400
        )

        # =====================================================
        # PUZZLE VARIABLES
        # =====================================================

        self.puzzle = None
        self.grid_size = 3

        self.selected_tile = None

        self.hint_tile = None
        self.hint_home = None

        self.hinted_positions = []

        self.original_image = None
        self.original_photo = None

        self.tile_photo_images = []

        # =====================================================
        # CONTROL FRAME
        # =====================================================

        control_frame = tk.Frame(
            root,
            pady=5
        )

        control_frame.pack()

        # Choose Image
        tk.Button(
            control_frame,
            text="Choose Image",
            width=13,
            command=self.choose_image
        ).grid(
            row=0,
            column=0,
            padx=3
        )

        # Grid
        tk.Label(
            control_frame,
            text="Grid:"
        ).grid(
            row=0,
            column=1,
            padx=3
        )

        self.grid_var = tk.StringVar(
            value="3"
        )

        tk.OptionMenu(
            control_frame,
            self.grid_var,
            "3",
            "4",
            "5",
            command=self.change_grid
        ).grid(
            row=0,
            column=2,
            padx=3
        )

        # Scramble
        tk.Button(
            control_frame,
            text="Scramble",
            width=10,
            command=self.scramble_puzzle
        ).grid(
            row=0,
            column=3,
            padx=3
        )

        # Hint
        self.hint_button = tk.Button(
            control_frame,
            text="Hint",
            width=10,
            command=self.give_hint
        )

        self.hint_button.grid(
            row=0,
            column=4,
            padx=3
        )

        # Solve
        tk.Button(
            control_frame,
            text="Solve",
            width=10,
            command=self.solve_puzzle
        ).grid(
            row=0,
            column=5,
            padx=3
        )

        # Exit
        tk.Button(
            control_frame,
            text="Exit",
            width=10,
            command=self.root.destroy
        ).grid(
            row=0,
            column=6,
            padx=3
        )

        # =====================================================
        # INFORMATION FRAME
        # =====================================================

        info_frame = tk.Frame(
            root,
            pady=2
        )

        info_frame.pack()

        self.moves_label = tk.Label(
            info_frame,
            text="Moves: 0",
            font=("Arial", 10)
        )

        self.moves_label.grid(
            row=0,
            column=0,
            padx=15
        )

        self.incorrect_label = tk.Label(
            info_frame,
            text="Incorrect tiles: 0",
            font=("Arial", 10)
        )

        self.incorrect_label.grid(
            row=0,
            column=1,
            padx=15
        )

        self.hints_label = tk.Label(
            info_frame,
            text="Hints: 0/3",
            font=("Arial", 10)
        )

        self.hints_label.grid(
            row=0,
            column=2,
            padx=15
        )

        # =====================================================
        # IMAGE AREA
        # =====================================================

        image_frame = tk.Frame(
            root,
            padx=5,
            pady=5
        )

        image_frame.pack()

        # =====================================================
        # ORIGINAL IMAGE
        # =====================================================

        original_frame = tk.Frame(
            image_frame
        )

        original_frame.grid(
            row=0,
            column=0,
            padx=5
        )

        tk.Label(
            original_frame,
            text="Original Image",
            font=("Arial", 12, "bold")
        ).pack(
            pady=2
        )

        self.original_label = tk.Label(
            original_frame,
            text="Choose an image",
            width=400,
            height=400,
            relief="solid",
            bd=1
        )

        self.original_label.pack()

        # =====================================================
        # SCRAMBLED PUZZLE
        # =====================================================

        puzzle_frame = tk.Frame(
            image_frame
        )

        puzzle_frame.grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Label(
            puzzle_frame,
            text="Scrambled Puzzle",
            font=("Arial", 12, "bold")
        ).pack(
            pady=2
        )

        self.puzzle_container = tk.Frame(
            puzzle_frame,
            width=400,
            height=400
        )

        self.puzzle_container.pack()

        # =====================================================
        # INSTRUCTIONS
        # =====================================================

        instructions = (
            "Left click = Select / Swap   |   "
            "Right click = Rotate 90°   |   "
            "Shift + Left click = Flip"
        )

        tk.Label(
            root,
            text=instructions,
            font=("Arial", 9),
            pady=3
        ).pack()

    # =========================================================
    # CHANGE GRID
    # =========================================================

    def change_grid(self, value):

        self.grid_size = int(value)

        if self.puzzle is not None:

            self.puzzle = None

            self.selected_tile = None

            self.hint_tile = None
            self.hint_home = None

            self.hinted_positions = []

            self.original_image = None

            self.original_photo = None

            self.tile_photo_images = []

            for widget in (
                self.puzzle_container.winfo_children()
            ):
                widget.destroy()

            self.original_label.config(
                image="",
                text="Choose an image",
                width=400,
                height=400
            )

            self.original_label.image = None

        # Reset displayed game information.
        self.moves_label.config(
            text="Moves: 0"
        )

        self.incorrect_label.config(
            text="Incorrect tiles: 0"
        )

        self.hints_label.config(
            text="Hints: 0/3"
        )

        self.hint_button.config(
            state="normal"
        )

    # =========================================================
    # CHOOSE IMAGE
    # =========================================================

    def choose_image(self):

        file_path = filedialog.askopenfilename(
            title="Choose Image",
            filetypes=[
                (
                    "Image Files",
                    "*.jpg *.jpeg *.png *.bmp"
                ),
                (
                    "JPG Files",
                    "*.jpg *.jpeg"
                ),
                (
                    "PNG Files",
                    "*.png"
                ),
                (
                    "BMP Files",
                    "*.bmp"
                )
            ]
        )

        if not file_path:
            return

        try:

            loaded_image = (
                self.processor.load_image(
                    file_path
                )
            )

            prepared_image = (
                self.processor.prepare_image(
                    loaded_image,
                    self.grid_size
                )
            )

            tiles = (
                self.processor.create_tiles(
                    prepared_image,
                    self.grid_size
                )
            )

            self.puzzle = Puzzle(
                tiles,
                self.grid_size
            )

            self.original_image = (
                prepared_image.copy()
            )

            self.selected_tile = None

            self.hint_tile = None
            self.hint_home = None

            self.hinted_positions = []

            self.display_original()

            self.puzzle.scramble()

            self.create_puzzle_buttons()

            self.update_information()

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

    # =========================================================
    # DISPLAY ORIGINAL IMAGE
    # =========================================================

    def display_original(self):

        if self.original_image is None:
            return

        pil_image = (
            self.processor.cv_to_pil(
                self.original_image
            )
        )

        width, height = pil_image.size

        scale = min(
            400 / width,
            400 / height
        )

        new_width = max(
            1,
            int(width * scale)
        )

        new_height = max(
            1,
            int(height * scale)
        )

        pil_image = pil_image.resize(
            (
                new_width,
                new_height
            )
        )

        # =====================================================
        # BLUE HINT ON ORIGINAL IMAGE
        # =====================================================

        if (
            self.hint_home is not None
            and self.puzzle is not None
        ):

            draw = ImageDraw.Draw(
                pil_image
            )

            grid = self.grid_size

            tile_width = (
                new_width / grid
            )

            tile_height = (
                new_height / grid
            )

            home = self.hint_home

            row = home // grid
            col = home % grid

            center_x = int(
                col * tile_width
                + tile_width / 2
            )

            center_y = int(
                row * tile_height
                + tile_height / 2
            )

            radius = int(
                min(
                    tile_width,
                    tile_height
                ) * 0.35
            )

            draw.ellipse(
                [
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius
                ],
                outline="blue",
                width=5
            )

        self.original_photo = (
            ImageTk.PhotoImage(
                pil_image
            )
        )

        self.original_label.config(
            image=self.original_photo,
            text="",
            width=new_width,
            height=new_height
        )

        self.original_label.image = (
            self.original_photo
        )

    # =========================================================
    # CREATE PUZZLE BUTTONS
    # =========================================================

    def create_puzzle_buttons(self):

        for widget in (
            self.puzzle_container.winfo_children()
        ):
            widget.destroy()

        self.tile_photo_images = []

        if self.puzzle is None:
            return

        tile_size = (
            400 // self.grid_size
        )

        for index, tile in enumerate(
            self.puzzle.tiles
        ):

            pil_image = (
                self.processor.cv_to_pil(
                    tile.image
                )
            )

            pil_image = pil_image.resize(
                (
                    tile_size,
                    tile_size
                )
            )

            draw = ImageDraw.Draw(
                pil_image
            )

            # Normal border
            draw.rectangle(
                [
                    0,
                    0,
                    tile_size - 1,
                    tile_size - 1
                ],
                outline="gray",
                width=2
            )

            # Check correct tile
            correct = (
                tile.is_correct(index)
            )

            # =================================================
            # GREEN TICK
            # =================================================

            if correct:

                draw.rectangle(
                    [
                        3,
                        3,
                        tile_size - 4,
                        tile_size - 4
                    ],
                    outline="green",
                    width=5
                )

                x1 = int(
                    tile_size * 0.18
                )

                y1 = int(
                    tile_size * 0.55
                )

                x2 = int(
                    tile_size * 0.42
                )

                y2 = int(
                    tile_size * 0.75
                )

                x3 = int(
                    tile_size * 0.82
                )

                y3 = int(
                    tile_size * 0.25
                )

                draw.line(
                    [
                        (x1, y1),
                        (x2, y2),
                        (x3, y3)
                    ],
                    fill="green",
                    width=max(
                        5,
                        tile_size // 9
                    )
                )

            # =================================================
            # SELECTED TILE
            # =================================================

            if self.selected_tile == index:

                draw.rectangle(
                    [
                        5,
                        5,
                        tile_size - 6,
                        tile_size - 6
                    ],
                    outline="orange",
                    width=4
                )

            # =================================================
            # BLUE HINT
            # =================================================

            if (
                self.hint_tile is not None
                and index == self.hint_tile
            ):

                center = (
                    tile_size // 2
                )

                radius = (
                    tile_size // 3
                )

                draw.ellipse(
                    [
                        center - radius,
                        center - radius,
                        center + radius,
                        center + radius
                    ],
                    outline="blue",
                    width=5
                )

            photo = ImageTk.PhotoImage(
                pil_image
            )

            self.tile_photo_images.append(
                photo
            )

            button = tk.Button(
                self.puzzle_container,
                image=photo,
                bd=0,
                padx=0,
                pady=0
            )

            button.grid(
                row=index // self.grid_size,
                column=index % self.grid_size
            )

            button.bind(
                "<Button-1>",
                lambda event, i=index:
                self.left_click(
                    i,
                    event
                )
            )

            button.bind(
                "<Button-3>",
                lambda event, i=index:
                self.right_click(i)
            )

    # =========================================================
    # LEFT CLICK
    # =========================================================

    def left_click(
        self,
        index,
        event
    ):

        if self.puzzle is None:
            return

        if self.puzzle.solved:
            return

        shift_pressed = (
            (event.state & 0x0001) != 0
        )

        # =====================================================
        # SHIFT + LEFT CLICK = FLIP
        # =====================================================

        if shift_pressed:

            self.clear_hint()

            self.puzzle.flip_tile(
                index,
                "horizontal"
            )

            self.selected_tile = None

            self.update_after_move()

            return

        # =====================================================
        # NORMAL LEFT CLICK
        # =====================================================

        self.clear_hint()

        if self.selected_tile is None:

            self.selected_tile = index

            self.create_puzzle_buttons()

            return

        if self.selected_tile == index:

            self.selected_tile = None

            self.create_puzzle_buttons()

            return

        first = self.selected_tile
        second = index

        self.puzzle.swap_tiles(
            first,
            second
        )

        self.selected_tile = None

        self.update_after_move()

    # =========================================================
    # RIGHT CLICK = ROTATE
    # =========================================================

    def right_click(self, index):

        if self.puzzle is None:
            return

        if self.puzzle.solved:
            return

        self.clear_hint()

        self.puzzle.rotate_tile(
            index,
            90
        )

        self.selected_tile = None

        self.update_after_move()

    # =========================================================
    # UPDATE AFTER MOVE
    # =========================================================

    def update_after_move(self):

        if self.puzzle.is_solved():

            self.puzzle.solved = True

            self.selected_tile = None

            self.hint_tile = None
            self.hint_home = None

            self.create_puzzle_buttons()

            self.display_original()

            self.update_information()

            messagebox.showinfo(
                "Puzzle Solved!",
                "Congratulations!\n\n"
                "The puzzle has been solved."
            )

            return

        self.create_puzzle_buttons()

        self.display_original()

        self.update_information()

    # =========================================================
    # UPDATE INFORMATION
    # =========================================================

    def update_information(self):

        if self.puzzle is None:
            return

        self.moves_label.config(
            text=(
                "Moves: "
                + str(
                    self.puzzle.moves
                )
            )
        )

        self.incorrect_label.config(
            text=(
                "Incorrect tiles: "
                + str(
                    self.puzzle.get_incorrect_count()
                )
            )
        )

        self.hints_label.config(
            text=(
                "Hints: "
                + str(
                    self.puzzle.hints_used
                )
                + "/3"
            )
        )

        if self.puzzle.hints_used >= 3:

            self.hint_button.config(
                state="disabled"
            )

        else:

            self.hint_button.config(
                state="normal"
            )

    # =========================================================
    # HINT
    # =========================================================

    def give_hint(self):

        if self.puzzle is None:

            messagebox.showwarning(
                "No Image",
                "Please choose an image first."
            )

            return

        if self.puzzle.solved:
            return

        if self.puzzle.hints_used >= 3:

            messagebox.showinfo(
                "Hints",
                "You have used all 3 hints."
            )

            return

        # =====================================================
        # FIND ALL INCORRECT TILES
        # =====================================================

        incorrect_positions = []

        for position, tile in enumerate(
            self.puzzle.tiles
        ):

            if not tile.is_correct(position):

                incorrect_positions.append(
                    position
                )

        if not incorrect_positions:
            return

        # =====================================================
        # FIND AN INCORRECT TILE NOT HINTED BEFORE
        # =====================================================

        available_positions = []

        for position in incorrect_positions:

            if position not in self.hinted_positions:

                available_positions.append(
                    position
                )

        if available_positions:

            incorrect_position = (
                available_positions[0]
            )

        else:

            incorrect_position = (
                incorrect_positions[0]
            )

        # =====================================================
        # REMEMBER THIS HINT
        # =====================================================

        if incorrect_position not in self.hinted_positions:

            self.hinted_positions.append(
                incorrect_position
            )

        # =====================================================
        # CURRENT SCRAMBLED LOCATION
        # =====================================================

        self.hint_tile = (
            incorrect_position
        )

        # =====================================================
        # CORRECT ORIGINAL LOCATION
        # =====================================================

        self.hint_home = (
            self.puzzle.tiles[
                incorrect_position
            ].correct_position
        )

        # =====================================================
        # INCREASE HINT COUNT
        # =====================================================

        self.puzzle.hints_used += 1

        # =====================================================
        # DISPLAY HINT
        # =====================================================

        self.create_puzzle_buttons()

        self.display_original()

        self.update_information()

    # =========================================================
    # CLEAR HINT
    # =========================================================

    def clear_hint(self):

        self.hint_tile = None
        self.hint_home = None

    # =========================================================
    # SCRAMBLE
    # =========================================================

    def scramble_puzzle(self):

        if self.puzzle is None:

            messagebox.showwarning(
                "No Image",
                "Please choose an image first."
            )

            return

        # =====================================================
        # REBUILD ORIGINAL CORRECT TILE ORDER
        # =====================================================

        original_tiles = (
            [None] * len(self.puzzle.tiles)
        )

        for tile in self.puzzle.tiles:

            original_tiles[
                tile.correct_position
            ] = (
                tile.original_image.copy()
            )

        # =====================================================
        # CREATE NEW PUZZLE FROM ORIGINAL ORDER
        # =====================================================

        self.puzzle = Puzzle(
            original_tiles,
            self.grid_size
        )

        self.selected_tile = None

        self.hint_tile = None
        self.hint_home = None

        self.hinted_positions = []

        # =====================================================
        # CREATE NEW RANDOM SCRAMBLE
        # =====================================================

        self.puzzle.scramble()

        self.create_puzzle_buttons()

        self.display_original()

        self.update_information()

    # =========================================================
    # SOLVE
    # =========================================================

    def solve_puzzle(self):

        if self.puzzle is None:

            messagebox.showwarning(
                "No Image",
                "Please choose an image first."
            )

            return

        if self.puzzle.solved:
            return

        self.puzzle.solve()

        self.selected_tile = None

        self.hint_tile = None
        self.hint_home = None

        self.create_puzzle_buttons()

        self.display_original()

        self.update_information()

        messagebox.showinfo(
            "Puzzle Solved",
            "The puzzle has been solved."
        )


# =============================================================
# MAIN PROGRAM
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    PuzzleGUI(root)

    root.mainloop()