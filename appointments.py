import sqlite3
from datetime import datetime, timedelta

import patients
import staff
import Logging
connect = sqlite3.connect('database.db')
cursor = connect.cursor()


def bookAppointment(patientID, current_user, presentDate=None):
    staffID = staff.searchStaff()
    if staffID is None:
        print("No staff member selected")
        return
    if presentDate is None:
        date = validateAppointmentDate()
    else:
        date = presentDate
    time = validateAppointmentTime()
    duration = selectDuration()


    excludeAppointmentID = None
    conflict = checkConflict(date, time, duration,staffID,patientID, excludeAppointmentID)
    if conflict != True:
        cursor.execute("""
        INSERT INTO Appointments_Table
        (Appointment_date, Appointment_time, PatientID, StaffID, Duration)
        VALUES (?,?,?,?,?)
        """, (date, time, patientID, staffID, duration))
        connect.commit()
        cursor.execute("""
        SELECT last_insert_rowid()
        """)
        appointmentID = cursor.fetchone()[0]
        Logging.log_action(
            current_user,
            "CREATE_APPOINTMENT",
            f"AppointmentID {appointmentID}, PatientID {patientID}, StaffID {staffID}"
        )
        print("Appointment booked")
        return True
    else:
        return False


def checkConflict(date, time, duration, staffID, patientID, excludeAppointmentID=None):

    bookingStart = datetime.strptime(time, "%H:%M")
    bookingEnd = bookingStart + timedelta(minutes=duration)

    # Staff

    if excludeAppointmentID is None:
        cursor.execute("""
        SELECT Appointment_time, Duration
        FROM Appointments_Table
        WHERE Appointment_date = ?
        AND StaffID = ?
        """, (date, staffID))

    else:
        cursor.execute("""
        SELECT Appointment_time, Duration
        FROM Appointments_Table
        WHERE Appointment_date = ?
        AND StaffID = ?
        AND AppointmentID != ?
        """, (date, staffID, excludeAppointmentID))

    staffAppointments = cursor.fetchall()

    for each in staffAppointments:

        existingStart = datetime.strptime(each[0], "%H:%M")
        existingEnd = existingStart + timedelta(minutes=each[1])

        if bookingStart < existingEnd and bookingEnd > existingStart:
            print("Staff member already booked")
            return True

    # Patient

    if excludeAppointmentID is None:
        cursor.execute("""
        SELECT Appointment_time, Duration
        FROM Appointments_Table
        WHERE Appointment_date = ?
        AND PatientID = ?
        """, (date, patientID))

    else:
        cursor.execute("""
        SELECT Appointment_time, Duration
        FROM Appointments_Table
        WHERE Appointment_date = ?
        AND PatientID = ?
        AND AppointmentID != ?
        """, (date, patientID, excludeAppointmentID))

    patientAppointments = cursor.fetchall()
    for each in patientAppointments:
        existingStart = datetime.strptime(each[0], "%H:%M")
        existingEnd = existingStart + timedelta(minutes=each[1])

        if bookingStart < existingEnd and bookingEnd > existingStart:
            print("Patient already has an appointment at this time")
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

def appointmentsmenu(results, current_user):
    valid = False
    while not valid:
        try:
            choice = int(input(
                "\n1. Cancel Appointment"
                "\n2. Edit Appointment"
                "\n3. Exit\n\n"
                ">> "
            ))

            if choice == 1:
                cancelAppointment(results, current_user)
                valid = True
            elif choice == 2:
                editAppointmentMenu(results, current_user)
                valid = True
            elif choice == 3:
                valid = True
            else:
                print("Not a valid option")
        except ValueError:
            print("Invalid Input")

def editAppointmentMenu(results, current_user):
    valid_ids = []

    for a in results:
        valid_ids.append(a[0])

    valid = False

    while not valid:
        try:
            appointmentID = int(input(
                "Enter Appointment ID: "
            ))

            if appointmentID in valid_ids:
                editAppointment(appointmentID, current_user)
                valid = True

            else:
                print("Invalid ID")

        except ValueError:
            print("Invalid Input")

def editAppointment(appointmentID, current_user):

    cursor.execute("""
    SELECT PatientID
    FROM Appointments_Table
    WHERE AppointmentID = ?
    """, (appointmentID,))

    patientID = cursor.fetchone()[0]
    staffID = staff.searchStaff()
    date = validateAppointmentDate()
    time = validateAppointmentTime()
    duration = selectDuration()
    conflict = checkConflict(
        date,
        time,
        duration,
        staffID,
        patientID,
        appointmentID
    )
    if conflict:
        print("Time slot already booked")

    else:
        confirm = input("Are you sure? ").strip().lower()
        if confirm in ["yes", "y"]:
            try:
                cursor.execute("""
                UPDATE Appointments_Table
                SET Appointment_date = ?,
                    Appointment_time = ?,
                    Duration = ?,
                    StaffID = ?
                WHERE AppointmentID = ?
                """, (date, time, duration, staffID, appointmentID))
                connect.commit()
                Logging.log_action(
                    current_user,
                    "EDIT_APPOINTMENT",
                    f"AppointmentID {appointmentID}, StaffID {staffID}"
                )
                print("Appointment updated")
            except:
                print("Database error")

def searchMenu(current_user):
    valid = False
    while not valid:
        try:
            choice = int(input("1. Show all appointments\n"
                               "2. Search appointment by date\n"
                               "3. Search appointment by patient\n"
                               "4. Exit\n\n"
                               ">>  "))
            if choice == 1:
                viewAllAppointments(current_user)
            elif choice == 2:
                viewAppointmentsbyDate(current_user)
            elif choice == 3:
                viewAppointmentsbyPatient(current_user)
            elif choice == 4:
                valid = True
            else:
                print("Not a valid input")
        except ValueError:
            print("Must be a number")



def fetchAppointments(results,current_user):
    if len(results) == 0:
        print("No appointments found")
        return

    for p in results:
        print(f"ID: {p[0]}"
              f" | Date: {p[1]}"
              f" | Time: {p[2]}"
              f" | PatientID: {p[3]}"
              f" | StaffID: {p[4]}"
              f" | Duration: {p[5]} mins")
    appointmentsmenu(results, current_user)


def viewAllAppointments(current_user):
    cursor.execute("""
    SELECT * FROM Appointments_Table""")
    results = cursor.fetchall()
    fetchAppointments(results, current_user)

def viewAppointmentsbyDate(current_user):
    date = validateAppointmentDate()
    cursor.execute("""
    SELECT * FROM Appointments_Table 
    WHERE Appointment_date = ?""",(date,))
    results = cursor.fetchall()
    fetchAppointments(results, current_user)

def viewAppointmentsbyPatient(current_user):
    PatientID = patients.searchPatient()
    cursor.execute("""
    SELECT * FROM Appointments_Table
    WHERE PatientID = ?""",(PatientID,))
    results = cursor.fetchall()
    fetchAppointments(results, current_user)


def cancelAppointment(results, current_user):
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
                        Logging.log_action(
                            current_user,
                            "DELETE_APPOINTMENT",
                            f"AppointmentID {enteredID}"
                        )
                        print("Deleted successfully")
                        valid = True
                    elif confirm in ["no","n"]:
                        print("Cancelled deletion")
                        break


                else:
                    print("Invalid ID")
        except ValueError:
            print("Invalid Input")




