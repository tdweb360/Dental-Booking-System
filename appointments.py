import sqlite3
from datetime import datetime, timedelta

import patients
import staff
connect = sqlite3.connect('database.db')
cursor = connect.cursor()


def bookAppointment(patientID):
    staffID = staff.searchStaff()
    date = validateAppointmentDate()
    time = validateAppointmentTime()
    duration = selectDuration()

    # check for conflicts
    conflict = checkConflict(date, time, duration,staffID)
    if conflict == True:
        print("Time slot already booked")
    else:
        cursor.execute("""
        INSERT INTO Appointments_Table
        (Appointment_date, Appointment_time, PatientID, StaffID, Duration)
        VALUES (?,?,?,?,?)
        """, (date, time, patientID, staffID, duration))

        connect.commit()
        print("Appointment booked")


def checkConflict(date, time, duration,staffID):
    cursor.execute("""
    SELECT Appointment_time, Duration
    FROM Appointments_Table
    WHERE Appointment_date = ?
    AND StaffID = ?
    """, (date, staffID))

    existing = cursor.fetchall()
    bookingStart = datetime.strptime(time, "%H:%M")
    bookingEnd = datetime.strptime(time, "%H:%M") + timedelta(minutes=duration)
    for each in existing:
        existingStart = datetime.strptime(each[0], "%H:%M")
        existingEnd = datetime.strptime(each[0], "%H:%M") + timedelta(minutes=each[1])
        if bookingStart < existingEnd and bookingEnd > existingStart:
            print("Appointments Conflict")
            return True
    return False


def validateAppointmentDate():
    valid = False
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d %m %Y", "%d.%m.%Y"]

    while not valid:
        date_input = input("Enter date of appointment (DD/MM/YYYY): ").strip()

        for x in formats:
            try:
                today = datetime.today()
                date = datetime.strptime(date_input, x)

                if date.date() < today.date():
                    print("Cannot be in past")
                else:
                    valid = True
                    break

            except ValueError:
                continue

        if valid:
            return date.strftime("%Y-%m-%d")
        else:
            print("Error, incorrect format. Try DD/MM/YYYY")


def validateAppointmentTime():
    valid = False

    while not valid:
        time_input = input("Enter appointment time (HH:MM): ").strip()

        try:
            time = datetime.strptime(time_input, "%H:%M")

            if not (9 <= time.hour < 17):
                print("Appointment must be between 9AM and 5PM")

            elif time.minute not in [0, 15, 30, 45]:
                print("Appointments must be on a 15 minute interval")

            else:
                valid = True

        except ValueError:
            print("Invalid time format, use HH:MM")

    return time.strftime("%H:%M")


def selectDuration():
    valid = False

    while not valid:
        try:
            duration = int(input("Enter duration (15, 30, 45, 60): "))

            if duration in [15, 30, 45, 60]:
                return duration
            else:
                print("Invalid duration")

        except ValueError:
            print("Invalid input")

def searchMenu():
    valid = False
    while not valid:
        try:
            choice = int(input("1. Show all appointments\n"
                               "2. Search appointment by date\n"
                               "3. Search appointment by patient\n"
                               "4. Exit\n\n"
                               ">>  "))
            if choice == 1:
                viewAllAppointments()
            elif choice == 2:
                viewAppointmentsbyDate()
            elif choice == 3:
                viewAppointmentsbyPatient()
            elif choice == 4:
                valid = True
            else:
                print("Not a valid input")
        except ValueError:
            print("Must be a number")



def fetchAppointments(results):
    if len(results) == 0:
        print("No appointments found")
    else:
        for p in results:
            print(f"ID: {p[0]}"
                  f" | Date: {p[1]}"
                  f" | Time: {p[2]}"
                  f" | PatientID: {p[3]}"
                  f" | StaffID: {p[4]}"
                  f" | Duration: {p[5]} mins")
    choice = input("Do you want to cancel an appointment?").strip().lower()
    if choice in ["yes","y"]:
        cancelAppointment(results)


def viewAllAppointments():
    cursor.execute("""
    SELECT * FROM Appointments_Table""")
    results = cursor.fetchall()
    fetchAppointments(results)

def viewAppointmentsbyDate():
    date = validateAppointmentDate()
    cursor.execute("""
    SELECT * FROM Appointments_Table 
    WHERE Appointment_date = ?""",(date,))
    results = cursor.fetchall()
    fetchAppointments(results)

def viewAppointmentsbyPatient():
    PatientID = patients.searchPatient()
    cursor.execute("""
    SELECT * FROM Appointments_Table
    WHERE PatientID = ?""",(PatientID,))
    results = cursor.fetchall()
    fetchAppointments(results)


def cancelAppointment(results):
    valid = False
    while not valid:
        try:
            enteredID = int(input("Enter appointment ID"))
            valid_ids = []
            if len(results) == 0:
                print("No appointments found")
            else:
                for a in results:
                    valid_ids.append(a[0])
                if enteredID in valid_ids:
                    confirm = input("Are you sure?").strip().lower()
                    if confirm in ["yes","y"]:
                        cursor.execute("""
                        DELETE FROM Appointments_Table
                        WHERE AppointmentID = ?
                        """,(enteredID,))
                        connect.commit()
                        print("Deleted successfully")
                        valid = True
                    elif confirm in ["no","n"]:
                        print("Cancelled")
                        break


                else:
                    print("Invalid ID")
        except ValueError:
            print("Invalid Input")