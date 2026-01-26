import sqlite3

def setup():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # Create sample tables
    cursor.execute("CREATE TABLE patients (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, condition TEXT)")
    cursor.execute("CREATE TABLE appointments (id INTEGER PRIMARY KEY, patient_id INTEGER, doctor TEXT, date TEXT)")
    
    # Insert sample data
    patients = [
        (1, 'Daniel', 28, 'Malaria'),
        (2, 'Sarah', 34, 'Flu'),
        (3, 'James', 45, 'Hypertension')
    ]
    cursor.executemany("INSERT INTO patients VALUES (?,?,?,?)", patients)
    
    conn.commit()
    conn.close()
    print("✅ Created hospital.db with sample patient data.")

if __name__ == "__main__":
    setup()
