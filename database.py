import sqlite3
connect = sqlite3.connect('database.db')
cursor = connect.cursor()


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
    FOREIGN KEY (PatientID) REFERENCES Patients_Table(PatientID),
    FOREIGN KEY (StaffID) REFERENCES Staff_Table(StaffID)
)
                """)

## Staff Table ##
cursor.execute("""
CREATE TABLE IF NOT EXISTS Staff_Table(
    StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT,
    Password_Hash TEXT,
    Staff_Role TEXT
)
               """)

connect.commit()
connect.close()
