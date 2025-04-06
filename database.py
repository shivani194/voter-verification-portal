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

"""def insert_voters():
    voters = [
        
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

"""

def get_voter_by_phone(phone):
    conn = sqlite3.connect("voters.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT voter_id, voter_name FROM voters WHERE voter_phone = ?", (phone,))
    voter = cursor.fetchone()
    
    conn.close()
    return voter




if __name__ == "__main__":
    init_db()
    
    
    
