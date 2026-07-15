import sqlite3
connect = sqlite3.connect('database.db')
cursor = connect.cursor()

cursor.execute("PRAGMA foreign_keys = ON")

## patients table ##
cursor.execute("""
CREATE TABLE IF NOT EXISTS Patients_Table(
    PatientID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT,
    Surname TEXT,
    Date_of_birth TEXT,
    Phone_Num TEXT
)
               """)

## Appointments table ##
cursor.execute("""
CREATE TABLE IF NOT EXISTS Appointments_Table (
    AppointmentID INTEGER PRIMARY KEY AUTOINCREMENT,
    Appointment_date TEXT,
    Appointment_time TEXT,
    PatientID INTEGER,
    StaffID INTEGER,
    Duration INTEGER,
    FOREIGN KEY (PatientID) REFERENCES Patients_Table(PatientID),
    FOREIGN KEY (StaffID) REFERENCES Staff_Table(StaffID)
)
                """)

## Staff Table ##
cursor.execute("""
CREATE TABLE IF NOT EXISTS Staff_Table(
    StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT,
    Surname TEXT,
    Username TEXT UNIQUE,
    Password_Hash TEXT,
    Staff_Role TEXT
)
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS AuditLog (
    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Action TEXT NOT NULL,
    Details TEXT,
    Timestamp TEXT NOT NULL
)
                """)


cursor.execute("""
CREATE TABLE IF NOT EXISTS Recall_Table(
    RecallID INTEGER PRIMARY KEY AUTOINCREMENT,
    PatientID INTEGER NOT NULL,
    AppointmentID INTEGER NOT NULL,
    SuggestedDate TEXT NOT NULL,
    Priority INTEGER NOT NULL,
    Completed INTEGER DEFAULT 0,
    FOREIGN KEY(PatientID) REFERENCES Patients_Table(PatientID),
    FOREIGN KEY(AppointmentID) REFERENCES Appointments_Table(AppointmentID)
)
""")

connect.commit()


connect.commit()
connect.commit()
connect.close()
