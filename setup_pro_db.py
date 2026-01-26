import sqlite3

def setup():
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    # 1. Clear old data
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS doctors")
    cursor.execute("DROP TABLE IF EXISTS appointments")
    cursor.execute("DROP TABLE IF EXISTS prescriptions")

    # 2. Create complex schema
    cursor.execute("""
        CREATE TABLE patients (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            age INTEGER, 
            gender TEXT,
            blood_type TEXT
        )""")
    
    cursor.execute("""
        CREATE TABLE doctors (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            specialty TEXT,
            experience_years INTEGER
        )""")
    
    cursor.execute("""
        CREATE TABLE appointments (
            id INTEGER PRIMARY KEY, 
            patient_id INTEGER, 
            doctor_id INTEGER, 
            visit_date DATE,
            reason TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )""")
    
    cursor.execute("""
        CREATE TABLE prescriptions (
            id INTEGER PRIMARY KEY,
            appointment_id INTEGER,
            medication_name TEXT,
            dosage TEXT,
            FOREIGN KEY(appointment_id) REFERENCES appointments(id)
        )""")

    # 3. Seed data
    cursor.executemany("INSERT INTO patients VALUES (?,?,?,?,?)", [
        (1, 'Daniel', 28, 'M', 'O+'), (2, 'Sarah', 34, 'F', 'A-'), (3, 'James', 45, 'M', 'B+'), (4, 'Linda', 22, 'F', 'O-')
    ])
    
    cursor.executemany("INSERT INTO doctors VALUES (?,?,?,?)", [
        (1, 'Dr. Smith', 'Cardiology', 15), (2, 'Dr. Adams', 'Pediatrics', 8), (3, 'Dr. Okoro', 'General Medicine', 12)
    ])
    
    cursor.executemany("INSERT INTO appointments VALUES (?,?,?,?,?)", [
        (1, 1, 3, '2026-01-20', 'Malaria Checkup'), (2, 2, 1, '2026-01-22', 'Heart Palpitations'), (3, 3, 3, '2026-01-25', 'General Wellness')
    ])

    cursor.executemany("INSERT INTO prescriptions VALUES (?,?,?,?)", [
        (1, 1, 'Artemether', '80mg'), (2, 2, 'Aspirin', '100mg')
    ])
    
    conn.commit()
    conn.close()
    print("✅ hospital.db boosted with 4 tables and relational data!")

if __name__ == "__main__":
    setup()
