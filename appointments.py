import sqlite3
from datetime import datetime
import re

def bookAppointment(patientID):
    date = validateAppointmentDate()
    time = validateAppointmentTime()

def validateAppointmentDate():
    valid = False
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d %m %Y", "%d.%m.%Y"]
    while not valid:
        date_of_appointment = input("Enter date of appointment (DD/MM/YYYY): ").strip()
        date = 0
        for x in formats:
            try:
                today = datetime.today()
                date = datetime.strptime(date_of_appointment, x)
                if date < today:
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
        time_of_appointment = input("Enter appointment time (HH:MM)").strip()
        try:
            time = datetime.strptime(time_of_appointment, "%H:%M")
            if not (9 <= time.hour < 17):
                print("Appointment must be between 9AM and 5PM")
            elif time.minute not in [0,15,30,45]:
                print("Appointments must be on a 15 minute interval")
            else:
                valid = True
        except ValueError:
            print("Invalid time format, use HH:MM")
    return time.strftime("%H:%M")