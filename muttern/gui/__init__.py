"""This module includes all GUI elements."""

import tkinter as tk
from PIL import Image, ImageTk
import gui.labels
import configparser
import database
from typing import Any
import barcode_scanner
import config as cfg
import gui.frames

class MainGUI(tk.Tk):
    """The barcode scanner GUI."""

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

        with database.OFFDatabaseHandler(cache_location=None) as dbh:
            with barcode_scanner.BarcodeScanner(dbh) as scanner:
                bs_frame = frames.BarcodeScannerFrame(self, barcode_scanner)
                bs_frame.pack()
                bs_frame.stream()
