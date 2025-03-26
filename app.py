from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    choice = request.form.get('verification_method')

    if choice == 'face':
        subprocess.run(['python', 'face.py'])  # Runs face verification
    elif choice == 'otp':
        subprocess.run(['python', 'otp.py'])  # Runs OTP verification

    return redirect(url_for('home'))  # Redirect to home after running script

if __name__ == '__main__':
    app.run(debug=True)
