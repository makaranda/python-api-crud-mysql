from flask import Flask, render_template, request, jsonify
import cv2
import dlib
import numpy as np
import mysql.connector
from PIL import Image
import io

app = Flask(__name__)

# Initialize dlib face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(dlib.download_dlib_model('shape_predictor_68_face_landmarks.dat'))

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword",
    database="attendance_db"
)
cursor = db.cursor()

# Load known faces
known_faces = {}
def load_known_faces():
    # Example function to load known faces from the database
    cursor.execute("SELECT id, face_encoding FROM employees")
    for (id, face_encoding) in cursor:
        known_faces[id] = np.frombuffer(face_encoding, dtype=np.float64)

load_known_faces()

def get_face_encoding(image):
    # Convert image to gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Detect faces in the image
    faces = detector(gray)
    encodings = []
    for face in faces:
        shape = predictor(gray, face)
        face_encoding = np.array([shape.part(i) for i in range(68)])
        encodings.append(face_encoding)
    return encodings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    file = request.files['image'].read()
    image = np.array(Image.open(io.BytesIO(file)))
    
    face_encodings = get_face_encoding(image)
    if face_encodings:
        for encoding in face_encodings:
            for id, known_encoding in known_faces.items():
                if np.allclose(encoding, known_encoding, atol=0.6):
                    # Mark attendance
                    cursor.execute("INSERT INTO attendance (user_id, timestamp) VALUES (%s, NOW())", (id,))
                    db.commit()
                    return jsonify({"status": "success", "user_id": id})
    
    return jsonify({"status": "error", "message": "Face not recognized"})

if __name__ == '__main__':
    app.run(debug=True)
