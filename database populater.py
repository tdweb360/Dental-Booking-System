# wipes patients, appointments and recalls, then fills the database with
# test data that is always in the FUTURE (relative to the day you run it)
# staff accounts are NOT deleted, so you can still log in

import sqlite3
import random
from datetime import datetime, timedelta

# ---------- settings you can change ----------
NUM_PATIENTS = 50
NUM_APPOINTMENTS = 100
DAYS_AHEAD = 14          # appointments spread over the next 14 weekdays
# ---------------------------------------------

connect = sqlite3.connect("database.db")
cursor = connect.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

# 1) get the real staff IDs so appointments only use staff that exist
cursor.execute("SELECT StaffID FROM Staff_Table")
staffIDs = [row[0] for row in cursor.fetchall()]
if len(staffIDs) == 0:
    print("No staff in the database - run the main program once to create a manager first")
    connect.close()
    raise SystemExit

# 2) wipe - ORDER MATTERS: tables that reference others must be emptied first
cursor.execute("DELETE FROM Recall_Table")
cursor.execute("DELETE FROM Appointments_Table")
cursor.execute("DELETE FROM Patients_Table")
# reset the AUTOINCREMENT counters so IDs start from 1 again
for table in ["Recall_Table", "Appointments_Table", "Patients_Table"]:
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))
# uncomment the next line if you also want an empty audit log
cursor.execute("DELETE FROM AuditLog")

# 3) patients
firstNames = ["Tom","Sarah","Emma","Jake","Olivia","James","Sophie","Ben",
              "Lucy","Daniel","Mia","Harry","Grace","Charlie","Amelia"]
surnames = ["Smith","Jones","Brown","Taylor","Wilson","Johnson","Evans",
            "Thomas","Roberts","Walker","White","Hall","Davies","Lewis"]

for i in range(NUM_PATIENTS):
    dob = f"{random.randint(1950, 2015):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    phone = "07" + "".join(str(random.randint(0, 9)) for _ in range(9))
    cursor.execute("""
    INSERT INTO Patients_Table (FirstName, Surname, Date_of_birth, Phone_Num)
    VALUES (?,?,?,?)
    """, (random.choice(firstNames), random.choice(surnames), dob, phone))

# 4) appointments - list of future weekdays starting from tomorrow
dates = []
day = datetime.today() + timedelta(days=1)
while len(dates) < DAYS_AHEAD:
    if day.weekday() < 5:                      # 0-4 = Monday-Friday
        dates.append(day.strftime("%Y-%m-%d"))
    day += timedelta(days=1)

# remember what has been booked so we can avoid overlaps
# key = (person type, ID, date) -> list of (start, end) in minutes since midnight
booked = {}

def isFree(key, start, end):
    for (s, e) in booked.get(key, []):
        if start < e and end > s:              # same overlap test as your Appointment class
            return False
    return True

created = 0
attempts = 0
while created < NUM_APPOINTMENTS and attempts < NUM_APPOINTMENTS * 20:
    attempts += 1
    date = random.choice(dates)
    duration = random.choice([15, 30, 45, 60])
    start = random.choice(range(9 * 60, 17 * 60, 15))   # 09:00 to 16:45
    end = start + duration
    if end > 17 * 60:                          # must finish by 17:00
        continue
    patientID = random.randint(1, NUM_PATIENTS)
    staffID = random.choice(staffIDs)
    staffKey = ("staff", staffID, date)
    patientKey = ("patient", patientID, date)
    if not (isFree(staffKey, start, end) and isFree(patientKey, start, end)):
        continue
    booked.setdefault(staffKey, []).append((start, end))
    booked.setdefault(patientKey, []).append((start, end))
    time = f"{start // 60:02d}:{start % 60:02d}"
    cursor.execute("""
    INSERT INTO Appointments_Table
    (Appointment_date, Appointment_time, PatientID, StaffID, Duration)
    VALUES (?,?,?,?,?)
    """, (date, time, patientID, staffID, duration))
    created += 1

connect.commit()
connect.close()
print(f"Done: {NUM_PATIENTS} patients and {created} future appointments created")