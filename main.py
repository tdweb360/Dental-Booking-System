import patients
import appointments
valid = False
while not valid:
    choice = int(input("1. Add Patient\n2. Search Patient\n3. \n\n>>  "))
    if choice == 1:
        patients.enterpatientdetails()
    elif choice == 2:
        patientID = patients.searchPatient()
        if patientID is not None:
            patients.patientmanagementwindow(patientID)
    elif choice == 3:
        appointments.searchMenu()
    elif choice == 4:
        print("Exiting...")
        valid = True
    else:
        print("Error")

