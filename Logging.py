import sqlite3
from datetime import datetime

connect = sqlite3.connect("database.db")
cursor = connect.cursor()

def log_action(username, action, details):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO AuditLog
        (Username, Action, Details, Timestamp)
        VALUES (?, ?, ?, ?)
    """, (username, action, details, timestamp))

    connect.commit()


def viewAuditLog():

    page = 0
    recordsPerPage = 10
    valid = False

    while not valid:
        offset = page * recordsPerPage
        cursor.execute("""
        SELECT Username,
               Action,
               Details,
               Timestamp
        FROM AuditLog
        ORDER BY LogID DESC
        LIMIT ?
        OFFSET ?
        """, (recordsPerPage, offset))
        results = cursor.fetchall()
        if len(results) == 0:
            print("No audit records found")
        else:
            print(f"\n--- Audit Log Page {page + 1} ---\n")
            for log in results:
                print(
                    f"{log[3]}"
                    f" | {log[0]}"
                    f" | {log[1]}"
                    f" | {log[2]}"
                )
        try:
            choice = int(input(
                "\n1. Next Page"
                "\n2. Previous Page"
                "\n3. Exit\n\n"
                ">> "
            ))
            if choice == 1:
                page += 1
            elif choice == 2:
                if page > 0:
                    page -= 1
                else:
                    print("Already on first page")
            elif choice == 3:
                valid = True
            else:
                print("Not a valid option")
        except ValueError:
            print("Input must be a number")