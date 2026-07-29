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
            print(f"Created recall for PatientID {patientID}")
    connect.commit()


def viewRecalls(current_user):
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
        manageRecalls(current_user)

def manageRecalls(current_user):
    valid = False
    while not valid:
        try:
            choice = int(input(
                "\n1. Change Priority"
                "\n2. Book Recall"
                "\n3. Complete Recall Without Booking Follow-Up"
                "\n4. Exit\n\n"
                ">> "
            ))
            if choice == 1:
                changePriority()
            elif choice == 2:
                bookRecall(current_user)
            elif choice == 3:
                confirm = (input("Are you sure")).lower().strip()
                if confirm in ["yes","y"]:
                    completeRecall()
                else:
                    print("Recall left active")
            elif choice == 4:
                valid = True
            else:
                print("Not a valid option")
        except ValueError:
            print("Invalid Input")

def bookRecall(current_user):
    try:
        recallID = int(input(
            "Enter Recall ID: "
        ))
        cursor.execute("""
        SELECT PatientID,
               SuggestedDate
        FROM Recall_Table
        WHERE RecallID = ?
        """, (recallID,))
        result = cursor.fetchone()
        if result is None:
            print("Recall not found")
            return
        patientID = result[0]
        suggestedDate = result[1]
        valid = False
        while valid == False:
            try:
                choice = int(input(
                    "\n1. Use Suggested Date"
                    "\n2. Book Earlier/Later"
                    "\n3. Exit\n\n"
                    ">> "
                ))
                if choice == 1:
                    successful = appointments.bookAppointment(patientID,current_user,suggestedDate)
                elif choice == 2:
                    successful = appointments.bookAppointment(patientID,current_user)
                elif choice == 3:
                    return
                else:
                    print("Not a valid option")
                    continue

                if successful:
                    cursor.execute("""
                    UPDATE Recall_Table
                    SET Completed = 1
                    WHERE RecallID = ?
                    """, (recallID,))
                    connect.commit()
                    print("Recall completed")
                    valid = True
            except ValueError:
                print("Error")
    except ValueError:
        print("Invalid Input")

def changePriority():
    valid = False
    while valid == False:
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
                valid = True
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


def testRecalls():

    print("\n===== TESTING RECALL LIST =====\n")

    cursor.execute("""
    SELECT *
    FROM Recall_Table
    """)

    recalls = cursor.fetchall()

    print("Recall records found:", len(recalls))

    for r in recalls:
        print(r)

    print("\n===== TESTING ACTIVE RECALLS =====\n")

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

    print("Active recalls:", len(results))

    for r in results:
        print(
            f"RecallID: {r[0]}"
            f" | PatientID: {r[1]}"
            f" | Name: {r[2]} {r[3]}"
            f" | Suggested Date: {r[4]}"
            f" | Priority: {r[5]}"
        )

    print("\n===== TEST COMPLETE =====")