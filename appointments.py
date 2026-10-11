
# file manages all appointment logic and SQL queries related to appointments

import sqlite3
from datetime import datetime, timedelta

import patients
import staff
import Logging
connect = sqlite3.connect('database.db')
cursor = connect.cursor()
cursor.execute("PRAGMA foreign_keys = ON")


def createAppointment(patientID,staffID,date,time,duration,current_user):
    if not validateAppointmentDate(date):
        return "INVALID DATE"
    if not validateAppointmentTime(
            time,
            duration):
        return "INVALID TIME"
    date = datetime.strptime(date,"%d/%m/%Y").strftime("%Y-%m-%d")

    conflict = checkConflict(date,time,duration,staffID,patientID)
    if conflict:
        return "CONFLICT"
    cursor.execute("""
    INSERT INTO Appointments_Table
    (Appointment_date, Appointment_time, PatientID, StaffID, Duration)
    VALUES (?,?,?,?,?)
    """, (date, time, patientID, staffID, duration))
    connect.commit()
    Logging.log_action(current_user,"CREATE_APPOINTMENT",f"PatientID {patientID}, StaffID {staffID}")
    return "SUCCESS"




def checkConflict(date, time, duration, staffID, patientID, excludeAppointmentID=None):

    bookingStart = datetime.strptime(time, "%H:%M")
    bookingEnd = bookingStart + timedelta(minutes=duration)

    #s
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
            return True

    #p
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
            return True
    return False






def editAppointment(appointmentID,date,time,duration,patientID, staffID,current_user):
    if not validateAppointmentDate(date):
        return "INVALID DATE"
    dbDate = datetime.strptime(date,"%d/%m/%Y").strftime("%Y-%m-%d")
    if not validateAppointmentTime(time, duration):
        return "INVALID TIME"
    conflict = checkConflict(dbDate,time,duration,staffID,patientID,appointmentID)

    if conflict:
        return "CONFLICT"
    else:
        return editAppointmentSQL(appointmentID,dbDate,time,duration,patientID,staffID,current_user)

def editAppointmentSQL(appointmentID,date,time,duration,patientID, staffID, current_user):
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
            f"AppointmentID {appointmentID}, StaffID {staffID}")
        return "SUCCESSFUL"
    except:
        return "UNSUCCESSFUL"


def deleteAppointment(appointmentID,current_user):
    cursor.execute("""
    DELETE FROM Appointments_Table
    WHERE AppointmentID = ?
    """, (appointmentID,))
    connect.commit()
    Logging.log_action(
        current_user,
        "DELETE_APPOINTMENT",
        f"AppointmentID {appointmentID}")
    return True



def validateAppointmentDate(date):
    try:
        date = datetime.strptime(date, "%d/%m/%Y")
        if date.date() < datetime.today().date():
            return False
        return True
    except ValueError:
        return False

def validateAppointmentTime(time, duration):
    try:
        time = datetime.strptime(time, "%H:%M")
        endTime = time + timedelta(minutes=duration)
        if not (9 <= time.hour < 17):
            return False
        if time.minute not in [0, 15, 30, 45]:
            return False
        if endTime > datetime.strptime("17:00", "%H:%M"):
            return False
        return True
    except ValueError:
        return False

def getAppointmentsByDate(date, staffID):
    date = datetime.strptime(date,"%d/%m/%Y").strftime("%Y-%m-%d")
    cursor.execute("""
    SELECT Appointment_time, Duration
    FROM Appointments_Table
    WHERE Appointment_date = ?
    AND StaffID = ?
    ORDER BY Appointment_time
    """, (date, staffID))
    return cursor.fetchall()

def getAppointmentsByDateAndStaff(date,staffID):

    date = datetime.strptime(
        date,
        "%d/%m/%Y"
    ).strftime("%Y-%m-%d")
    cursor.execute("""
    SELECT Appointment_time, Duration
    FROM Appointments_Table
    WHERE Appointment_date = ?
    AND StaffID = ?
    ORDER BY Appointment_time
    """, (date, staffID))
    Results = cursor.fetchall()

    return Results

def getAllAppointments():

    cursor.execute("""
    SELECT
        A.AppointmentID,
        A.Appointment_date,
        A.Appointment_time,
        P.FirstName || ' ' || P.Surname AS PatientName,
        S.FirstName || ' ' || S.Surname AS StaffName,
        A.Duration

    FROM Appointments_Table A
    INNER JOIN Patients_Table P
        ON A.PatientID = P.PatientID
    INNER JOIN Staff_Table S
        ON A.StaffID = S.StaffID
    ORDER BY
        A.Appointment_date,
        A.Appointment_time
    """)
    return cursor.fetchall()

def searchAppointments(patient, date):
    if date != "":
        try:
            date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return []
    cursor.execute("""
    SELECT
        A.AppointmentID,
        A.Appointment_date,
        A.Appointment_time,
        P.FirstName || ' ' || P.Surname AS PatientName,
        S.FirstName || ' ' || S.Surname AS StaffName,
        A.Duration
    FROM Appointments_Table A
    INNER JOIN Patients_Table P
        ON A.PatientID = P.PatientID
    INNER JOIN Staff_Table S
        ON A.StaffID = S.StaffID
    WHERE
        (P.FirstName LIKE ?
        OR P.Surname LIKE ?)
        AND A.Appointment_date LIKE ?

    ORDER BY
        A.Appointment_date,
        A.Appointment_time
    """, (f"%{patient}%",f"%{patient}%",f"%{date}%"))
    return cursor.fetchall()

def getAppointmentByID(appointmentID):
    cursor.execute("""
    SELECT
        AppointmentID,
        Appointment_date,
        Appointment_time,
        PatientID,
        StaffID,
        Duration
    FROM Appointments_Table
    WHERE AppointmentID = ?
    """, (appointmentID,))
    return cursor.fetchone()