import patients
import appointments
import authentication
import sqlite3
import staff
connect = sqlite3.connect('database.db')
cursor = connect.cursor()


def main():
    staff.createInitialManager()
    staffID, role = authentication.login()
    if role == "Manager":
        manager_menu()
    else:
        staff_menu()

def staff_menu():
    valid = False
    while not valid:
        try:
            choice = int(input(
                "1. Add Patient\n"
                "2. Search Patient\n"
                "3. Manage Appointments\n"
                "4. Logout\n\n>>  "))

            if choice == 1:
                patients.enterpatientdetails()

            elif choice == 2:
                patientID = patients.searchPatient()
                if patientID is not None:
                    patients.patientmanagementwindow(patientID)

            elif choice == 3:
                appointments.searchMenu()

            elif choice == 4:
                valid = True

            else:
                print("Error")

        except ValueError:
            print("Incorrect datatype")

def manager_menu():
    valid = False
    while not valid:
        try:
            choice = int(input(
                "1. Add Patient\n"
                "2. Search Patient\n"
                "3. Manage Appointments\n"
                "4. Manage Staff\n"
                "5. Logout\n\n>>  "))

            if choice == 1:
                patients.enterpatientdetails()

            elif choice == 2:
                patientID = patients.searchPatient()
                if patientID is not None:
                    patients.patientmanagementwindow(patientID)

            elif choice == 3:
                appointments.searchMenu()

            elif choice == 4:
                staff.staffManagementMenu()

            elif choice == 5:
                valid = True

            else:
                print("Error")

        except ValueError:
            print("Incorrect datatype")




if __name__ == "__main__":
    main()