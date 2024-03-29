import tkinter as tk
import configparser
import config as cfg
import barcode_scanner as bs
import gui.labels as labels
from PIL import Image, ImageTk
import product as prdct
from typing import Any

# TODO: Add type hints
# TODO: Add docstrings
# TODO: Add __slots__?

class BarcodeScannerFrame(tk.Frame):

    configuration = configparser.ConfigParser()
    configuration.read("config.ini")

    screen_size = cfg.str_to_tuple(configuration["hardware"]["screen_size"], int)
    resolution = cfg.str_to_tuple(configuration["hardware"]["resolution"], int)
    framerate = configuration["hardware"].getint("framerate")

    stream_delay = int(1000 / framerate)

    def __init__(self, master, barcode_scanner: bs.BarcodeScanner):
        super().__init__(master)

        # Configure frame.
        self.configure(bg="white")

        self.barcode_scanner = barcode_scanner

        # Create string variables.
        self.barcode_text = tk.StringVar()
        self.brand_text = tk.StringVar()
        self.name_text = tk.StringVar()

        # Create the widgets.
        self.image = labels.ImageLabel(self, bg="white")
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
        confirm_image = Image.open("muttern/assets/checkmark.png")
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
            command=self.confirm
        )
        self.confirm_button.grid(row=3, column=1, sticky="NSEW")

        # Retrieve the image for the dismiss button and scale it down.
        # Note that you must keep a reference to the image object.
        dismiss_image = Image.open("muttern/assets/cross.png")
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

    def confirm(self):
        self.barcode_text.set("")
        self.brand_text.set("")
        self.name_text.set("")
        self.image.after(self.stream_delay, self.stream)

    def stream(self) -> None:
        """Update the GUI with the current frame; scan for barcodes and show product information."""

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

        # Show product information in GUI.
        for product in products:
            self.barcode_text.set(product.barcode)

            if type(product) == prdct.OFFProduct:
                self.brand_text.set(product.brands)
                self.name_text.set(product.name)
            else:
                self.name_text.set("Product not found.")


