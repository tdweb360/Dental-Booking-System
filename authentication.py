import sqlite3

import bcrypt
import Logging

connect = sqlite3.connect('database.db')
cursor = connect.cursor()
def login():
    valid = False
    attempts = 0
    while not valid and attempts < 3:
        username = input("Enter Username: ")
        password = input("Enter Password: ")
        cursor.execute("""
        SELECT StaffID, Password_Hash, Staff_Role
        FROM Staff_Table
        WHERE Username = ?
        """, (username,))
        result = cursor.fetchone()
        if not result:
            print("Invalid Username or Password")
            attempts += 1
        else:
            staffID = result[0]
            storedHash = result[1]
            role = result[2]
            if bcrypt.checkpw(password.encode(), storedHash.encode()):
                Logging.log_action(
                    username,"LOGIN_SUCCESS",f"StaffID {staffID}")
                return staffID, role, username
            else:
                print("Invalid Username or Password")
                Logging.log_action(
                    username,
                    "LOGIN_FAILED",
                    "Invalid credentials"
                )
                attempts += 1
    print("Too many failed attempts")
    Logging.log_action(
        username,
        "ACCOUNT_LOCKED",
        "Three failed login attempts"
    )
    return None

