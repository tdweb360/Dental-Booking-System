import patients
import sqlite3
import re
import bcrypt
import Logging
from patients import validateFNandSN

connect = sqlite3.connect('database.db')
cursor = connect.cursor()


def addStaff(current_user):

    confirm = False
    attempts = 0
    while confirm == False and attempts < 5:
        firstname, surname = patients._validateFNandSN()
        username = createUsername()
        password = createPass()
        hashed_pass = hashpass(password)
        role = roleselect()
        print("\nYou entered:\nName:", firstname, surname,
              "\nUsername:", username,
              "\nRole:", role)
        answer = input("Are these details correct?:  ").strip().lower()

        if answer in ["y", "yes"]:
            confirm = True
        else:
            attempts += 1
    if attempts == 5:
        print("Too many failed attempts")
        return
    try:
        cursor.execute("""
        INSERT INTO Staff_Table (FirstName, Surname, Username, Password_Hash, Staff_Role) 
        VALUES (?,?,?,?,?)
            """, (firstname, surname, username, hashed_pass, role,))
        connect.commit()
        cursor.execute("""
        SELECT last_insert_rowid()
        """)
        staffID = cursor.fetchone()[0]
        Logging.log_action(
            current_user,
            "CREATE_STAFF",
            f"StaffID {staffID}, Username {username}"
        )

    except:
        print("database error")

def addStaffGUI(firstname,surname,username,password,pass2,role,current_user):
    if not patients.validateFNandSN(firstname, surname):
        return "INVALID FIRST NAME OR SURNAME"
    if not createUsername(username):
        return "INVALID USERNAME"
    passresult = createPass(password,pass2)
    if passresult != "VALID":
        return passresult

    hashed_pass = hashpass(password)
    try:
        cursor.execute("""
        INSERT INTO Staff_Table (FirstName, Surname, Username, Password_Hash, Staff_Role) 
        VALUES (?,?,?,?,?)
            """, (firstname, surname, username, hashed_pass, role,))
        connect.commit()
        cursor.execute("""
        SELECT last_insert_rowid()
        """)
        staffID = cursor.fetchone()[0]
        Logging.log_action(
            current_user,
            "CREATE_STAFF",
            f"StaffID {staffID}, Username {username}"
        )

        return "SUCCESS"
    except:
        return "DATABASE ERROR"

def createUsername(username):

    pattern = r"^[A-Za-z0-9._]+$"

    if not(4 <= len(username) <= 20):
        return False
    elif not(re.match(pattern,username)):
        return False
    else:
        cursor.execute("""
            SELECT Username
            FROM Staff_Table
            WHERE Username = ?
            """, (username,))

        result = cursor.fetchone()

        if result:
            return False
        else:
            return username

def createPass(password, pass2):
    if len(password) < 8:
        return "PASSWORD_LENGTH"
    elif not re.search(r"[A-Z]", password):
        return "PASSWORD_UPPERCASE"
    elif not re.search(r"[a-z]", password):
        return "PASSWORD_LOWERCASE"
    elif not re.search(r"\d", password):
        return "PASSWORD_NUMBER"
    elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "PASSWORD_SPECIAL"
    elif password != pass2:
        return "PASSWORD_MATCH"
    return "VALID"


def roleselect():
    valid = False
    while not valid:
        try:
            role = int(input("Enter role:"
                             "\n\n1. Dentist"
                             "\n\n2. Receptionist"
                             "\n\n3. Manager"))
            if role == 1:
                return "Dentist"
            elif role == 2:
                return "Receptionist"
            elif role == 3:
                if checkManager():
                    return "Manager"
                else:
                    print("Failed")
            else:
                print("Not a valid choice")
        except ValueError:
            print("Input must be a number")
def checkManager():
    return True

def createInitialManager():
    cursor.execute("""
    SELECT COUNT(*)
    FROM Staff_Table
    WHERE Staff_Role = 'Manager'
    """)

    result = cursor.fetchone()

    if result[0] == 0:
        print("No manager account found.")
        print("Create an initial manager account.\n")

        firstname, surname = patients._validateFNandSN()
        username = createUsername()
        password = createPass()

        hashedPassword = hashpass(password)

        cursor.execute("""
        INSERT INTO Staff_Table
        (FirstName, Surname, Username, Password_Hash, Staff_Role)
        VALUES (?,?,?,?,?)
        """, (
            firstname,
            surname,
            username,
            hashedPassword,
            "Manager"
        ))

        connect.commit()
        Logging.log_action(
            "SYSTEM",
            "CREATE_INITIAL_MANAGER",
            f"Username {username}"
        )
        print("Manager account created successfully")


def hashpass(password):
    salt = bcrypt.gensalt()
    hashedPassword = bcrypt.hashpw(password.encode(), salt)
    return hashedPassword.decode()

def staffManagementMenu(current_user):
    chosenID = searchStaff()

    if chosenID is None:
        return

    valid = False

    while not valid:
        try:
            choice = int(input(
                "Do you want to:\n\n"
                "1. Edit Name\n"
                "2. Edit Username\n"
                "3. Reset Password\n"
                "4. Change Role\n"
                "5. Delete Staff Member\n"
                "6. Exit\n\n"
                ">> "))
            if choice == 1:
                editName(chosenID, current_user)
            elif choice == 2:
                resetUsername(chosenID, current_user)
            elif choice == 3:
                resetPassword(chosenID, current_user)
            elif choice == 4:
                changeRole(chosenID, current_user)
            elif choice == 5:
                successful = deleteStaff(chosenID, current_user)
                if successful:
                    valid = True
            elif choice == 6:
                valid = True
            else:
                print("Not a valid option")
        except ValueError:
            print("Invalid Input")

def editName(staffID,current_user):
    firstname,surname = patients._validateFNandSN()
    confirm = input("Are you sure?").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            cursor.execute("""UPDATE Staff_Table
                SET FirstName = ?, Surname = ?
                WHERE StaffID = ?""", (firstname,surname, staffID))
            connect.commit()
            Logging.log_action(
                current_user,
                "EDIT_STAFF_NAME",
                f"StaffID {staffID}, New Name {firstname} {surname}"
            )
            print("Name changed")
        except:
            print("Database error")

def resetUsername(staffID,current_user):
    username = createUsername()
    confirm = input("Are you sure?").strip().lower()
    if confirm in ["yes", "y"]:
        try:
            cursor.execute("""UPDATE Staff_Table
                SET Username = ?
                WHERE StaffID = ?""", (username,staffID))
            connect.commit()
            Logging.log_action(
                current_user,
                "EDIT_STAFF_USERNAME",
                f"StaffID {staffID}, New Username {username}"
            )
            print("Username changed")
        except:
            print("Database error")

def resetPassword(staffID, current_user):
    password = createPass()
    hashedPassword = hashpass(password)

    confirm = input("Are you sure? ").strip().lower()

    if confirm in ["yes", "y"]:
        try:
            cursor.execute("""
            UPDATE Staff_Table
            SET Password_Hash = ?
            WHERE StaffID = ?
            """, (hashedPassword, staffID))

            connect.commit()
            Logging.log_action(
                current_user,
                "RESET_PASSWORD",
                f"StaffID {staffID}"
            )
            print("Password changed")

        except:
            print("Database error")

def changeRole(staffID, current_user):
    role = roleselect()

    confirm = input("Are you sure? ").strip().lower()

    if confirm in ["yes", "y"]:
        try:
            cursor.execute("""
            UPDATE Staff_Table
            SET Staff_Role = ?
            WHERE StaffID = ?
            """, (role, staffID))

            connect.commit()
            Logging.log_action(
                current_user,
                "CHANGE_ROLE",
                f"StaffID {staffID}, New Role {role}"
            )
            print("Role changed")

        except:
            print("Database error")

def deleteStaff(staffID, current_user):
    try:
        cursor.execute("""
        DELETE FROM Staff_Table
        WHERE StaffID = ?
        """,(staffID,))
        connect.commit()
        Logging.log_action(
            current_user,
            "DELETE_STAFF",
            f"StaffID {staffID}")
        return "SUCCESS"
    except:
        return "DATABASE_ERROR"

def searchStaff():
    valid = False
    while not valid:
        try:
            choice = int(input("Do you want to search by:"
                               "\n\n1. Staff Role"
                               "\n2. Name"
                               "\n\n>> "))
            if choice == 1:
                return searchStaffRole()
            elif choice == 2:
                return searchStaffName()
            else:
                print("Not a valid option")
        except ValueError:
            print("Must be an integer")

def searchStaffRole():
    valid = False

    while not valid:
        try:
            choice = int(input(
                "Select role:\n\n"
                "1. Dentist\n"
                "2. Receptionist\n"
                "3. Manager\n\n"
                ">> "
            ))
            if choice == 1:
                role = "Dentist"
            elif choice == 2:
                role = "Receptionist"
            elif choice == 3:
                role = "Manager"
            else:
                print("Not a valid choice")
                continue
            cursor.execute("""
            SELECT *
            FROM Staff_Table
            WHERE Staff_Role = ?
            """, (role,))
            results = cursor.fetchall()
            return fetchStaffQueryResults(results)
        except ValueError:
            print("Input must be a number")

def getAllStaff():

    cursor.execute("""
    SELECT StaffID, FirstName, Surname
    FROM Staff_Table
    ORDER BY Surname, FirstName
    """)
    return cursor.fetchall()

def searchStaffNameOLD():
    name = input("Enter name: ").strip().capitalize()
    searchPattern = "%" + name + "%"
    pattern = r"^[A-Za-z'-]+$"
    valid = False
    while not valid:

        if len(name) > 2 and re.match(pattern, name):

            cursor.execute("""
            SELECT * FROM Staff_Table
            WHERE FirstName LIKE ? or Surname LIKE ?
                           """, (searchPattern, searchPattern))
            results = cursor.fetchall()
            if len(results) > 0:
                valid = True
            else:
                print("Error")
        else:
            print("Error")
    return fetchStaffQueryResults(results)

def fetchStaffQueryResults(results):
    valid_ids = []
    if len(results) == 0:
        print("No staff members found")
    else:
        for p in results:
            print(f"ID: {p[0]}"
                  f" | Name: {p[1]} {p[2]}"
                  f" | Username: {p[3]}"
                  f" | Role: {p[5]}")
            valid_ids.append(p[0])
        chosenID = selectStaff(valid_ids)
        return chosenID

def selectStaff(valid_ids):
    valid = False
    while not valid:
        try:
            chosenID = int(input("Enter ID of chosen staff member:  "))
            if chosenID in valid_ids:
                return chosenID

            else:
                print("Not present")
        except ValueError:
            print("Invalid Input")

def getStaffByID(staffID):
    cursor.execute("""
    SELECT *
    FROM Staff_Table
    WHERE StaffID = ?
    """,(staffID,))
    return cursor.fetchone()


def searchStaffName(name):
    searchPattern = f"%{name}%"
    cursor.execute("""
    SELECT *
    FROM Staff_Table
    WHERE FirstName LIKE ?
    OR Surname LIKE ?
    """,(searchPattern, searchPattern))
    return cursor.fetchall()