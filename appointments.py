
# file manages all appointment logic and SQL queries related to appointments

import sqlite3
from datetime import datetime, timedelta

import Logging
connect = sqlite3.connect('database.db')
cursor = connect.cursor()
cursor.execute("PRAGMA foreign_keys = ON")


def createAppointment(patientID,staffID,date,time,duration,current_user):
    resultDATE = validateAppointmentDate(date)
    if resultDATE == "WRONG FORMAT":
        return "WRONG FORMAT"
    elif resultDATE == "PAST DATE":
        return "PAST DATE"
    resultTIME = validateAppointmentTime(time,duration)
    if resultTIME in ["HOUR", "MIN"] or resultTIME is False:
        return "INVALID TIME"
    if resultTIME == "ENDofDAY":
        return "END OF DAY"
    if datetime.strptime(date + " " + time, "%d/%m/%Y %H:%M") < datetime.now():
        return "PAST DATE"
    date = datetime.strptime(date,"%d/%m/%Y").strftime("%Y-%m-%d")

    conflict = checkConflict(date,time,duration,staffID,patientID)
    if conflict:
        return conflict
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
            return "STAFF CONFLICT"

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
            return "PATIENT CONFLICT"

    return False






def editAppointment(appointmentID,date,time,duration,patientID, staffID,current_user):

    resultDATE = validateAppointmentDate(date)
    if resultDATE == "WRONG FORMAT":
        return "WRONG FORMAT"
    elif resultDATE == "PAST DATE":
        return "PAST DATE"
    resultTIME = validateAppointmentTime(time,duration)
    if resultTIME in ["HOUR", "MIN"] or resultTIME is False:
        return "INVALID TIME"
    if resultTIME == "ENDofDAY":
        return "END OF DAY"
    if datetime.strptime(date + " " + time, "%d/%m/%Y %H:%M") < datetime.now():
        return "PAST DATE"
    dbDate = datetime.strptime(date,"%d/%m/%Y").strftime("%Y-%m-%d")
    conflict = checkConflict(dbDate,time,duration,staffID,patientID,appointmentID)
    if conflict:
        return conflict
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
    except sqlite3.Error:
        return "UNSUCCESSFUL"


def deleteAppointment(appointmentID, current_user):
    try:
        cursor.execute("""
        DELETE FROM Recall_Table
        WHERE AppointmentID = ?
        """, (appointmentID,))
        cursor.execute("""
        DELETE FROM Appointments_Table
        WHERE AppointmentID = ?
        """, (appointmentID,))
        if cursor.rowcount == 0:
            connect.rollback()
            return False
        connect.commit()
        Logging.log_action(
            current_user,
            "DELETE_APPOINTMENT",
            f"AppointmentID {appointmentID}")
        return True
    except sqlite3.Error:
        connect.rollback()
        return False


def validateAppointmentDate(date):
    try:
        parsedDate = datetime.strptime(date, "%d/%m/%Y")
        if parsedDate.strftime("%d/%m/%Y") != date:
            return "WRONG FORMAT"
        if parsedDate.date() < datetime.today().date():
            return "PAST DATE"
        return True
    except ValueError:
        return "WRONG FORMAT"
#
def validateAppointmentTime(time, duration):
    try:
        if duration not in [15, 30, 45, 60]:
            return False
        parsed = datetime.strptime(time, "%H:%M")
        if parsed.strftime("%H:%M") != time:
            return False
        time = parsed
        endTime = time + timedelta(minutes=duration)
        if not (9 <= time.hour < 17):
            return "HOUR"
        if time.minute not in [0, 15, 30, 45]:
            return "MIN"
        if endTime > datetime.strptime("17:00", "%H:%M"):
            return "ENDofDAY"
        return True
    except ValueError:
        return False

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