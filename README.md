# FaceSecure-ATM-Pinless-Banking-System
FaceSecure ATM is a pinless banking system that uses face recognition for secure authentication. It integrates a webcam, Arduino-based RFID triggers, and a Streamlit web interface, allowing users to check balance, deposit, withdraw, and view transaction history while ensuring safety and convenience.

## Features
- Face recognition authentication using OpenCV, face_recognition, and Mediapipe
- RFID-based ATM hardware integration via Arduino
- Web interface for balance inquiry, deposit, withdrawal, and transaction history
- Secure user data storage with SQLite database
- Real-time webcam verification with face mesh overlay
- Modular and extensible design for future upgrades

## Components

### Hardware
- Arduino Uno
- LCD Display and Keypad (optional)
- RFID Module and Reader

### Software
- Python 3.12
- OpenCV, Mediapipe, face_recognition
- Streamlit for web interface
- SQLite for database management
- PySerial for Arduino communication

## Setup and Installation

### Hardware Setup
1. Connect Arduino, RFID module, and optional LCD/keypad.
2. Upload the Arduino code to your Arduino Uno.
3. Ensure correct COM port for serial communication.

### Software Setup 
1. Clone the repository:
   <pre>git clone <repository-url></pre>
2. Navigate to the project directory:
   <pre>cd FaceSecure-ATM</pre>
3. Install required Python packages:
   <pre>pip install -r requirements.txt</pre>
4. Initialize the database:
   <pre>python atm_db.py</pre>
6. Ensure face images are stored in the image_Folder.

## Running the Project
1. Face Recognition & Hardware Integration
   <pre>python face_recognition.py</pre>
   - The system waits for RFID triggers from Arduino.
   - Recognized users can access the ATM functions.

2. Streamlit Web Interface
   <pre>streamlit run app.py</pre>
   - Log in with your username and password.
   - Access balance, deposit, withdrawal, and transaction history.

## Project Structure
<pre>
  FaceSecure-ATM/
│
├── app.py                 # Streamlit web interface
├── face_recognition.py    # Face recognition and Arduino integration
├── database.py            # SQLite database management
├── requirements.txt       # Python dependencies
├── image_Folder/          # Folder containing face images
└── ArduinoCode.ino        #
</pre>
- the face recognition script (face_recognition.py) to authenticate users.
- Open the Streamlit web interface (app.py) to manage account functions like balance inquiry, deposits, withdrawals, and transaction history.
- Use the ATM interface securely without PINs, relying on facial verification.

## Notes 
- Ensure your webcam is connected and functional.
- Use the correct COM port in face_recognition.py for Arduino communication.
- For additional users, add face images in the image_Folder and update the database if needed.
