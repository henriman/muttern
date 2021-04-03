import tkinter as tk
from PIL import Image, ImageTk
import cv2
import database
import configparser
from typing import Callable, Any, Optional, Tuple, List
import product
import barcode_scanner
import config as cfg
import numpy

class ImageLabel(tk.Label):
    def update_image(self, image: numpy.ndarray) -> None:
        display_image = Image.fromarray(image)
        display_image = ImageTk.PhotoImage(display_image)
        self.config(image=display_image)
        self.image = display_image

class GUI(tk.Tk):

    config = configparser.ConfigParser()
    config.read("config.ini")

    screen_size = cfg.str_to_tuple(config["hardware"]["screen_size"], int)
    resolution = cfg.str_to_tuple(config["hardware"]["resolution"], int)
    framerate = config["hardware"].getint("framerate")

    stream_delay = int(1000 / framerate)

    def __init__(self, barcode_scanner: barcode_scanner.BarcodeScanner) -> None:
        """Initialize the GUI."""

        super().__init__()

        self.barcode_scanner = barcode_scanner

        # Configure the window.
        self.title("muttern")
        self.geometry(f"{self.screen_size[0]}x{self.screen_size[1]}")
        self.configure(bg="white")
        # TODO: translate to fullscreen
        # root.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda _: self.destroy())

        # Create string variables.
        self.barcode_text = tk.StringVar()
        self.brand_text = tk.StringVar()
        self.name_text = tk.StringVar()

        # Create the widgets.
        self.image = ImageLabel(self, bg="white")
        self.image.grid(rowspan=5)

        # Label which shows the scanned barcode.
        self.barcode_label = tk.Label(
            self,
            bg="white",
            textvariable=self.barcode_text,
            wraplength=self.screen_size[0] - self.resolution[0]
        )
        self.barcode_label.grid(row=0, column=1, sticky="NS")

        # Label which shows the brand of the scanned item.
        self.brand_label = tk.Label(
            self,
            bg="white",
            textvariable=self.brand_text,
            wraplength=self.screen_size[0] - self.resolution[0]
        )
        self.brand_label.grid(row=1, column=1, sticky="NS")

        # Label which shows the name of the scanned item.
        self.name_label = tk.Label(
            self,
            bg="white",
            textvariable=self.name_text,
            wraplength=self.screen_size[0] - self.resolution[0]
        )
        self.name_label.grid(row=2, column=1, sticky="NS")

        # Retrieve the image for the confirm button and scale it down.
        # Note that you must keep a reference to the image object.
        confirm_image = Image.open("assets/checkmark.png")
        confirm_image = confirm_image.resize(
            (confirm_image.width // 2, confirm_image.height // 2)
        )
        self.confirm_image = ImageTk.PhotoImage(confirm_image)
        # FIXME: Tkinter size specifications suck;
        # specifying the right width and height won't actually make widgets that size.
        self.confirm_button = tk.Button(
            self,
            state=tk.DISABLED,
            bg="white",
            width=152,
            height=120,
            image=self.confirm_image,
            command=lambda: self.image.after(self.stream_delay, self.stream)
        )
        self.confirm_button.grid(row=3, column=1, sticky="NSEW")

        # Retrieve the image for the dismiss button and scale it down.
        # Note that you must keep a reference to the image object.
        dismiss_image = Image.open("assets/cross.png")
        dismiss_image = dismiss_image.resize(
            (dismiss_image.width // 2, dismiss_image.height // 2)
        )
        self.dismiss_image = ImageTk.PhotoImage(dismiss_image)
        self.dismiss_button = tk.Button(
            self,
            state=tk.DISABLED,
            bg="white",
            width=152,
            height=120,
            image=self.dismiss_image,
            command=lambda: self.image.after(self.stream_delay, self.stream)
        )
        self.dismiss_button.grid(row=4, column=1, sticky="NSEW")

    def stream(self) -> None:
        # Get the current frame and scan it for barcodes.
        products: Any  # TODO: actual type
        (frame, products) = self.barcode_scanner.get_and_scan_current_frame()

        # Display frame.
        self.image.update_image(frame)

        if not products:
            # Continue streaming video.
            self.image.after(self.stream_delay, self.stream)
            self.confirm_button.config(state=tk.DISABLED)
        else:
            self.confirm_button.config(state=tk.NORMAL)

        for product in products:
            self.barcode_text.set(product.barcode)
            self.brand_text.set(product.brands)
            self.name_text.set(product.name)

with database.OFFDatabaseHandler(cache_location=None) as dbh:
    with barcode_scanner.BarcodeScanner(dbh) as scanner:
        gui = GUI(scanner)
        gui.stream()
        gui.mainloop()
