import warnings
import cv2
import numpy as np
import face_recognition
import mediapipe as mp
import os
import serial
import time
import webbrowser
from collections import defaultdict

warnings.filterwarnings('ignore', message='SymbolDatabase.GetPrototype() is deprecated')

# -------------------- Serial Communication -------------------- #
try:
    ser = serial.Serial('COM3', 9600, timeout=1)  # Change COM port as needed
    print("[INFO] Serial connection established")
except serial.SerialException as e:
    print(f"[ERROR] Serial connection failed: {e}")
    ser = None

# -------------------- Load Face Images -------------------- #
IMAGE_PATH = 'E:/image_Folder'
images, classNames = [], []
for filename in os.listdir(IMAGE_PATH):
    img = cv2.imread(os.path.join(IMAGE_PATH, filename))
    if img is not None:
        images.append(img)
        classNames.append(os.path.splitext(filename)[0].upper())
print(f"[INFO] Loaded users: {classNames}")

# -------------------- Face Encodings -------------------- #
def encode_faces(images):
    encode_list = []
    for img in images:
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)
        if encodings:
            encode_list.append(encodings[0])
    return encode_list

encodeListKnown = encode_faces(images)
print("[INFO] Face encoding complete.")

# -------------------- Mediapipe Setup -------------------- #
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
mp_drawing = mp.solutions.drawing_utils

# -------------------- Haar Cascade Face Detection -------------------- #
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# -------------------- User Balances -------------------- #
user_balances = defaultdict(lambda: 1000)  # Default balance = 1000

# -------------------- Face Recognition Function -------------------- #
def run_face_recognition():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return None

    recognized_name = None
    recognizedNames = []

    while True:
        success, img = cap.read()
        if not success:
            break

        # Resize for faster processing
        img_small = cv2.resize(img, (0,0), fx=0.25, fy=0.25)
        img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

        faces_current = face_recognition.face_locations(img_rgb)
        encodes_current = face_recognition.face_encodings(img_rgb, faces_current)

        for encode_face, face_loc in zip(encodes_current, faces_current):
            matches = face_recognition.compare_faces(encodeListKnown, encode_face)
            face_dist = face_recognition.face_distance(encodeListKnown, encode_face)
            best_match_index = np.argmin(face_dist)

            if matches[best_match_index]:
                recognized_name = classNames[best_match_index]
                if recognized_name not in recognizedNames:
                    recognizedNames.append(recognized_name)
                    print(f"[INFO] Recognized: {recognized_name}")
                # Scale back coordinates
                y1, x2, y2, x1 = face_loc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.rectangle(img, (x1, y2-35), (x2, y2), (0,255,0), cv2.FILLED)
                cv2.putText(img, recognized_name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)

        # Haar cascade overlay
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)

        # Mediapipe mesh overlay
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=img,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,0), thickness=1, circle_radius=1)
                )

        cv2.imshow('Face Recognition', img)
        if recognized_name:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return recognized_name

# -------------------- ATM Interface -------------------- #
def atm_interface(user_name):
    while True:
        print(f"\nWelcome {user_name}!")
        print("1. Balance Inquiry")
        print("2. Withdraw")
        print("3. Deposit")
        print("4. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            print(f"Balance: ${user_balances[user_name]}")

        elif choice == '2':
            amount = float(input("Withdraw amount: "))
            if amount <= user_balances[user_name]:
                user_balances[user_name] -= amount
                print(f"Withdrew ${amount}. New Balance: ${user_balances[user_name]}")
            else:
                print("Insufficient funds!")

        elif choice == '3':
            amount = float(input("Deposit amount: "))
            user_balances[user_name] += amount
            print(f"Deposited ${amount}. New Balance: ${user_balances[user_name]}")

        elif choice == '4':
            print("Thank you for using the ATM!")
            break

        else:
            print("Invalid choice!")

# -------------------- Main Program -------------------- #
def main():
    if ser is None:
        print("[WARN] Arduino not connected. Proceeding without RFID trigger.")
        recognized_name = run_face_recognition()
        if recognized_name:
            webbrowser.open('http://localhost:8501')  # Change to your Streamlit URL
            atm_interface(recognized_name)
        return

    # Listen for RFID messages from Arduino
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line in ["rfid", "rfid1", "rfid2"]:
                print(f"[INFO] RFID trigger detected: {line}")
                recognized_name = run_face_recognition()
                if recognized_name:
                    print(f"[INFO] User recognized: {recognized_name}")
                    webbrowser.open('http://localhost:8501')  # Launch Streamlit
                    atm_interface(recognized_name)
                else:
                    print("[WARN] Face not recognized. Access denied.")
                break
            else:
                print("[INFO] No card detected.")
        time.sleep(0.1)

if __name__ == "__main__":
    main()
