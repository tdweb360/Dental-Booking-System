import patients
import appointments
import authentication
import sqlite3
import staff
import Logging
connect = sqlite3.connect('database.db')
cursor = connect.cursor()


def main():
    staff.createInitialManager()
    result = authentication.login()
    if result is None:
        return
    staffID, role, username = result
    if role == "Manager":
        manager_menu(username)
    else:
        staff_menu(username)

def staff_menu(username):
    valid = False
    while not valid:
        try:
            choice = int(input(
                "1. Add Patient\n"
                "2. Search Patient/book appointment\n"
                "3. Manage Appointments\n"
                "4. Logout\n\n>>  "))

            if choice == 1:
                patients.enterpatientdetails(username)

            elif choice == 2:
                patientID = patients.searchPatient()
                if patientID is not None:
                    patients.patientmanagementwindow(patientID, username)

            elif choice == 3:
                appointments.searchMenu(username)

            elif choice == 4:
                valid = True

            else:
                print("Error")

        except ValueError:
            print("Incorrect datatype")

def manager_menu(username):
    valid = False
    while not valid:
        try:
            choice = int(input(
                "1. Add Patient\n"
                "2. Search Patient\n"
                "3. Manage Appointments\n"
                "4. Add Staff\n"
                "5. Manage Staff\n"
                "6. View Audit Log\n"
                "7. Logout\n\n>>  "))

            if choice == 1:
                patients.enterpatientdetails(username)

            elif choice == 2:
                patientID = patients.searchPatient()
                if patientID is not None:
                    patients.patientmanagementwindow(patientID,username)

            elif choice == 3:
                appointments.searchMenu(username)

            elif choice == 4:
                staff.addStaff(username)

            elif choice == 5:
                staff.staffManagementMenu(username)

            elif choice == 6:
                Logging.viewAuditLog()

            elif choice == 7:
                valid = True

            else:
                print("Error")

        except ValueError:
            print("Incorrect datatype")




if __name__ == "__main__":
    main()