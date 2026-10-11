
# file contains all logging SQL statements and logic

import sqlite3
from datetime import datetime

connect = sqlite3.connect("database.db")
cursor = connect.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

def log_action(username, action, details):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO AuditLog
        (Username, Action, Details, Timestamp)
        VALUES (?, ?, ?, ?)
    """, (username, action, details, timestamp))

    connect.commit()


def getAuditLogs():
    cursor.execute("""
    SELECT LogID,
           Username,
           Action,
           Details,
           Timestamp
    FROM AuditLog
    ORDER BY LogID DESC
    """)
    return cursor.fetchall()



