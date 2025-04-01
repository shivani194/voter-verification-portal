from flask import Flask, render_template, request, session, jsonify
import sqlite3
from face import capture_image, recognize_face, fetch_voter_details, load_voter_images
from otp import check_voter, generate_otp, send_otp
from database import get_voter_by_phone

DB_PATH = "voters.db"
VOTED_VOTERS_FILE = "voted_voters.txt"

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session storage

def has_voted(voter_id):
    """Checks if the voter has already voted."""
    try:
        with open(VOTED_VOTERS_FILE, "r") as file:
            voted_voters = file.readlines()
            return any(voter_id in line for line in voted_voters)
    except FileNotFoundError:
        return False


def mark_voter_as_voted(voter_name, voter_id, phone):
    """Marks a voter as voted by adding them to voted_voters.txt."""
    with open(VOTED_VOTERS_FILE, "a") as file:
        file.write(f"{voter_name},{voter_id},{phone}\n")



@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route('/verify', methods=['POST'])
def verify():
    method = request.form.get('verification_method')

    if method == "face":
        known_faces, known_names = load_voter_images()  # Load known faces first
        captured_frame = capture_image()
        voter_name = recognize_face(captured_frame, known_faces, known_names)

        if voter_name != "Unknown":
            voter_data = fetch_voter_details(voter_name)
            if voter_data:
                voter_id = voter_data["voter_id"]

                if has_voted(voter_id):
                    return render_template('result.html', result="Voter already cast their vote ❌")

                mark_voter_as_voted(voter_name, voter_id, voter_data["phone"])
                return render_template('result.html', result=f"Voter Verified ✅<br>Name: {voter_name}<br>Voter ID: {voter_id}")
        return render_template('result.html', result="Voter Not Found ❌")

    elif method == "otp":
        return render_template('otp_input.html')

    elif method == "voter_id":
        return render_template('voter_id_verification.html')

    return jsonify({"status": "error", "message": "Invalid verification method"})



@app.route('/send_otp', methods=['POST'])
def send_otp_request():
    phone = request.form.get('phone')
    voter = get_voter_by_phone(phone)

    if voter:
        voter_id = voter[0]
        if has_voted(voter_id):
            return render_template('result.html', result="Voter already cast their vote ❌")

        otp = generate_otp()
        session['otp'] = str(otp)
        session['voter_id'] = voter_id
        session['voter_name'] = voter[1]
        session['phone'] = phone

        print(f"Generated OTP: {otp}")  # Debugging

        send_otp(phone, otp)  # Sends OTP to the user's phone
        return render_template('otp_verify.html', phone=phone)

    return render_template('result.html', result="Voter Not Found ❌")

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = str(request.form.get('otp'))
    correct_otp = str(session.get('otp'))

    voter_name = session.get('voter_name')
    voter_id = session.get('voter_id')
    phone = session.get('phone')

    if entered_otp == correct_otp:
        if has_voted(voter_id):
            return render_template('result.html', result="Voter already cast their vote ❌")

        mark_voter_as_voted(voter_name, voter_id, phone)
        return render_template('result.html', result=f"Voter Verified ✅<br>Name: {voter_name}<br>Voter ID: {voter_id}")
    else:
        return render_template('result.html', result="Invalid OTP ❌")


def verify_voter_id(voter_id):
    """Checks if the voter ID exists in the database and verifies them."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT voter_name, voter_id, phone FROM voters WHERE voter_id = ?", (voter_id,))
    voter = cursor.fetchone()
    conn.close()

    if voter:
        voter_name, voter_id, phone = voter

        if has_voted(voter_id):
            return {"status": "error", "message": "Voter already cast their vote ❌"}

        mark_voter_as_voted(voter_name, voter_id, phone)
        return {"status": "success", "message": "Voter Verified ✅", "name": voter_name, "voter_id": voter_id}
    else:
        return {"status": "error", "message": "No matching voter found ❌"}

@app.route("/verify_id", methods=["POST"])
def verify_id():
    data = request.form  
    method = data.get("method")  

    if method == "voter_id":
        voter_id = data.get("voter_id")

        if not voter_id:
            return render_template("result.html", result="Voter ID is required ❌")

        # Check if voter has already voted
        if has_voted(voter_id):
            return render_template("result.html", result="Voter already cast their vote ❌")

        # Verify voter ID
        voter_data = verify_voter_id(voter_id)
        
        if voter_data["status"] == "success":
            voter_name = voter_data["name"]
            phone = voter_data.get("voter_phone", "N/A")  # Handle missing phone number

            # Mark voter as voted
            mark_as_voted(voter_name, voter_id, phone)

            return render_template("result.html", result=f"Voter Verified ✅<br>Name: {voter_name}<br>Voter ID: {voter_id}")
        else:
            return render_template("result.html", result="Voter Not Found ❌")

    return render_template("result.html", result="Invalid verification method ❌")



if __name__ == '__main__':
    app.run(debug=True)
