import sqlite3
import patients

connect = sqlite3.connect("database.db")
cursor = connect.cursor()


from datetime import datetime

def viewOverdueRecalls():
    today = datetime.today().strftime("%Y-%m-%d")
    cursor.execute("""
    SELECT RecallID,
           Patients_Table.FirstName,
           Patients_Table.Surname,
           DueDate,
           Priority
    FROM Recall_Table
    INNER JOIN Patients_Table
    ON Recall_Table.PatientID = Patients_Table.PatientID
    WHERE DueDate <= ?
    AND Completed = 0
    ORDER BY Priority ASC, DueDate ASC
    """, (today,))
    results = cursor.fetchall()
    if len(results) == 0:
        print("No overdue recalls found")
    else:
        for r in results:
            print(
                f"RecallID: {r[0]}"
                f" | Name: {r[1]} {r[2]}"
                f" | Priority: {r[4]}"
                f" | Due Date: {r[3]}"
            )


def completeRecall():

    recallID = int(input("Enter Recall ID: "))

    cursor.execute("""
    UPDATE Recall_Table
    SET Completed = 1
    WHERE RecallID = ?
    """, (recallID,))

    connect.commit()

    print("Recall completed")