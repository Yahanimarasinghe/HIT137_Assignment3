"""test_logic.py - checks the puzzle logic for all grid sizes.
Run with:  python test_logic.py"""

import random
import numpy as np
import cv2

from image_processor import ImageProcessor
from puzzle import Puzzle


def make_test_image(path):
    img = np.random.randint(0, 255, (300, 420, 3), np.uint8)
    cv2.imwrite(path, img)


def run():
    processor = ImageProcessor(max_width=480, max_height=480)
    for ext in ("jpg", "png", "bmp"):
        make_test_image(f"test_image.{ext}")

    for ext in ("jpg", "png", "bmp"):
        for grid in (3, 4, 5):
            image = processor.load_image(f"test_image.{ext}")
            prepared = processor.prepare_image(image, grid)
            assert prepared.shape[0] % grid == 0
            tiles = processor.create_tiles(prepared, grid)

            for _ in range(50):                       # repeat the randomness
                puzzle = Puzzle(tiles, grid)
                puzzle.scramble()
                expected = {3: 6, 4: 12, 5: 20}[grid]
                assert len(puzzle._history) == expected, "wrong count"
                assert puzzle.get_incorrect_count() > 0
                for _ in range(5):                    # some player moves
                    puzzle.swap_tiles(random.randrange(grid * grid),
                                      random.randrange(grid * grid))
                    puzzle.rotate_tile(random.randrange(grid * grid), 90)
                    puzzle.flip_tile(random.randrange(grid * grid))
                puzzle.solve()
                assert puzzle.is_solved() and puzzle.moves == 0

            # hint limit
            puzzle = Puzzle(tiles, grid)
            puzzle.scramble()
            hints = [puzzle.get_hint() for _ in range(4)]
            assert hints[3] is None and puzzle.hints_used == 3

            joined = processor.tiles_to_image(
                [t.image for t in puzzle.tiles], grid)
            assert joined.shape == prepared.shape
            print(f"{ext.upper()} {grid}x{grid}: OK")

    # A bad file must raise a clear error
    open("bad.png", "w").write("not an image")
    try:
        processor.load_image("bad.png")
        raise SystemExit("bad file was accepted")
    except ValueError as e:
        print("Bad file handled:", e)
    print("All tests passed.")


if __name__ == "__main__":
    run()
