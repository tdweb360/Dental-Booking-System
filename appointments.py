import sqlite3
from datetime import datetime, timedelta

connect = sqlite3.connect('database.db')
cursor = connect.cursor()


def bookAppointment(patientID):
    date = validateAppointmentDate()
    time = validateAppointmentTime()
    duration = selectDuration()
    staffID = 1

    # check for conflicts
    conflict = checkConflict(date, time, duration)
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


def checkConflict(date, time, duration):
    cursor.execute("""
    SELECT Appointment_time, Duration
    FROM Appointments_Table
    WHERE Appointment_date = ?
    """, (date,))

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