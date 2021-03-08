import guizero
import imutils.video as video
import time
import imutils
from pyzbar import pyzbar
import requests
import cv2
import database
import sys

def exit_app(video_stream):
    video_stream.stop()
    sys.exit()

# Configure the app.
app = guizero.App(
    title="muttern",
    bg=(255, 255, 255)
)
app.tk.attributes("-fullscreen", True)
app.tk.bind("<Escape>", lambda _: app.destroy())

# Add the widgets.
barcode = guizero.Text(app)
brand = guizero.Text(app)
name = guizero.Text(app)

app.display()

# Initialize the video stream.
video_stream = video.VideoStream(usePiCamera=True).start()
time.sleep(2)  # Allow the camera sensor to warm up.
app.on_close(lambda: exit_app(video_stream))

# Initialize the database handler.
database_handler = database.OFFDatabaseHandler(cache_location=None)
with database_handler as dbh:
    while True:
        # Grab the current frame of the frame from the video stream.
        frame = video_stream.read()
        frame = imutils.resize(frame, width=400)  # Resize to improve performance.

        # Find and decode the barcodes in the frame.
        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            # Convert the barcode data into a string.
            barcode_data = barcode.data.decode("utf-8")

            product = dbh.get(barcode_data)
            if product:
                barcode.clear()
                barcode.append(barcode_data)
                brand.clear()
                brand.append(product.brands)
                name.clear()
                name.append(product.name)

"""
while True:
    # Grab the current frame from the video stream.
    frame = video_stream.read()
    frame = imutils.resize(frame, width=400)  # Resize to improve performance.

    # Find and decode the barcodes in the frame.
    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:
        # Extract the bounding box location of the barcode and draw it.
        # (x, y, w, h) = barcode.rect

        # Convert the barocde data into a string.
        barcode_data = barcode.data.decode("utf-8")

        with database_handler as dbh:
            product = dbh.get(barcode_data)
            if product:
                # Draw the barcode data and barcode type on the image.
                # cv2.putText(frame, f"{product.brands}: {product.name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            # else:
                # cv2.putText(frame, "Product not found", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Show the output frame.
    # cv2.imshow("Barcode scanner", frame)
    # key = cv2.waitKey(1) & 0xff

    # If the `q` key was pressed, break from the loop.
    if key == ord("q"):
        break

cv2.destroyAllWindows()
video_stream.stop()
"""

