"""This module includes all GUI elements."""

import tkinter as tk
from PIL import Image, ImageTk
import gui.labels
import configparser
import database
from typing import Any
import barcode_scanner
import config as cfg
import gui.frames as frames

class MainGUI(tk.Tk):
    """The barcode scanner GUI."""

    configuration = configparser.ConfigParser()
    configuration.read("config.ini")

    screen_size = cfg.str_to_tuple(configuration["hardware"]["screen_size"], int)

    def __init__(self, barcode_scanner) -> None:
        """Initialize the GUI."""

        super().__init__()

        # Configure the window.
        self.title("muttern")
        self.geometry(f"{self.screen_size[0]}x{self.screen_size[1]}")
        self.configure(bg="white")
        # TODO: translate to fullscreen
        # root.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda _: self.destroy())

        bs_frame = frames.BarcodeScannerFrame(self, barcode_scanner)
        bs_frame.pack()
        bs_frame.stream()
