import sqlite3

def init_db():
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS voters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        voter_name TEXT NOT NULL,
                        voter_id TEXT UNIQUE NOT NULL,
                        voter_phone TEXT UNIQUE NOT NULL)''')
    conn.commit()
    conn.close()

def insert_voters():
    voters = [
        ("Shivani", "VOTER123", "+918010254687"),
        ("Pracheta", "VOTER111", "+919322509193"),
        ("Aishwarya", "VOTER127", "+917887555776"),
        ("Shivani Dahrmjidnyasu", "VOTER0194", "+918010254687"),
        ("Samiksha Kale", "VOTER1605", "+918108471605"),
    ]
    
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    
    for voter in voters:
        try:
            cursor.execute("INSERT INTO voters (voter_name, voter_id, voter_phone) VALUES (?, ?, ?)", voter)
        except sqlite3.IntegrityError:
            print(f"Voter {voter[1]} already exists.")
    
    conn.commit()
    conn.close()
    print("Voter data inserted successfully.")

def update_voter_phone(voter_id, new_phone):
    """Updates the phone number of a voter identified by voter_id."""
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE voters SET voter_phone = ? WHERE voter_id = ?", (new_phone, voter_id))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"✅ Phone number updated for voter ID {voter_id}.")
    else:
        print(f"⚠️ No voter found with ID {voter_id}.")
    
    conn.close()

update_voter_phone("VOTER127", "+917887555776")  # Example usage

def update_voter_name(voter_id, new_name):
    """Updates the voter name based on voter_id."""
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE voters SET voter_name = ? WHERE voter_id = ?", (new_name, voter_id))
    conn.commit()

    if cursor.rowcount > 0:
        print(f"✅ Voter name updated for voter ID {voter_id}.")
    else:
        print(f"⚠️ No voter found with ID {voter_id}.")
    
    conn.close()

update_voter_name("VOTER0194", "Shivani Dharmjidnyasu")
update_voter_name("VOTER111", "Pracheta Kadam") 
update_voter_name("VOTER127", "Aishwarya Kale")  # Example usage
 # Example usage
  # Example usage




if __name__ == "__main__":
    init_db()
    insert_voters()
    print("Database initialized and voters inserted.")
