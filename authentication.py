import sqlite3

import bcrypt

connect = sqlite3.connect('database.db')
cursor = connect.cursor()
def login():
    valid = False
    attempts = 0
    while valid == False and attempts <= 3:
        attempts += 1
        username = input("Enter Username")
        password = input("Enter Password")
        cursor.execute("""
        SELECT StaffID, Password_Hash, Staff_Role
        FROM Staff_Table
        WHERE Username = ?""",(username,))
        result = cursor.fetchone()
        staffID = result[0]
        storedHash = result[1]
        role = result[2]
        if not result:
            print("Invalid Username or Password")
        else:
            if bcrypt.checkpw(password.encode(), storedHash.encode()):
                valid = True
            else:
                print("Invalid Username or Password")
        attempts += 1
    if attempts == 3:
        print("Too many failed attempts")
    else:
        return staffID, role
