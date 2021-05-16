"""This module includes all GUI elements."""

import tkinter as tk
from PIL import Image, ImageTk
import gui.labels
import configparser
from typing import Any
import barcode_scanner
import config as cfg
import gui.frames

class MainGUI(tk.Tk):
    """The barcode scanner GUI."""

    configuration = configparser.ConfigParser()
    configuration.read("config.ini")

    screen_size = cfg.str_to_tuple(configuration["hardware"]["screen_size"], int)
    resolution = cfg.str_to_tuple(configuration["hardware"]["resolution"], int)
    framerate = configuration["hardware"].getint("framerate")

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

        self.bs_frame = frames.BarcodeScannerFrame(self, barcode_scanner)
        self.bs_frame.pack()
        self.bs_frame.stream()
