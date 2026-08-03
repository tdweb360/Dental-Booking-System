import customtkinter as ctk
import staff
import appointments
import authentication
import Logging
import patients

class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Dental Booking System")
        self.geometry("800x600")

        self.attempts = 0

        self.login_frame = LoginFrame(self)

        self.dashboard_frame = DashboardFrame(self)

        self.patient_frame = PatientFrame(self)
        self.patient_details_frame = PatientDetailsFrame(self)
        self.add_patient_frame = AddPatientFrame(self)
        self.existing_appointment_frame = ManageAppointmentFrame(self)
        self.new_appointment_frame = BookAppointmentFrame(self)
        self.recall_frame = RecallFrame(self)



        self.frames = [
            self.login_frame,
            self.dashboard_frame,
            self.patient_frame,
            self.patient_details_frame,
            self.add_patient_frame,
            self.existing_appointment_frame,
            self.new_appointment_frame,
            self.recall_frame
        ]

        self.show_frame(self.login_frame)

    def show_frame(self, frame):
        for f in self.frames:
            f.pack_forget()

        frame.pack(fill="both",expand=True)


class LoginFrame(ctk.CTkFrame):

    def __init__(self, app):
        super().__init__(app)

        self.app = app
        self.username_entry = ctk.CTkEntry(self,placeholder_text="Username")
        self.password_entry = ctk.CTkEntry(self,placeholder_text="Password",show="*")
        self.login_button = ctk.CTkButton(self,text="Login",command=self.login_pressed)
        self.error_label = ctk.CTkLabel(self,text="Username or password is incorrect",text_color="red")
        self.locked_label = ctk.CTkLabel(self,text="Too many attempts. Restart application",text_color="red")


        self.username_entry.pack(pady=10)
        self.password_entry.pack(pady=10)
        self.login_button.pack(pady=10)

    def login_pressed(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        self.error_label.pack_forget()

        if self.app.attempts >= 3:
            self.locked_label.pack(pady=20)
            Logging.log_action(
                username,
                "ACCOUNT_LOCKED",
                "Three failed login attempts"
            )

            return

        result = authentication.login(username,password)

        if result is None:
            self.app.attempts += 1
            self.error_label.pack(pady=5)

        else:
            staff_id, role, username = result
            self.app.current_user = username
            self.app.attempts = 0
            self.app.dashboard_frame.welcome_label.configure(text=f"Welcome {username}\nRole: {role}",font= ctk.CTkFont(size=30, weight="bold"))
            self.app.show_frame(self.app.dashboard_frame)


class DashboardFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)

        self.app = app
        self.welcome_label = ctk.CTkLabel(self,text="Welcome")
        self.patient_button = ctk.CTkButton(self,text="Search Patient",command=self.open_patient_frame)
        self.add_patient_button = ctk.CTkButton(self, text="Register New Patient", command=self.open_add_patient)
        self.appointment_button = ctk.CTkButton(self,text="Manage Appointments",command=self.open_appointment_frame)
        self.recall_button = ctk.CTkButton(self,text="View Recalls",command=self.open_recall_frame)
        self.logout_button = ctk.CTkButton(self,text="Logout",command=self.logout)

        self.welcome_label.pack(pady=20)
        self.patient_button.pack(pady=10)
        self.add_patient_button.pack(pady=10)
        self.appointment_button.pack(pady=10)
        self.recall_button.pack(pady=10)
        self.logout_button.pack(pady=50)


    def open_patient_frame(self):
        self.app.show_frame(self.app.patient_frame)

    def open_add_patient(self):
        self.app.show_frame(self.app.add_patient_frame)

    def open_appointment_frame(self):
        self.app.show_frame(self.app.existing_appointment_frame)

    def open_recall_frame(self):
        self.app.show_frame(self.app.recall_frame)

    def logout(self):

        login = self.app.login_frame

        login.username_entry.delete(0, "end")
        login.password_entry.delete(0, "end")

        login.error_label.pack_forget()
        login.locked_label.pack_forget()

        self.app.show_frame(self.app.login_frame)


class PatientFrame(ctk.CTkFrame):

    def __init__(self, app):
        super().__init__(app)
        self.app = app

        self.search_frame = ctk.CTkFrame(self)
        self.results_frame = ctk.CTkScrollableFrame(self,width=700,height=150)

        self.title_label = ctk.CTkLabel(self,text="Patient Management",font=ctk.CTkFont(size=35, weight="bold"))

        self.feedback_label = ctk.CTkLabel(self, text="")
        self.back_button = ctk.CTkButton(self,text="Back",command=self.back)
        self.search_button = ctk.CTkButton(self.search_frame,text="Search",command=self.search_patient)

        self.name_label = ctk.CTkLabel(self.search_frame,text="Search By Name")
        self.phone_label = ctk.CTkLabel(self.search_frame,text="Search By Phone")
        self.dob_label = ctk.CTkLabel(self.search_frame,text="Search By Date Of Birth")

        self.name_entry = ctk.CTkEntry(self.search_frame,placeholder_text="First or Last Name")
        self.phone_entry = ctk.CTkEntry(self.search_frame,placeholder_text="07123456789")
        self.dob_entry = ctk.CTkEntry(self.search_frame,placeholder_text="DD/MM/YYYY")

        self.search_frame.grid_columnconfigure(0, weight=1)
        self.search_frame.grid_columnconfigure(1, weight=1)
        self.search_frame.grid_columnconfigure(2, weight=1)

        self.results_title = ctk.CTkLabel(self,text="Search Results")


        self.name_label.grid(row=0,column=0,padx=20)
        self.phone_label.grid(row=0,column=1,padx=20)
        self.dob_label.grid(row=0,column=2,padx=20)

        self.name_entry.grid(row=1,column=0,padx=20,sticky="ew")
        self.phone_entry.grid(row=1,column=1,padx=20,sticky="ew")
        self.dob_entry.grid(row=1,column=2,padx=20,sticky="ew")
        self.search_button.grid(row=2,column=0,columnspan=3,pady=15)

        self.header = ctk.CTkFrame(self.results_frame, fg_color="#1F6AA5")
        self.header.pack(fill="x",pady=(0, 5))
        ctk.CTkLabel(self.header,text="ID",width=60).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(self.header,text="First Name",width=120).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(self.header,text="Surname",width=120).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(self.header,text="DOB",width=120).grid(row=0, column=3, padx=5)
        ctk.CTkLabel(self.header,text="Phone",width=120).grid(row=0, column=4, padx=5)

        self.title_label.pack(pady=20)
        self.feedback_label.pack()

        self.search_frame.pack(fill="x",padx=20,pady=10)
        self.results_title.pack(pady=(5, 0))
        self.results_frame.pack(fill="both",expand=True,padx=20,pady=10)
        self.bottom_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.bottom_frame.pack(side="bottom",fill="x",pady=(0, 20))
        self.back_button = ctk.CTkButton(self.bottom_frame,text="Back",command=self.back)
        self.back_button.pack()


    def search_patient(self):
        self.feedback_label.configure(text="")
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        dob = self.dob_entry.get().strip()

        results = patients.search_patients(name=name,phone=phone,dob=dob)
        if results == "INVALID_DATE":
            self.results_title.configure(text="Date must be DD/MM/YYYY")

            return

        for w in self.results_frame.winfo_children():
            if w != self.header:
                w.destroy()
        if len(results) == 0:
            no_results_label = ctk.CTkLabel(self.results_frame,text="No patients found",text_color="red")
            no_results_label.pack(pady=10)
            return
        for patient in results:
            self.create_patient_row(patient)
        self.results_title.configure(text=f"Search Results ({len(results)} found)")

    def refreshSearch(self):
        self.search_patient()
        self.feedback_label.configure(text="Patient deleted successfully",text_color="green",font=ctk.CTkFont(size=20, weight="bold"))

    def create_patient_row(self, patient):
        from functools import partial
        row = ctk.CTkFrame(self.results_frame)
        row.pack(fill="x", pady=2)
        widths = [60, 120, 120, 120, 120]
        for Count in range(5):
            ctk.CTkLabel(row,text=patient[Count],width=widths[Count]).grid(row=0,column=Count,padx=5)
        patient_id = patient[0]
        ctk.CTkButton(row,text="Open",width=80,command=partial(self.open_patient,patient_id)).grid(row=0, column=5, padx=5)

    def open_patient(self, patient_id):
        self.app.patient_details_frame.load_patient(patient_id)
        self.app.show_frame(self.app.patient_details_frame)

    def back(self):
        self.app.show_frame(self.app.dashboard_frame)


class PatientDetailsFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)

        self.app = app

        self.title_label = ctk.CTkLabel(self, text="Patient Details", font= ctk.CTkFont(size=30, weight="bold"))
        self.firstname_label = ctk.CTkLabel(self, text="First Name")
        self.firstname_entry = ctk.CTkEntry(self)
        self.surname_label = ctk.CTkLabel(self, text="Surname")
        self.surname_entry = ctk.CTkEntry(self)
        self.dob_label = ctk.CTkLabel(self, text="Date Of Birth")
        self.dob_entry = ctk.CTkEntry(self)
        self.phone_label = ctk.CTkLabel(self, text="Phone Number")
        self.phone_entry = ctk.CTkEntry(self)
        self.save_button = ctk.CTkButton(self, text="Save Changes",command=self.saveChanges)
        self.delete_button = ctk.CTkButton(self, text="Delete Patient",text_color="red",command=self.deletePatient)
        self.appointment_button = ctk.CTkButton(self, text="Book Appointment", command=self.openAppointmentScreen)
        self.back_button = ctk.CTkButton(self, text="Back", command=self.back)
        self.feedback_label = ctk.CTkLabel(self, text="")


        self.title_label.pack(pady=20)

        self.firstname_label.pack()
        self.firstname_entry.pack(pady=5)
        self.surname_label.pack()
        self.surname_entry.pack(pady=5)
        self.dob_label.pack()
        self.dob_entry.pack(pady=5)
        self.phone_label.pack()
        self.phone_entry.pack(pady=5)
        self.save_button.pack(pady=5)
        self.delete_button.pack(pady=5)
        self.appointment_button.pack(pady=5)
        self.feedback_label.pack(pady=5)

        self.back_button.pack(pady=20)

    def load_patient(self, patient_id):
        from datetime import datetime
        self.patient_id = patient_id
        patient = patients.get_patient_by_id(patient_id)
        self.firstname_entry.delete(0, "end")
        self.firstname_entry.insert(0, patient[1])
        self.surname_entry.delete(0, "end")
        self.surname_entry.insert(0, patient[2])
        self.dob_entry.delete(0, "end")
        dob = datetime.strptime(patient[3],"%Y-%m-%d").strftime("%d/%m/%Y")
        self.dob_entry.insert(0, dob)
        self.phone_entry.delete(0, "end")
        self.phone_entry.insert(0, patient[4])

    def saveChanges(self):
        firstname = self.firstname_entry.get().strip()
        surname = self.surname_entry.get().strip()
        dob = self.dob_entry.get().strip()
        phone = self.phone_entry.get().strip()
        result = patients.updatePatient(self.patient_id,firstname,surname,dob,phone,self.app.current_user)

        if result == "SUCCESS":
            self.feedback_label.configure(text="Patient updated successfully",text_color="green")
        elif result == "INVALID_NAME":
            self.feedback_label.configure(text="Invalid first name or surname",text_color="red")
        elif result == "INVALID_DOB":
            self.feedback_label.configure(text="Date must be DD/MM/YYYY",text_color="red")
        elif result == "INVALID_PHONE":
            self.feedback_label.configure(text="Phone number format is invalid",text_color="red")
        else:
            self.feedback_label.configure(text="Database error",text_color="red")

    def openAppointmentScreen(self):
        self.app.new_appointment_frame.loadPatient(self.patient_id)
        self.app.show_frame(self.app.new_appointment_frame)

    def deletePatient(self):
        self.confirm_window = ctk.CTkToplevel(self)
        self.confirm_window.title("Confirm Delete")
        self.confirm_window.geometry("300x150")

        self.confirm_window.lift()
        self.confirm_window.focus_force()
        self.confirm_window.grab_set()
        self.confirm_window.resizable(False, False)

        ctk.CTkLabel(self.confirm_window, text="Are you sure you want to delete this patient?").pack(pady=20)
        ctk.CTkButton(self.confirm_window, text="Yes", command=self.confirmDelete).pack(pady=5)
        ctk.CTkButton(self.confirm_window, text="No", command=self.confirm_window.destroy).pack(pady=5)

    def confirmDelete(self):
        success = patients.deletePatient(self.patient_id, self.app.current_user)
        if success:
            self.confirm_window.destroy()
            self.app.patient_frame.refreshSearch()
            self.app.show_frame(self.app.patient_frame)
        else:
            self.feedback_label.configure(text="Error deleting patient", text_color="red")

    def back(self):
        self.app.show_frame(self.app.patient_frame)

class AddPatientFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        ctk.CTkLabel(self, text="Add Patient", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)
        self.firstname_label = ctk.CTkLabel(self, text="First Name")
        self.firstname_entry = ctk.CTkEntry(self)
        self.surname_label = ctk.CTkLabel(self, text="Surname")
        self.surname_entry = ctk.CTkEntry(self)
        self.dob_label = ctk.CTkLabel(self, text="Date Of Birth")
        self.dob_entry = ctk.CTkEntry(self)
        self.phone_label = ctk.CTkLabel(self, text="Phone Number")
        self.phone_entry = ctk.CTkEntry(self)
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.register_button = ctk.CTkButton(self, text="Register Patient", command=self.registerPatient)
        ctk.CTkButton(self,text="Back",command=self.back).pack(pady=20)

        self.firstname_label.pack()
        self.firstname_entry.pack(pady=5)

        self.surname_label.pack()
        self.surname_entry.pack(pady=5)

        self.dob_label.pack()
        self.dob_entry.pack(pady=5)

        self.phone_label.pack()
        self.phone_entry.pack(pady=5)
        self.register_button.pack(pady=10)
        self.feedback_label.pack(pady=5)

    def registerPatient(self):

        firstname = self.firstname_entry.get().strip()
        surname = self.surname_entry.get().strip()
        dob = self.dob_entry.get().strip()
        phone = self.phone_entry.get().strip()

        result = patients.addPatient(firstname,surname,dob,phone,self.app.current_user)
        if result == "SUCCESS":
            self.feedback_label.configure(text="Patient registered successfully", text_color="green")
            self.clearFields()
        elif result == "INVALID_NAME":
            self.feedback_label.configure(text="Invalid first name or surname", text_color="red")
        elif result == "INVALID_DOB":
            self.feedback_label.configure(text="Date must be DD/MM/YYYY", text_color="red")
        elif result == "INVALID_PHONE":
            self.feedback_label.configure(text="Phone number format is invalid", text_color="red")
        else:
            self.feedback_label.configure(text="Database error", text_color="red")

    def clearFields(self):
        self.firstname_entry.delete(0, "end")
        self.surname_entry.delete(0, "end")
        self.dob_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")


    def back(self):
        self.app.show_frame(self.app.dashboard_frame)

class BookAppointmentFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)

        self.app = app
        self.selected_slot = None

        ctk.CTkLabel(self, text="Book Appointment", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)

        self.patient_label = ctk.CTkLabel(self, text="",font=ctk.CTkFont(size=15))
        self.date_entry = ctk.CTkEntry(self, placeholder_text="DD/MM/YYYY")
        self.duration_menu = ctk.CTkOptionMenu(self, values=["15", "30", "45", "60"])
        self.search_button = ctk.CTkButton(self, text="Check Availability", command=self.checkDay)
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.results_frame = ctk.CTkScrollableFrame(self, width=300, height=250)
        self.selected_slot_label = ctk.CTkLabel(self, text="Selected Slot: None")
        self.book_button = ctk.CTkButton(self, text="Book Appointment", command=self.bookAppointment)
        self.staff_menu = ctk.CTkOptionMenu(self, values=["Select Staff"])

        self.staff_lookup = {}
        StaffMembers = staff.getAllStaff()
        Names = []
        for e in StaffMembers:
            StaffID = e[0]
            FullName = e[1] + " " + e[2]

            Names.append(FullName)
            self.staff_lookup[FullName] = StaffID
        self.staff_menu.configure(values=Names)

        self.patient_label.pack()
        self.date_entry.pack(pady=5)
        self.duration_menu.pack(pady=5)
        self.staff_menu.pack(pady=5)
        self.search_button.pack(pady=5)
        self.feedback_label.pack()
        self.results_frame.pack(pady=5)
        self.selected_slot_label.pack()
        self.book_button.pack(pady=7)
        ctk.CTkButton(self,text="Back",command=self.back).pack(padx=20)

    def loadPatient(self, patient_id):
        self.patient_id = patient_id
        patient = patients.get_patient_by_id(patient_id)
        self.patient_label.configure(text=f"{patient[1]} {patient[2]}")

    def chooseSlot(self, slot):
        self.selected_slot = slot
        self.selected_slot_label.configure(
            text=f"Selected Slot: {slot}")

    def checkDay(self):
        from datetime import datetime, timedelta
        from functools import partial

        all_slots = [
            "09:00","09:15","09:30","09:45",
            "10:00","10:15","10:30","10:45",
            "11:00","11:15","11:30","11:45",
            "12:00","12:15","12:30","12:45",
            "13:00","13:15","13:30","13:45",
            "14:00","14:15","14:30","14:45",
            "15:00","15:15","15:30","15:45",
            "16:00","16:15","16:30","16:45"
        ]
        #clear prev results
        for w in self.results_frame.winfo_children():
            w.destroy()
        date = self.date_entry.get().strip()
        if not appointments.validateAppointmentDate(date):
            self.feedback_label.configure(text="Invalid date",text_color="red")
            return

        self.feedback_label.configure(text="")
        selectedStaff = self.staff_menu.get()
        if selectedStaff == "Select Staff":
            self.feedback_label.configure(text="Select a staff member",text_color="red")
            return
        staffID = self.staff_lookup[selectedStaff]
        results = appointments.getAppointmentsByDateAndStaff(date,staffID)
        booked_slots = []
        for appointment in results:
            start_time = datetime.strptime(appointment[0],"%H:%M")
            duration = appointment[1]
            slots_needed = duration // 15
            for Count in range(slots_needed):
                slot_time = start_time + timedelta(minutes=Count * 15)
                booked_slots.append(slot_time.strftime("%H:%M"))
        ctk.CTkLabel(self.results_frame,text="Time        Status",font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        #available in green and clickable, booked not clickable
        for slot in all_slots:
            if slot in booked_slots:
                ctk.CTkLabel(self.results_frame,text=f"{slot}    BOOKED",text_color="red").pack(pady=2)
            else:
                #pass slot val to chooseSlot when click
                button = ctk.CTkButton(self.results_frame,text=f"{slot} AVAILABLE",fg_color="green",command=partial(self.chooseSlot, slot))
                button.pack(pady=2)

    def bookAppointment(self):
        if self.selected_slot == None:
            self.feedback_label.configure(text="Select a slot first",text_color="red")
            return
        date = self.date_entry.get().strip()
        selectedStaff = self.staff_menu.get()
        if selectedStaff == "Select Staff":
            self.feedback_label.configure(text="Select a staff member",text_color="red")
            return
        staffID = self.staff_lookup[selectedStaff]
        duration = int(self.duration_menu.get())
        selectedStaff = self.staff_menu.get()
        staffID = self.staff_lookup[selectedStaff]
        result = appointments.createAppointment(self.patient_id,staffID,date,self.selected_slot,duration,self.app.current_user)
        if result == "SUCCESS":
            self.feedback_label.configure(text="Appointment Booked Successfully",text_color="green")
            self.back()
        else:
            self.feedback_label.configure(text="Appointment could not be booked", text_color="red")

    def back(self):
        self.app.show_frame(self.app.dashboard_frame)

class ManageAppointmentFrame(ctk.CTkFrame):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        ctk.CTkLabel(self,text="Appointment Management").pack(pady=20)
        ctk.CTkButton(self,text="Back",command=self.back).pack(pady=20)

    def createAppointment(patientID, date, time):
        pass
    def getAppointmentsByPatient(patientID):
        pass
    def deleteAppointment(appointmentID):
        pass
    def updateAppointment(appointmentID, date, time):
        pass

    def back(self):
        self.app.show_frame(self.app.dashboard_frame)




class RecallFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        ctk.CTkLabel(self,text="Recall Management").pack(pady=20)
        ctk.CTkButton(self,text="Back",command=self.back).pack(pady=20)

    def back(self):
        self.app.show_frame(self.app.dashboard_frame)
app = App()
app.mainloop()