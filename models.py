from symtable import Class


class Person():
    def __init__(self, firstname, surname):
        self.__firstname = firstname
        self.__surname = surname

    def getFN(self):
        return self.__firstname
    def getSN(self):
        return self.__surname
    def getFull(self):
        return (f"{self.__firstname} {self.__surname}")
    #override by sub
    def describe(self):
        return self.getFull()

class Patient(Person):
    def __init__(self, patientID, firstname, surname, dob,phone):
        super().__init__(firstname,surname)
        self.__patientID = patientID
        self.__dob = dob
        self.__phone = phone

    @staticmethod
    def fromRow(row):
        return Patient(row[0], row[1], row[2], row[3], row[4])

    def getPatientID(self):
        return self.__patientID
    def getDOB(self):
        return self.__dob
    def getPhoNum(self):
        return self.__phone
    def describe(self):
        return f"{self.getFull()} (Patient ID: {self.__patientID})"

class StaffMember(Person):
    def __init__(self, staffID,firstname,surname,username,role):
        super().__init__(firstname,surname)
        self.__staffID = staffID
        self.__username = username
        self.__role = role

    @staticmethod
    def fromRow(row):
        return StaffMember(row[0],row[1],row[2],row[3],row[4])
    def getStaffID(self):
        return self.__staffID
    def getusername(self):
        return self.__username
    def getrole(self):
        return self.__role
    def ismanager(self):
        if self.__role == "Manager":
            return True
        else:
            return False
    def describe(self):
        return f"{self.getFullName()} ({self.__role})"