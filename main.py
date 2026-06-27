import patients
import appointments
valid = False
while not valid:
    choice = int(input("1. Add Patient\n2. Search Patient\n3. \n\n>>  "))
    if choice == 1:
        patients.enterpatientdetails()
    elif choice == 2:
        patients.searchPatient()
    else:
        print("Error")

