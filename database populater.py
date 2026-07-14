import sqlite3
# from datetime import datetime
# import random
#
# connect = sqlite3.connect('database.db')
# cursor = connect.cursor()
#
# firstnames = ["Tom", "Dan", "Alex", "Sam", "Jamie", "Chris", "Taylor"]
# surnames = ["Smith", "Brown", "Webster", "Jones", "Taylor", "Wilson"]
#
# for i in range(20):  # creates 20 patients
#     firstname = random.choice(firstnames)
#     surname = random.choice(surnames)
#
#     # random date of birth
#     year = random.randint(1970, 2010)
#     month = random.randint(1, 12)
#     day = random.randint(1, 28)  # safe so no invalid dates
#
#     date_of_birth = f"{year:04d}-{month:02d}-{day:02d}"
#
#     # random UK-style phone number
#     phone = "07" + "".join(str(random.randint(0,9)) for _ in range(9))
#
#
#     cursor.execute("""
#     INSERT INTO Patients_Table (FirstName, Surname, Date_of_birth, Phone_Num)
#     VALUES (?, ?, ?, ?)
#     """, (firstname, surname, date_of_birth, phone))
#
# connect.commit()
# connect.close()
#
# print("✅ Database populated with test patients")
# import sqlite3
# import random
#
connect = sqlite3.connect('database.db')
cursor = connect.cursor()
#
# # sample times (15-minute intervals)
# times = [
#     "09:00", "09:15", "09:30", "09:45",
#     "10:00", "10:15", "10:30", "10:45",
#     "11:00", "11:15", "11:30", "11:45",
#     "13:00", "13:15", "13:30", "13:45",
#     "14:00", "14:15", "14:30", "14:45",
#     "15:00", "15:15", "15:30", "15:45",
#     "16:00", "16:15", "16:30"
# ]
#
# durations = [15, 30, 45, 60]
#
# # example dates
# dates = [
#     "2026-09-18",
#     "2026-09-19",
#     "2026-09-20"
# ]
#
# for i in range(20):  # creates 20 appointments
#     date = random.choice(dates)
#     time = random.choice(times)
#     duration = random.choice(durations)
#
#     patientID = random.randint(1, 10)  # assumes you have patients
#     staffID = 1
#
#     try:
#         cursor.execute("""
#         INSERT INTO Appointments_Table
#         (Appointment_date, Appointment_time, PatientID, StaffID, Duration)
#         VALUES (?,?,?,?,?)
#         """, (date, time, patientID, staffID, duration))
#     except:
#         pass  # ignore duplicates/conflicts in filler
#
# connect.commit()
# connect.close()
#
# print("✅ Appointments table populated")

cursor.execute("DELETE FROM Staff_Table")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='Staff_Table'")
connect.commit()