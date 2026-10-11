
# file manages all authentication logic and SQL queries related to authentication


import sqlite3

import bcrypt
import Logging

connect = sqlite3.connect('database.db')
cursor = connect.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

def login(username,password):
    cursor.execute("""
    SELECT StaffID, Password_Hash, Staff_Role
    FROM Staff_Table
    WHERE Username = ?
    """, (username,))
    result = cursor.fetchone()
    if not result:
        print("")
    else:
        staffID = result[0]
        storedHash = result[1]
        role = result[2]
        if bcrypt.checkpw(password.encode(), storedHash.encode()):
            Logging.log_action(
                username,"LOGIN_SUCCESS",f"StaffID {staffID}")
            return staffID, role, username
        else:
            Logging.log_action(
                username,
                "LOGIN_FAILED",
                "Invalid credentials"
            )
    return None

