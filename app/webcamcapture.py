#!/usr/bin/env python3

import os
import cv2 as cv
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from flask import Flask, Response

# ---------------- CONFIG ----------------
print("Available style images in 'styles' directory:")
for filename in os.listdir(STYLE_DIR):
    if filename.endswith((".png", ".jpg", ".jpeg")):
        print(f" - {filename}")
        
STYLE_IMAGE_NAME = input("Enter the name of the style image (e.g., 'picasso.png'): ")
CAMERA_INDEX = 0
WIDTH, HEIGHT = 640, 360

# ----------------------------------------

os.environ["TFHUB_MODEL_LOAD_FORMAT"] = "COMPRESSED"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_DIR = os.path.join(BASE_DIR, "styles")

# ---------------- LOAD MODEL ----------------

print("Loading model...")
model = hub.load(
    "https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2"
)
print("Model loaded.")

# ---------------- LOAD STYLE IMAGE ----------------

def load_image(path):
    img = tf.io.read_file(path)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)
    return img[tf.newaxis, ...]

style_image = load_image(os.path.join(STYLE_DIR, STYLE_IMAGE_NAME))

# ---------------- CAMERA ----------------

cap = cv.VideoCapture(CAMERA_INDEX)
cap.set(cv.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, HEIGHT)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

# ---------------- FLASK - GENERATE FRAMES ----------------

app = Flask(__name__)

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        frame = tf.image.convert_image_dtype(frame, tf.float32)
        frame = frame[tf.newaxis, ...]

        stylized = model(frame, style_image)[0]
        output = np.squeeze(stylized.numpy())

        output = (output * 255).astype(np.uint8)
        output = cv.cvtColor(output, cv.COLOR_RGB2BGR)

        _, buffer = cv.imencode(".jpg", output)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

@app.route("/")
def index():
    return """
    <html>
        <head><title>Live Style Transfer</title></head>
        <body>
            <h1>Live Webcam Style Transfer</h1>
            <img src="/video">
        </body>
    </html>
    """

@app.route("/video")
def video():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
