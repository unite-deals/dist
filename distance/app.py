from flask import Flask, render_template, Response
import cv2
import numpy as np
import math

app = Flask(__name__)
video_capture = cv2.VideoCapture(0)
points = []

def generate_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            frame = process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def process_frame(frame):
    for point in points:
        cv2.circle(frame, point, 5, (0, 0, 255), -1)

    if len(points) == 2:
        distance = calculate_distance(points[0], points[1])
        cv2.putText(frame, f"Distance: {distance:.2f} meters", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        points.clear()

    return frame

def calculate_distance(point1, point2):
    pixel_distance = math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    # Assuming a known conversion factor from pixels to meters
    conversion_factor = 0.1
    distance = pixel_distance * conversion_factor
    return distance

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/point', methods=['POST'])
def point():
    x = int(request.form['x'])
    y = int(request.form['y'])
    points.append((x, y))
    return 'Point added'

if __name__ == '__main__':
    app.run()
