# https://www.pyimagesearch.com/2018/05/21/an-opencv-barcode-and-qr-code-scanner-with-zbar/
# https://www.jeffgeerling.com/blog/2017/fixing-blurry-focus-on-some-raspberry-pi-camera-v2-models
# Import necessary packages.
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import requests

# https://opengtindb.org/index.php
# https://world.openfoodfacts.org/cgi/search.pl
# OFF API: https://documenter.getpostman.com/view/8470508/SVtN3Wzy#exporting-data

# Parse the arguments.
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                help="Path to the output file containing the barcodes.")
args = vars(ap.parse_args())

# Initialize the video stram and allow the camera sensor to warm up.
print("[INFO] Starting video stream.")
vs = VideoStream(usePiCamera=True).start()
time.sleep(2)

# Open the ouput CSV file for writing and initialize the set of barcodes found thus far.
with open(args["output"], "w") as csv:
    found = set()
    while True:
        # Grab the frame from the video stram and resize it to improve performance.
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # Find the barcodes in the frame and decode each of them.
        barcodes = pyzbar.decode(frame)

        for barcode in barcodes:
            # Extract the bounding box location of the barcode and draw it.
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Convert the barcode data into a string.
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            # Retrieve product information.
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
            response = requests.get(url=url)
            data = response.json()
            product_name = data["product"]["product_name"]

            # Draw the barcode data and barcode type on the image.
            # text = f"{barcode_data} ({barcode_type})"
            cv2.putText(frame, product_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # If the barcode is not already in our CSV file, log it.
            if barcode_data not in found:
                csv.write(f"{datetime.datetime.now(), {barcode_data}}\n")
                csv.flush()
                found.add(barcode_data)

        # Show the output frame.
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF

        # If the `q` key was pressed, break from the loop.
        if key == ord("q"):
            break
    print("[INFO] Cleaning up.")
    csv.close()
    cv2.destroyAllWindows()
    vs.stop()
