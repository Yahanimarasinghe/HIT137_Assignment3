import cv2
import numpy as np
from PIL import Image


class ImageProcessor:
    """Handles image loading, resizing and creating puzzle tiles."""

    def __init__(self, max_width=500, max_height=500):
        self.max_width = max_width
        self.max_height = max_height
        self.image = None

    def load_image(self, file_path):
        """
        Load an image from a file.

        Supports standard image formats that OpenCV can read,
        including JPG, JPEG, PNG and BMP.
        """

        if not file_path:
            raise ValueError("No image file was selected.")

        image = cv2.imread(file_path)

        if image is None:
            raise ValueError(
                "Could not load the selected image. "
                "Please choose a valid JPG, PNG or BMP image."
            )

        if image.size == 0:
            raise ValueError("The selected image is empty.")

        self.image = image

        return image

    def resize_image(self, image):
        """
        Resize the image while maintaining its original
        aspect ratio and keeping it within the maximum size.
        """

        if image is None or image.size == 0:
            raise ValueError("Cannot resize an empty image.")

        height, width = image.shape[:2]

        if width <= 0 or height <= 0:
            raise ValueError("The image has invalid dimensions.")

        scale = min(
            self.max_width / width,
            self.max_height / height
        )

        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))

        return cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA
        )

    def prepare_image(self, image, grid_size):
        """
        Resize and crop the image into a square whose
        dimensions are evenly divisible by the selected grid size.
        """

        if grid_size not in (3, 4, 5):
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        if image is None or image.size == 0:
            raise ValueError(
                "Cannot prepare an empty image."
            )

        # Resize while preserving aspect ratio.
        image = self.resize_image(image)

        height, width = image.shape[:2]

        # Find the largest possible square.
        square_size = min(width, height)

        # Ensure the square is large enough for the selected grid.
        if square_size < grid_size:
            raise ValueError(
                "The image is too small for the selected grid size."
            )

        # Calculate the starting position for a centre crop.
        start_x = (width - square_size) // 2
        start_y = (height - square_size) // 2

        # Crop the image into a square.
        image = image[
            start_y:start_y + square_size,
            start_x:start_x + square_size
        ]

        # Make the image dimensions divisible by the grid size.
        final_size = (
            square_size // grid_size
        ) * grid_size

        if final_size < grid_size:
            raise ValueError(
                "The image is too small for the selected grid size."
            )

        # Crop slightly if necessary.
        image = image[
            :final_size,
            :final_size
        ]

        return image

    def create_tiles(self, image, grid_size):
        """
        Divide the prepared image into equal-sized puzzle tiles.
        """

        if grid_size not in (3, 4, 5):
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        if image is None or image.size == 0:
            raise ValueError(
                "Cannot create tiles from an empty image."
            )

        height, width = image.shape[:2]

        if height % grid_size != 0 or width % grid_size != 0:
            raise ValueError(
                "Image dimensions must be divisible by the grid size."
            )

        tile_height = height // grid_size
        tile_width = width // grid_size

        tiles = []

        for row in range(grid_size):

            for col in range(grid_size):

                y1 = row * tile_height
                y2 = y1 + tile_height

                x1 = col * tile_width
                x2 = x1 + tile_width

                tile = image[
                    y1:y2,
                    x1:x2
                ].copy()

                tiles.append(tile)

        return tiles

    def tiles_to_image(self, tiles, grid_size):
        """
        Reassemble puzzle tiles into one complete image.
        """

        if grid_size not in (3, 4, 5):
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        expected_tiles = grid_size * grid_size

        if len(tiles) != expected_tiles:
            raise ValueError(
                f"Expected {expected_tiles} tiles, "
                f"but received {len(tiles)}."
            )

        rows = []

        for row in range(grid_size):

            start = row * grid_size
            end = start + grid_size

            row_tiles = tiles[start:end]

            row_image = np.hstack(row_tiles)

            rows.append(row_image)

        return np.vstack(rows)

    def cv_to_pil(self, image):
        """
        Convert an OpenCV BGR image to a Pillow RGB image.
        """

        if image is None or image.size == 0:
            raise ValueError(
                "Cannot convert an empty image."
            )

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        return Image.fromarray(rgb_image)

        
       