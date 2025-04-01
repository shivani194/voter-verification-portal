import cv2
import time
import face_recognition
import numpy as np
import os
import sqlite3

VOTER_IMAGES_PATH = "voter_images"  # Folder for voter images
DB_PATH = "voters.db"  # Database path
VOTED_VOTERS_FILE = "voted_voters.txt"  # File to store voted voter IDs

def load_voter_images():
    """Loads known voter images and encodes them."""
    known_faces = []
    known_names = []

    if not os.path.exists(VOTER_IMAGES_PATH):
        print(f"⚠️ Error: Folder '{VOTER_IMAGES_PATH}' not found! Create it and add voter images.")
        return known_faces, known_names

    for file_name in os.listdir(VOTER_IMAGES_PATH):
        if file_name.endswith((".jpg", ".png")):
            image_path = os.path.join(VOTER_IMAGES_PATH, file_name)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)

            if encoding:
                known_faces.append(encoding[0])
                known_names.append(file_name.split(".")[0])  # Use file name as voter name

    if not known_faces:
        print("⚠️ No voter images found in 'voter_images' folder. Add images before running.")
    
    return known_faces, known_names

def capture_image():
    """Opens camera for 5 sec, detects blink, and captures image."""
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    blink_detected = False
    captured_frame = None

    while time.time() - start_time < 5:  # Keep camera open for 5 seconds
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Error: No frame captured. Camera might be busy.")
            continue

        cv2.imshow("Live Feed - Blink to Capture", frame)

        # Blink detection (for now, detecting fast eye movement)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml').detectMultiScale(gray, 1.3, 5)

        if len(eyes) == 0:  # If no eyes are detected, assume blink
            print("👁️ Blink detected! Capturing image...")
            blink_detected = True
            captured_frame = frame
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit if user presses 'q'
            break

    cap.release()
    cv2.destroyAllWindows()

    if not blink_detected:
        print("⚠️ No blink detected. Try again.")
        return None

    return captured_frame

def recognize_face(captured_frame, known_faces, known_names):
    """Compares captured face with stored voter images using the best match."""
    if captured_frame is None:
        print("⚠️ No image captured. Exiting...")
        return "Unknown"

    rgb_frame = cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB)
    captured_encodings = face_recognition.face_encodings(rgb_frame)

    if not captured_encodings:
        print("⚠️ No face detected. Try again with better lighting.")
        return "Unknown"

    # Get the first face encoding found in the captured image
    captured_encoding = captured_encodings[0]

    # Compare the captured encoding with all known encodings
    face_distances = face_recognition.face_distance(known_faces, captured_encoding)
    best_match_index = np.argmin(face_distances)  # Find the closest match

    if face_distances[best_match_index] < 0.45:  # Adjust threshold (lower = more strict)
        return known_names[best_match_index]
    else:
        print("❌ No close match found.")
        return "Unknown"

def fetch_voter_details(voter_name):
    """Fetches voter details from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT voter_id, voter_name, voter_phone FROM voters WHERE voter_name = ?", (voter_name,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return {"voter_id": result[0], "voter_name": result[1], "phone": result[2]}
    return None

def check_if_voted(voter_id):
    """Checks if the voter ID has already cast their vote."""
    if not os.path.exists(VOTED_VOTERS_FILE):
        return False  # No votes recorded yet

    with open(VOTED_VOTERS_FILE, "r") as file:
        voted_voters = file.read().splitlines()

    return voter_id in voted_voters  # Check ID instead of name

def record_vote(voter_id):
    """Records the voter's ID in voted_voters.txt."""
    with open(VOTED_VOTERS_FILE, "a") as file:
        file.write(voter_id + "\n")

def main():
    """Main function to execute voter verification."""
    known_faces, known_names = load_voter_images()

    if not known_faces:
        print("⚠️ No registered voter images found. Exiting...")
        return

    print("📸 Camera is opening... Look at the camera and blink.")
    captured_frame = capture_image()
    voter_name = recognize_face(captured_frame, known_faces, known_names)

    if voter_name == "Unknown":
        print("❌ Voter not recognized. Access denied.")
        return

    voter_data = fetch_voter_details(voter_name)
    if voter_data:
        voter_id = voter_data['voter_id']

        if check_if_voted(voter_id):
            print(f"⚠️ Voter '{voter_data['voter_name']}' (ID: {voter_id}) has already cast their vote!")
            return

        print(f"✅ Voter Verified: {voter_data['voter_name']} (ID: {voter_id})")
        record_vote(voter_id)  # Save voter ID instead of name
        print(f"📌 Voter ID '{voter_id}' added to voted list.")
    else:
        print("❌ No matching voter found in database.")

if __name__ == "__main__":
    main()
