import patients
import sqlite3
import re
import bcrypt
import Logging
from patients import validateFNandSN

connect = sqlite3.connect('database.db')
cursor = connect.cursor()

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
        return "PASSWORD LENGTH"
    elif not re.search(r"[A-Z]", password):
        return "PASSWORD UPPERCASE"
    elif not re.search(r"[a-z]", password):
        return "PASSWORD LOWERCASE"
    elif not re.search(r"\d", password):
        return "PASSWORD NUMBER"
    elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "PASSWORD SPECIAL"
    elif password != pass2:
        return "PASSWORD MATCH"
    return "VALID"




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



def hashpass(password):
    salt = bcrypt.gensalt()
    hashedPassword = bcrypt.hashpw(password.encode(), salt)
    return hashedPassword.decode()



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

def updateStaff(staffID,firstname,surname,username,role,current_user):
    if not patients.validateFNandSN(
            firstname,
            surname):
        return "INVALID_NAME"

    try:
        cursor.execute("""
        SELECT StaffID
        FROM Staff_Table
        WHERE Username = ?
        """, (username,))
        result = cursor.fetchone()
        if result and result[0] != staffID:
            return "INVALID_USERNAME"
        cursor.execute("""
        UPDATE Staff_Table
        SET
        FirstName = ?,
        Surname = ?,
        Username = ?,
        Staff_Role = ?
        WHERE StaffID = ?
        """,(firstname,surname,username,role,staffID))
        connect.commit()
        Logging.log_action(
            current_user,
            "EDIT_STAFF",
            f"StaffID {staffID}"
        )
        return "SUCCESS"
    except:
        return "DATABASE_ERROR"

def resetPasswordGUI(staffID,password,confirmPassword,current_user):
    passResult = createPass(password,confirmPassword)
    if passResult != "VALID":
        return passResult
    hashedPassword = hashpass(password)
    try:
        cursor.execute("""
        UPDATE Staff_Table
        SET Password_Hash = ?
        WHERE StaffID = ?
        """,(hashedPassword,staffID))

        connect.commit()
        Logging.log_action(
            current_user,
            "RESET_PASSWORD",
            f"StaffID {staffID}"
        )
        return "SUCCESS"
    except:
        return "DATABASE_ERROR"



def getAllStaff():

    cursor.execute("""
    SELECT StaffID, FirstName, Surname
    FROM Staff_Table
    ORDER BY Surname, FirstName
    """)
    return cursor.fetchall()




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