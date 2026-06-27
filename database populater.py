import sqlite3
from datetime import datetime
import random

connect = sqlite3.connect('database.db')
cursor = connect.cursor()

firstnames = ["Tom", "Dan", "Alex", "Sam", "Jamie", "Chris", "Taylor"]
surnames = ["Smith", "Brown", "Webster", "Jones", "Taylor", "Wilson"]

for i in range(20):  # creates 20 patients
    firstname = random.choice(firstnames)
    surname = random.choice(surnames)

    # random date of birth
    year = random.randint(1970, 2010)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # safe so no invalid dates

    date_of_birth = f"{year:04d}-{month:02d}-{day:02d}"

    # random UK-style phone number
    phone = "07" + "".join(str(random.randint(0,9)) for _ in range(9))


    cursor.execute("""
    INSERT INTO Patients_Table (FirstName, Surname, Date_of_birth, Phone_Num)
    VALUES (?, ?, ?, ?)
    """, (firstname, surname, date_of_birth, phone))

connect.commit()
connect.close()

print("✅ Database populated with test patients")
