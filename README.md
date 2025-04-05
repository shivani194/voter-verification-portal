# Face Recognition, OTP, and Voter ID Based Voting System

A secure and intelligent voting system that verifies a voter's identity through **Facial Recognition**, **Phone-based OTP**, and **Voter ID** before allowing them to cast their vote.

## Features

- 📷 Face recognition-based user authentication
- 📱 OTP verification via phone number
- 🆔 Voter ID validation from database
- 🗳️ Vote casting interface with real-time validation
- 🚫 Duplicate voting prevention – once a voter is verified and has voted, they cannot vote again via any method
- 🌐 Language selection for accessibility

## Tech Stack

- **Frontend:** HTML, CSS (inline and internal styling)
- **Backend:** Python, Flask
- **Face Recognition:** dlib, OpenCV
- **OTP Service:** Custom script (can integrate APIs like Twilio)
- **Database:** Python dictionary or SQLite for storing voter data

## How to Run Locally

1. Clone the Reposiitory:
   git clone https://github.com/yourusername/voter-verification-portal.git
   cd voter-verification-portal

2. Install required dependencies:
   pip install -r requirements.txt

3. Set up your data:
  Add voter face images to the /voter_images directory.
  Add voter names and voter IDs in database.py.

 4.Run the Flask application:
  python app.py

5. Access the Systen in your browser:
  http://localhost:5000

## Security Considerations

- The system cross-verifies the voter using facial recognition, voter ID, and OTP for maximum authenticity.

- Once a voter has been verified and has cast their vote, they are marked as already voted.

- Even if the voter tries to verify again using any method (face, OTP, or ID), the system will detect duplication and deny access.

- OTPs are time-sensitive and single-use only

   
