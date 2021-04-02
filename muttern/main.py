import tkinter as tk
from PIL import Image, ImageTk
import time
import imutils
import imutils.video as video
import cv2
import database
from pyzbar import pyzbar
import configparser
from typing import Callable, Any

def str_to_tuple(s: str, f: Callable[[str], Any]):
    return tuple(map(f, s.strip("()").split(", ")))

def show_frame(frame) -> None:
    display_image = Image.fromarray(frame)
    display_image = ImageTk.PhotoImage(display_image)
    image.config(image=display_image)
    image.image = display_image

config = configparser.ConfigParser()
config.read("config.ini")

screen_size = str_to_tuple(config["hardware"]["screen_size"], int)
resolution = str_to_tuple(config["hardware"]["resolution"], int)
framerate = config["hardware"].getint("framerate")

def stream() -> None:
    # Grab the current frame of the video stream.
    frame = video_stream.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB color space.

    # Display frame.
    show_frame(frame)

    # Find and decode the barcodes in the frame.
    barcodes = pyzbar.decode(frame)

    if not barcodes:
        # Continue streaming video.
        image.after(delay, stream)
        confirm_button.config(state=tk.DISABLED)
    else:
        confirm_button.config(state=tk.NORMAL)

    for barcode in barcodes:
        # Convert the barcode data into a string.
        barcode_data = barcode.data.decode("utf-8")

        (x, y, w, h) = barcode.rect

        # Get the product from the database and display it.
        product = dbh.get(barcode_data)
        if product:
            # Display frame with a rectangle drawn around the barcode.
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
            show_frame(frame)

            barcode_text.set(barcode_data)
            brand_text.set(product.brands)
            name_text.set(product.name)

# Configure window.
root = tk.Tk()
root.title('muttern')
root.geometry(f"{screen_size[0]}x{screen_size[1]}")
# TODO: translate to fullscreen
# root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda _: root.destroy())

# Variables.
barcode_text = tk.StringVar()
brand_text = tk.StringVar()
name_text = tk.StringVar()

# Add the widgets.
image = tk.Label()
image.grid(rowspan=5)

barcode_label = tk.Label(
    root,
    textvariable=barcode_text,
    wraplength=screen_size[0] - resolution[0]
)
barcode_label.grid(row=0, column=1, sticky="NS")
brand_label = tk.Label(
    root,
    textvariable=brand_text,
    wraplength=screen_size[0] - resolution[0]
)
brand_label.grid(row=1, column=1, sticky="NS")
name_label = tk.Label(
    root,
    textvariable=name_text,
    wraplength=screen_size[0] - resolution[0]
)
name_label.grid(row=2, column=1, sticky="NS")

# Tkinter size specifications suck.
confirm_image = Image.open("checkmark.png")
confirm_image = confirm_image.resize(
    (confirm_image.width // 2, confirm_image.height // 2)
)
confirm_image = ImageTk.PhotoImage(confirm_image)
confirm_button = tk.Button(
    root,
    state=tk.DISABLED,
    width=151,
    height=111,
    image=confirm_image,
    command=lambda: image.after(delay, stream)
)
confirm_button.grid(row=3, column=1, sticky="NSEW")
confirm_button.grid_propagate(0)

dismiss_image = Image.open("cross.png")
dismiss_image = dismiss_image.resize(
    (dismiss_image.width // 2, dismiss_image.height // 2)
)
dismiss_image = ImageTk.PhotoImage(dismiss_image)
dismiss_button = tk.Button(
    root,
    state=tk.DISABLED,
    width=151,
    height=111,
    image=dismiss_image,
    command=lambda: image.after(delay, stream)
)
dismiss_button.grid(row=4, column=1, sticky="NSEW")
dismiss_button.grid_propagate(0)

# Initialize the video stream.
video_stream = video.VideoStream(
    usePiCamera=True,
    framerate=framerate,
    resolution=resolution
).start()
# TODO: let sleep asynchronously?
time.sleep(2)  # Allow the camera sensor to warm up.

delay = int(1000 / video_stream.camera.framerate)

# Initialize the database handler.
database_handler = database.OFFDatabaseHandler(cache_location=None)
with database_handler as dbh:
    stream()

root.mainloop()

# Stop the stream after the window was closed.
video_stream.stop()
