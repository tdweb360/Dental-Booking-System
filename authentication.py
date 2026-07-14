import sqlite3

import bcrypt

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
                return staffID, role
            else:
                print("Invalid Username or Password")
                attempts += 1
    print("Too many failed attempts")
    return None