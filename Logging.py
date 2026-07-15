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
    cursor.execute("""
        SELECT Username,
               Action,
               Details,
               Timestamp
        FROM AuditLog
        ORDER BY LogID DESC
    """)
    results = cursor.fetchall()

    for log in results:
        print(
            f"{log[3]} | {log[0]} | {log[1]} | {log[2]}"
        )