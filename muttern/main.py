import imutils.video as video
import time
import imutils
from pyzbar import pyzbar
import requests
import cv2
import database

# Initialize the video stream.
video_stream = video.VideoStream(usePiCamera=True).start()
time.sleep(2)  # Allow the camera sensor to warm up.

database_handler = database.OFFDatabaseHandler(local_location=None)

while True:
    # Grab the current frame from the video stream.
    frame = video_stream.read()
    frame = imutils.resize(frame, width=400)  # Resize to improve performance.

    # Find and decode the barcodes in the frame.
    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:
        # Extract the bounding box location of the barcode and draw it.
        (x, y, w, h) = barcode.rect

        # Convert the barocde data into a string.
        barcode_data = barcode.data.decode("utf-8")

        with database_handler as dbh:
            product = dbh.get(barcode_data)
            if product:
                product_name = product.name
                # Draw the barcode data and barcode type on the image.
                cv2.putText(frame, product_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Product not found", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Show the output frame.
    cv2.imshow("Barcode scanner", frame)
    key = cv2.waitKey(1) & 0xff

    # If the `q` key was pressed, break from the loop.
    if key == ord("q"):
        break

cv2.destroyAllWindows()
video_stream.stop()
