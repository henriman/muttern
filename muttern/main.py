import tkinter as tk
from PIL import Image, ImageTk
import time
import imutils
import imutils.video as video
import cv2
import database
from pyzbar import pyzbar

def stream():
    # Grab the current frame of the video stream.
    frame = video_stream.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB color space.

    # Display frame.
    display_image = Image.fromarray(frame)
    display_image = ImageTk.PhotoImage(display_image)
    image.config(image=display_image)
    image.image = display_image

    frame = imutils.resize(frame, width=320)  # Resize to improve performance.

    # Find and decode the barcodes in the frame.
    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:
        # Convert the barcode data into a string.
        barcode_data = barcode.data.decode("utf-8")

        # Get the product from the database and display it.
        product = dbh.get(barcode_data)
        if product:
            barcode_text.set(barcode_data)
            brand_text.set(product.brands)
            name_text.set(product.name)

    # Continue streaming video.
    image.after(delay, stream)

# Configure window.
root = tk.Tk()
root.title('muttern')
#root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda _: root.destroy())

# Variables.
barcode_text = tk.StringVar()
brand_text = tk.StringVar()
name_text = tk.StringVar()

# Add the widgets.
image = tk.Label()
image.pack()

barcode_label = tk.Label(root, textvariable=barcode_text)
barcode_label.pack()
brand_label = tk.Label(root, textvariable=brand_text)
brand_label.pack()
name_label = tk.Label(root, textvariable=name_text)
name_label.pack()

# Initialize the video stream.
video_stream = video.VideoStream(usePiCamera=True, resolution=(640, 480)).start()
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
