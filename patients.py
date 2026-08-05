import sqlite3
from datetime import datetime
import re
import appointments
import Logging

connect = sqlite3.connect('database.db')
cursor = connect.cursor()


def validateFNandSN(firstname, surname):
    pattern = r"^[A-Za-z'-]+$"
    if len(firstname) == 0 or len(surname) == 0:
        return False
    if not re.match(pattern, firstname):
        return False
    if not re.match(pattern, surname):
        return False
    return True

def validateDOB(dob):
    try:
        date = datetime.strptime(dob,"%d/%m/%Y")
        if date > datetime.today():
            return False
        return True
    except ValueError:
        return False


def validatePhoneNUM(phone):
    phone = phone.replace(" ", "")
    pattern = r"^(07\d{9}|\+44\d{10})$"
    if re.match(pattern, phone):
        return True
    return False

def search_patients(name="", phone="", dob=""):
    from datetime import datetime
    query = """
        SELECT *
        FROM Patients_Table
        WHERE 1=1
    """
    params = []

    if name:
        query += """
            AND (
                FirstName LIKE ?
                OR Surname LIKE ?
            )
        """
        params.extend([
            f"%{name}%",
            f"%{name}%"
        ])
    if phone:
        query += """
            AND Phone_Num LIKE ?
        """
        params.append(f"%{phone}%")
    if dob:
        try:
            dob = datetime.strptime(
                dob,
                "%d/%m/%Y"
            ).strftime("%Y-%m-%d")
        except ValueError:
            return "INVALID_DATE"
        query += """
            AND Date_of_birth = ?
        """
        params.append(dob)
    cursor.execute(query, params)
    return cursor.fetchall()




def get_patient_by_id(patient_id):
    cursor.execute("""
        SELECT *
        FROM Patients_Table
        WHERE PatientID = ?
    """, (patient_id,))
    return cursor.fetchone()


def deletePatient(patientID, current_user):
    try:
        cursor.execute("""
            DELETE FROM Patients_Table
            WHERE PatientID = ?
        """, (patientID,))
        connect.commit()
        Logging.log_action(
            current_user,
            "DELETE_PATIENT",
            f"PatientID {patientID}")
        return True
    except:
        return False



def updatePatient(patientID, firstname, surname, dob, phone, current_user):
    if not validateFNandSN(firstname, surname):
        return "INVALID_NAME"
    if not validateDOB(dob):
        return "INVALID_DOB"
    dob = datetime.strptime(dob,"%d/%m/%Y").strftime("%Y-%m-%d")
    if not validatePhoneNUM(phone):
        return "INVALID_PHONE"
    try:
        cursor.execute("""
            UPDATE Patients_Table
            SET
                FirstName = ?,
                Surname = ?,
                Date_of_birth = ?,
                Phone_Num = ?
            WHERE PatientID = ?
        """, (firstname, surname, dob, phone, patientID))
        connect.commit()
        Logging.log_action(
            current_user,
            "EDIT_PATIENT",
            f"PatientID {patientID}")
        return "SUCCESS"
    except:
        return "DATABASE_ERROR"

def addPatient(firstname, surname, dob, phone, current_user):
    if not validateFNandSN(firstname, surname):
        return "INVALID_NAME"
    if not validateDOB(dob):
        return "INVALID_DOB"
    dob = datetime.strptime(dob, "%d/%m/%Y").strftime("%Y-%m-%d")
    if not validatePhoneNUM(phone):
        return "INVALID_PHONE"
    try:
        cursor.execute("""
            INSERT INTO Patients_Table
            (FirstName, Surname, Date_of_birth, Phone_Num)
            VALUES (?, ?, ?, ?)
        """, (firstname, surname, dob, phone))
        connect.commit()
        patientID = cursor.lastrowid
        Logging.log_action(
            current_user,
            "CREATE_PATIENT",
            f"PatientID {patientID}"
        )
        return "SUCCESS"
    except Exception as e:
        print(e)
        return "DATABASE_ERROR"



