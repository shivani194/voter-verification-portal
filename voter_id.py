import sqlite3

DB_PATH = "voters.db"  # Database path

def verify_voter_id(voter_id):
    """Checks if a given voter ID exists in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT voter_name, voter_id FROM voters WHERE voter_id = ?", (voter_id,))
    voter = cursor.fetchone()

    conn.close()

    if voter:
        return f"✅ Voter Found!\nName: {voter[0]}\nVoter ID: {voter[1]}"
    else:
        return "❌ No matching voter found in the database."

if __name__ == "__main__":
    voter_id = input("Enter Voter ID: ")
    print(verify_voter_id(voter_id))
