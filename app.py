from flask import Flask, render_template, request, session, jsonify
import sqlite3
from face import capture_image, recognize_face, fetch_voter_details, load_voter_images
from otp import check_voter, generate_otp, send_otp
from database import get_voter_by_phone

DB_PATH = "voters.db"

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for session storage

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route('/verify', methods=['POST'])
def verify():
    method = request.form.get('verification_method')
    if method == "face":
        known_faces, known_names = load_voter_images()
        captured_frame = capture_image()
        voter_name = recognize_face(captured_frame, known_faces, known_names)
        
        if voter_name != "Unknown":
            voter_data = fetch_voter_details(voter_name)
            if voter_data:
                return render_template('result.html', result=f"Voter Verified ✅<br>Name: {voter_data['voter_name']}<br>Voter ID: {voter_data['voter_id']}")
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
        otp = generate_otp()
        session['otp'] = str(otp)
        session['voter_id'] = voter[0]
        session['voter_name'] = voter[1]
        
        print(f"Generated OTP: {otp}")
        send_otp(phone, otp)
        return render_template('otp_verify.html', phone=phone)
    
    return render_template('result.html', result="Voter Not Found ❌")

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = str(request.form.get('otp'))
    correct_otp = str(session.get('otp'))
    
    print(f"Entered OTP: {entered_otp}, Stored OTP: {correct_otp}")
    
    voter_name = session.get('voter_name')
    voter_id = session.get('voter_id')

    if entered_otp == correct_otp:
        return render_template('result.html', result=f"Voter Verified ✅<br>Name: {voter_name}<br>Voter ID: {voter_id}")
    else:
        return render_template('result.html', result="Invalid OTP ❌")


@app.route('/verify_voter_id', methods=['POST'])
def verify_voter_id(voter_id):
    """Checks if the voter ID exists in the database and returns voter details."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT voter_name, voter_id FROM voters WHERE voter_id = ?", (voter_id,))
    voter = cursor.fetchone()

    conn.close()

    if voter:
        return {"status": "success", "message": "Voter Found", "name": voter[0], "voter_id": voter[1]}
    else:
        return {"status": "error", "message": "No matching voter found"}

@app.route("/verify_id", methods=["POST"])
def verify_id():
    data = request.form  
    method = data.get("method")  

    if method == "voter_id":
        voter_id = data.get("voter_id")

        if not voter_id:
            return render_template("result.html", result="Voter ID is required ❌")

        voter_data = verify_voter_id(voter_id)
        
        if voter_data["status"] == "success":
            return render_template("result.html", result=f"Voter Verified ✅<br>Name: {voter_data['name']}<br>Voter ID: {voter_data['voter_id']}")
        else:
            return render_template("result.html", result="Voter Not Found ❌")

    return render_template("result.html", result="Invalid verification method ❌")


if __name__ == '__main__':
    app.run(debug=True)
