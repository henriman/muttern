import configparser
import time
# import imutils FIXME: necessary?
import imutils.video as video
from pyzbar import pyzbar
import numpy
import cv2
from typing import Callable, Any, Optional, Tuple, List
import product
import config as cfg
import database

class BarcodeScanner:

    config = configparser.ConfigParser()
    config.read("config.ini")

    framerate = config["hardware"].getint("framerate")
    resolution = cfg.str_to_tuple(config["hardware"]["resolution"], int)

    def __init__(self, database_handler: database.DatabaseHandler) -> None:
        """Initialize the video stream."""

        self.video_stream = video.VideoStream(
            usePiCamera=True,
            framerate=self.framerate,
            resolution=self.resolution
        )

        self.dbh = database_handler

    def get_current_frame(self) -> numpy.ndarray:
        """Return the current frame of the video stream."""

        # Grab the current frame and convert it to the right color space.
        frame = self.video_stream.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return frame

    def scan(self, frame: numpy.ndarray) -> List[Tuple[Tuple[int, int, int, int], product.P]]:
        """Scan for barcodes in the given frame; return the corresponding products."""

        # Find and decode the barcodes in the frame.
        barcodes = pyzbar.decode(frame)

        # Initialize list of found products.
        products = list()

        for barcode in barcodes:
            # Convert the barcode data into a string.
            barcode_data = barcode.data.decode("utf-8")

            # Get the corresponding product from the database.
            product = self.dbh.get(barcode_data)
            # TODO: What to do when product not found?
            if product:
                products.append((barcode.rect, product))

        return products

    def get_and_scan_current_frame(self) -> Tuple[numpy.ndarray, List[product.P]]:

        # Grab the current frame.
        frame = self.get_current_frame()

        # Scan for barcodes in the given frame.
        # Store their position as well as the corresponding products.
        barcodes: List[Tuple[Tuple[int, int, int, int], product.P]] = self.scan(frame)

        # Initialize list of found products.
        products = list()

        # Draw an outline around found barcodes.
        for barcode in barcodes:
            # Extract the position of the barcode and the corresponding product.
            ((x, y, w, h), product) = barcode

            # Add the product to the product list.
            products.append(product)

            # Draw the outline.
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

        return (frame, products)

    def __enter__(self) -> "BarcodeScanner":
        """Start the video stream and enter the context manager."""

        self.video_stream.start()
        # TODO: let sleep asynchronously?
        time.sleep(2)  # Allow the camera sensor to warm up.

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stop the video stream; exit the context manager."""

        self.video_stream.stop()
