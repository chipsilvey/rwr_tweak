# Load a PNG file into an OpenCV Mat object using cv2.IMREAD_UNCHANGED to preserve the alpha channel.
# Apply a series of manipulations based on the settings dictionary.
# Save the modified image array back to a file.

# image_processor.py
# Contains all OpenCV logic for image manipulation.

from typing import Any
import cv2
import numpy as np

class ImageProcessor:
    """
    Handles loading, processing, and saving images using OpenCV.
    """
    def __init__(self):
        # original_image_cv holds the pristine image loaded from disk (in OpenCV format)
        self.original_image_cv = None
        # processed_image_cv holds the result of the latest manipulation
        self.processed_image_cv = None

    def load(self, path:str) -> cv2.Mat | np.ndarray[Any, np.dtype[np.integer[Any] | np.floating[Any]]] | None:
        """
        Loads an image from the given path using OpenCV.
        Crucially, it uses IMREAD_UNCHANGED to preserve the alpha (transparency) channel.
        """
        # cv2.imread loads images in BGR(A) format (Blue, Green, Red, Alpha)
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if image is None:
            # This can happen if the file is corrupt or not a valid image format
            raise ValueError(f"Could not load image from path: {path}")
        
        # Ensure the image has an alpha channel for consistent processing.
        # If it's a 3-channel BGR image, we add a 4th (alpha) channel.
        if image.shape[2] == 3:
            print("Image is BGR, converting to BGRA")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        
        return image

    def save(self, path, image_data):
        """
        Saves the given image data (NumPy array) to the specified path.
        """
        if image_data is not None:
            cv2.imwrite(path, image_data)
        else:
            raise ValueError("No processed image data to save.")
