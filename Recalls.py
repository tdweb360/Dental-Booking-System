import sqlite3
import patients
from datetime import datetime

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

def viewRecalls():
    #inner join = combine records from two tables whenever there are matching values in a field common to both tables
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
    results = cursor.fetchall()
    if len(results) == 0:
        print("No recalls found")
    else:
        for r in results:
            print(
                f"\nRecallID: {r[0]}"
                f" | PatientID: {r[1]}"
                f" | Name: {r[2]} {r[3]}"
                f" | Suggested Date: {r[4]}"
                f" | Priority: {r[5]}"
            )
        manageRecalls()
def manageRecalls():
    valid = False
    while not valid:
        try:
            choice = int(input(
                "\n1. Change Priority"
                "\n2. Mark Complete"
                "\n3. Exit\n\n"
                ">> "
            ))
            if choice == 1:
                changePriority()
            elif choice == 2:
                completeRecall()
            elif choice == 3:
                valid = True
            else:
                print("Not a valid option")
        except ValueError:
            print("Invalid Input")

def changePriority():

    try:
        recallID = int(input(
            "Enter Recall ID: "
        ))
        priority = int(input(
            "Enter Priority (1-5): "
        ))
        if 1 <= priority <= 5:
            cursor.execute("""
            UPDATE Recall_Table
            SET Priority = ?
            WHERE RecallID = ?
            """, (
                priority,
                recallID
            ))
            connect.commit()
            print("Priority updated")
        else:
            print("Priority must be between 1 and 5")

    except ValueError:
        print("Invalid Input")


def completeRecall():
    try:
        recallID = int(input(
            "Enter Recall ID: "
        ))
        cursor.execute("""
        UPDATE Recall_Table
        SET Completed = 1
        WHERE RecallID = ?
        """, (recallID,))
        connect.commit()
        print("Recall completed")
    except ValueError:
        print("Invalid Input")