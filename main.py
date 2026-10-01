from image_processor import ImageProcessor
from puzzle import Puzzle

print("Starting HIT137 Assignment 3...")

processor = ImageProcessor()

image_path = "test_image.jpg"

grid_size = 5

image = processor.load_image(image_path)
print("Image loaded successfully.")

prepared_image = processor.prepare_image(image, grid_size)
print("Image prepared.")

print("Prepared image size:", prepared_image.shape)

tiles = processor.create_tiles(
    prepared_image,
    grid_size
)

print("Number of tiles:", len(tiles))

puzzle = Puzzle(
    tiles,
    grid_size
)

print("Puzzle created.")

puzzle.scramble()

print("Puzzle scrambled.")

# Reassemble the scrambled tiles
scrambled_image = processor.tiles_to_image(
    [tile.image for tile in puzzle.tiles],
    grid_size
)

print("Scrambled image reassembled successfully.")
print("Scrambled image size:", scrambled_image.shape)

# Solve the puzzle
puzzle.solve()

print("Puzzle solved.")

# Reassemble the solved tiles
solved_image = processor.tiles_to_image(
    [tile.image for tile in puzzle.tiles],
    grid_size
)

print("Solved image reassembled successfully.")
print("Solved image size:", solved_image.shape)

print("Test completed successfully.")