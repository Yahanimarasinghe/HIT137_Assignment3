import random
import cv2
import numpy as np
from abc import ABC, abstractmethod


# =============================================================
# PUZZLE TILE
# =============================================================

class PuzzleTile:
    """Represents one tile in the image puzzle."""

    def __init__(self, image, correct_position):
        self.original_image = image.copy()
        self.image = image.copy()
        self.correct_position = correct_position

        # Store the current transformation state.
        self.rotation = 0
        self.flip_horizontal = False
        self.flip_vertical = False

    def is_correct(self, current_position):
        """
        Check whether the tile is completely correct.

        A tile is correct only when:
        1. It is in its original position.
        2. Its image has the original orientation.
        """

        return (
            current_position == self.correct_position
            and np.array_equal(
                self.image,
                self.original_image
            )
        )


# =============================================================
# TRANSFORMATION BASE CLASS
# =============================================================

class Transformation(ABC):
    """
    Abstract base class for puzzle transformations.

    Subclasses implement apply().
    This demonstrates inheritance and polymorphism.
    """

    @abstractmethod
    def apply(self, puzzle, target_index=None):
        """Apply the transformation to the puzzle."""
        pass


# =============================================================
# SWAP TRANSFORMATION
# =============================================================

class SwapTransformation(Transformation):
    """Swaps the target tile with another randomly selected tile."""

    def apply(self, puzzle, target_index=None):

        if len(puzzle.tiles) < 2:
            return

        if target_index is None:
            first = random.randrange(
                len(puzzle.tiles)
            )
        else:
            first = target_index

        possible_second = [
            i
            for i in range(len(puzzle.tiles))
            if i != first
        ]

        second = random.choice(
            possible_second
        )

        puzzle.swap_tiles(
            first,
            second,
            count_move=False,
            record_history=True
        )


# =============================================================
# ROTATE TRANSFORMATION
# =============================================================

class RotateTransformation(Transformation):
    """Rotates one puzzle tile by 90, 180 or 270 degrees."""

    def apply(self, puzzle, target_index=None):

        if len(puzzle.tiles) == 0:
            return

        if target_index is None:
            index = random.randrange(
                len(puzzle.tiles)
            )
        else:
            index = target_index

        angle = random.choice(
            [90, 180, 270]
        )

        puzzle.rotate_tile(
            index,
            angle,
            count_move=False,
            record_history=True
        )


# =============================================================
# FLIP TRANSFORMATION
# =============================================================

class FlipTransformation(Transformation):
    """Flips one puzzle tile horizontally or vertically."""

    def apply(self, puzzle, target_index=None):

        if len(puzzle.tiles) == 0:
            return

        if target_index is None:
            index = random.randrange(
                len(puzzle.tiles)
            )
        else:
            index = target_index

        direction = random.choice(
            [
                "horizontal",
                "vertical"
            ]
        )

        puzzle.flip_tile(
            index,
            direction,
            count_move=False,
            record_history=True
        )


# =============================================================
# PUZZLE CLASS
# =============================================================

class Puzzle:
    """
    Main puzzle controller.

    Manages:
    - puzzle tiles
    - grid size
    - player moves
    - hints
    - scrambling
    - transformations
    - solution checking
    - solving
    """

    def __init__(self, tiles, grid_size):

        if grid_size not in (3, 4, 5):
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        expected_tiles = grid_size * grid_size

        if len(tiles) != expected_tiles:
            raise ValueError(
                f"A {grid_size}x{grid_size} puzzle "
                f"requires {expected_tiles} tiles."
            )

        self.grid_size = grid_size

        self.tiles = []

        self.moves = 0
        self.hints_used = 0
        self.solved = False

        # Stores transformations so Solve can reverse them.
        self.history = []

        # Create PuzzleTile objects.
        for position, image in enumerate(tiles):

            tile = PuzzleTile(
                image,
                position
            )

            self.tiles.append(tile)

    # =========================================================
    # SWAP TILES
    # =========================================================

    def swap_tiles(
        self,
        first,
        second,
        count_move=True,
        record_history=True
    ):
        """
        Swap two tiles.

        Parameters:
            first: index of first tile
            second: index of second tile
            count_move: whether to increase player move count
            record_history: whether to save the action
        """

        if not (
            0 <= first < len(self.tiles)
            and 0 <= second < len(self.tiles)
        ):
            return

        if first == second:
            return

        self.tiles[first], self.tiles[second] = (
            self.tiles[second],
            self.tiles[first]
        )

        if record_history:
            self.history.append(
                (
                    "swap",
                    first,
                    second
                )
            )

        if count_move:
            self.moves += 1

    # =========================================================
    # ROTATE TILE
    # =========================================================

    def rotate_tile(
        self,
        index,
        angle=90,
        count_move=True,
        record_history=True
    ):
        """
        Rotate a tile clockwise.

        Supported angles:
            90
            180
            270
        """

        if not (
            0 <= index < len(self.tiles)
        ):
            return

        tile = self.tiles[index]

        if angle == 90:

            tile.image = cv2.rotate(
                tile.image,
                cv2.ROTATE_90_CLOCKWISE
            )

        elif angle == 180:

            tile.image = cv2.rotate(
                tile.image,
                cv2.ROTATE_180
            )

        elif angle == 270:

            tile.image = cv2.rotate(
                tile.image,
                cv2.ROTATE_90_COUNTERCLOCKWISE
            )

        else:

            raise ValueError(
                "Rotation angle must be "
                "90, 180 or 270 degrees."
            )

        tile.rotation = (
            tile.rotation + angle
        ) % 360

        if record_history:

            inverse_angle = (
                360 - angle
            ) % 360

            self.history.append(
                (
                    "rotate",
                    index,
                    inverse_angle
                )
            )

        if count_move:
            self.moves += 1

    # =========================================================
    # FLIP TILE
    # =========================================================

    def flip_tile(
        self,
        index,
        direction="horizontal",
        count_move=True,
        record_history=True
    ):
        """
        Flip a tile horizontally or vertically.
        """

        if not (
            0 <= index < len(self.tiles)
        ):
            return

        tile = self.tiles[index]

        if direction == "horizontal":

            tile.image = cv2.flip(
                tile.image,
                1
            )

            tile.flip_horizontal = (
                not tile.flip_horizontal
            )

        elif direction == "vertical":

            tile.image = cv2.flip(
                tile.image,
                0
            )

            tile.flip_vertical = (
                not tile.flip_vertical
            )

        else:

            raise ValueError(
                "Flip direction must be "
                "'horizontal' or 'vertical'."
            )

        if record_history:

            self.history.append(
                (
                    "flip",
                    index,
                    direction
                )
            )

        if count_move:
            self.moves += 1

    # =========================================================
    # SCRAMBLE
    # =========================================================

    def scramble(self):
        """
        Scramble the puzzle using random transformations.

        Required transformation counts:
            3x3 -> 6
            4x4 -> 12
            5x5 -> 20

        Each physical puzzle tile is selected as a primary
        transformation target at most once.

        The three transformation types are:
            - Swap
            - Rotate
            - Flip
        """

        transformation_count = {
            3: 6,
            4: 12,
            5: 20
        }

        if self.grid_size not in transformation_count:
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        count = transformation_count[
            self.grid_size
        ]

        if count > len(self.tiles):
            raise ValueError(
                "Not enough tiles for the required "
                "scramble transformations."
            )

        # -----------------------------------------------------
        # Create transformation objects.
        #
        # These classes demonstrate polymorphism because
        # each object implements apply() differently.
        # -----------------------------------------------------

        transformations = [
            SwapTransformation(),
            RotateTransformation(),
            FlipTransformation()
        ]

        # -----------------------------------------------------
        # Make sure all three transformation types are used.
        #
        # The remaining transformations are chosen randomly.
        # -----------------------------------------------------

        plan = [
            SwapTransformation(),
            RotateTransformation(),
            FlipTransformation()
        ]

        remaining = count - len(plan)

        for _ in range(remaining):
            plan.append(
                random.choice(
                    transformations
                )
            )

        # Randomise the order of all transformations.
        random.shuffle(plan)

        # -----------------------------------------------------
        # Select unique PHYSICAL tiles.
        #
        # Tile objects are selected first, rather than positions.
        # This means a tile cannot become the primary target
        # twice, even if a previous swap moves it.
        # -----------------------------------------------------

        target_tiles = random.sample(
            self.tiles,
            count
        )

        # -----------------------------------------------------
        # Apply each transformation to its unique target tile.
        # -----------------------------------------------------

        for transformation, target_tile in zip(
            plan,
            target_tiles
        ):

            # Find the target tile's CURRENT position.
            target_index = self.tiles.index(
                target_tile
            )

            transformation.apply(
                self,
                target_index
            )

    # =========================================================
    # GET INCORRECT TILE COUNT
    # =========================================================

    def get_incorrect_count(self):
        """
        Return the number of tiles that are not completely
        correct.
        """

        incorrect = 0

        for position, tile in enumerate(
            self.tiles
        ):

            if not tile.is_correct(
                position
            ):

                incorrect += 1

        return incorrect

    # =========================================================
    # CHECK WHETHER PUZZLE IS SOLVED
    # =========================================================

    def is_solved(self):
        """
        Return True only when every tile is in its correct
        position and orientation.
        """

        for position, tile in enumerate(
            self.tiles
        ):

            if not tile.is_correct(
                position
            ):

                return False

        return True

    # =========================================================
    # SOLVE PUZZLE
    # =========================================================

    def solve(self):
        """
        Instantly solve the puzzle by reversing every
        recorded transformation.

        The move counter is reset to zero after solving.
        """

        # Reverse every recorded action.
        for action in reversed(
            self.history
        ):

            action_type = action[0]

            # -------------------------------------------------
            # Reverse swap
            # -------------------------------------------------

            if action_type == "swap":

                _, first, second = action

                self.swap_tiles(
                    first,
                    second,
                    count_move=False,
                    record_history=False
                )

            # -------------------------------------------------
            # Reverse rotation
            # -------------------------------------------------

            elif action_type == "rotate":

                _, index, angle = action

                if angle != 0:

                    self.rotate_tile(
                        index,
                        angle,
                        count_move=False,
                        record_history=False
                    )

            # -------------------------------------------------
            # Reverse flip
            # -------------------------------------------------

            elif action_type == "flip":

                _, index, direction = action

                self.flip_tile(
                    index,
                    direction,
                    count_move=False,
                    record_history=False
                )

        # Clear history after solving.
        self.history.clear()

        # Reset move counter.
        self.moves = 0

        # Mark puzzle as solved.
        self.solved = True