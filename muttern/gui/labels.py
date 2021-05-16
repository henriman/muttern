import tkinter as tk
import numpy
from PIL import Image, ImageTk

class ImageLabel(tk.Label):
    """A label with an updatable image."""

    def update_image(self, image: numpy.ndarray) -> None:
        """Update the label with the given image."""

        display_image = Image.fromarray(image)
        display_image = ImageTk.PhotoImage(display_image)
        self.config(image=display_image)
        self.image = display_image
