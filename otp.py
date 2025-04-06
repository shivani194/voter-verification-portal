import random
import sqlite3
from twilio.rest import Client

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone, otp):
    TWILIO_ACCOUNT_SID = "your_acc_sid"
    TWILIO_AUTH_TOKEN = "your_auth_token"
    TWILIO_PHONE_NUMBER = "your-twilio_number"
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your OTP is: {otp}. It is valid for 30 seconds.",
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )
    print(f"OTP sent successfully to {phone}.")

def check_voter(phone):
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    cursor.execute("SELECT voter_name, voter_id FROM voters WHERE voter_phone = ?", (phone,))
    voter = cursor.fetchone()
    conn.close()
    return voter

def has_already_voted(voter_id):
    try:
        with open("voted_voters.txt", "r") as file:
            voted_voters = file.read().splitlines()
        return voter_id in voted_voters
    except FileNotFoundError:
        return False

def mark_as_voted(voter_id):
    with open("voted_voters.txt", "a") as file:
        file.write(voter_id + "\n")

def main():
    phone = input("Enter your phone number: ")
    voter = check_voter(phone)
    
    if not voter:
        print("No voter record found for this phone number.")
        return
    
    voter_name, voter_id = voter
    
    if has_already_voted(voter_id):
        print("Vote already casted by the voter.")
        return
    
    otp = generate_otp()
    send_otp(phone, otp)
    
    user_otp = input("Enter the OTP received: ")
    
    if user_otp == otp:
        print("OTP Verified!")
        print(f"Voter Found!\nName: {voter_name}\nVoter ID: {voter_id}")
        mark_as_voted(voter_id)
    else:
        print("Invalid OTP. Verification failed.")

if __name__ == "__main__":
    main()
