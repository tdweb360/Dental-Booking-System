
# file contains all recall logic and SQL statements related to recalls and managing them


import sqlite3
import appointments
from datetime import datetime, timedelta
connect = sqlite3.connect("database.db")
cursor = connect.cursor()


def generateRecalls():

    today = datetime.today().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT AppointmentID,
           PatientID,
           Appointment_date
    FROM Appointments_Table
    WHERE Appointment_date < ?
    """, (today,))

    appointments = cursor.fetchall()

    for appointment in appointments:

        appointmentID = appointment[0]
        patientID = appointment[1]
        appointmentDate = appointment[2]

        cursor.execute("""
        SELECT COUNT(*)
        FROM Recall_Table
        WHERE AppointmentID = ?
        """, (appointmentID,))

        result = cursor.fetchone()

        if result[0] > 0:
            continue

        cursor.execute("""
        SELECT COUNT(*)
        FROM Appointments_Table
        WHERE PatientID = ?
        AND Appointment_date > ?
        """, (patientID, today))

        result = cursor.fetchone()

        if result[0] == 0:

            suggestedDate = (datetime.strptime(appointmentDate,"%Y-%m-%d") + timedelta(days=183)).strftime("%Y-%m-%d")

            cursor.execute("""
            INSERT INTO Recall_Table
            (PatientID,
             AppointmentID,
             SuggestedDate,
             Priority)
            VALUES (?,?,?,?)
            """, (
                patientID,
                appointmentID,
                suggestedDate,
                5
            ))
    connect.commit()


def getActiveRecalls():
    generateRecalls()
    cursor.execute("""
    SELECT RecallID,
           Patients_Table.PatientID,
           Patients_Table.FirstName,
           Patients_Table.Surname,
           SuggestedDate,
           Priority
    FROM Recall_Table
    INNER JOIN Patients_Table
    ON Recall_Table.PatientID = Patients_Table.PatientID
    WHERE Completed = 0
    ORDER BY Priority ASC, SuggestedDate ASC
    """)
    return cursor.fetchall()




def updatePriority(recallID, priority):
    cursor.execute("""
    UPDATE Recall_Table
    SET Priority = ?
    WHERE RecallID = ?
    """, (priority, recallID))
    connect.commit()

def completeRecall(recallID):
    cursor.execute("""
    UPDATE Recall_Table
    SET Completed = 1
    WHERE RecallID = ?
    """, (recallID,))
    connect.commit()


