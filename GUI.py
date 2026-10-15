
# main GUI window, every other file branches off of this file

import customtkinter as ctk
import staff
import appointments
import authentication
import Logging
import patients
import Recalls
import database
from datetime import datetime

class PagedFrame(ctk.CTkFrame):
    empty_message = "No records found"

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.current_page = 1
        self.records_per_page = 10
        self.results = []
        self.results_frame = None
        self.page_label = None

    def buildNavigation(self):
        self.navigation_frame = ctk.CTkFrame(self)
        self.navigation_frame.pack(side="bottom",pady=10)
        ctk.CTkButton(self.navigation_frame, text="Previous", command= self.previousPage).pack(side="left",pady=10)
        self.page_label = ctk.CTkLabel(self.navigation_frame, text="Page 1")
        self.page_label.pack(side="left",padx=10)
        ctk.CTkButton(self.navigation_frame, text="Next",command=self.nextPage).pack(side="left", padx=10)

    def getTotalPages(self):
        return max(1, (len(self.results) + self.records_per_page -1) // self.records_per_page)

    def displayResults(self):
        for w in self.results_frame.winfo_children():
            w.destroy()
        self.page_label.configure(text=f"Page {self.current_page} of {self.getTotalPages()}")
        if len(self.results) == 0:
            ctk.CTkLabel(self.results_frame,text=self.empty_message, text_color="#F52727").pack(pady=20)
            return
        start = (self.current_page -1) * self.records_per_page
        end = start + self.records_per_page
        for r in self.results[start:end]:
            self.createRow(r)

    def createRow(self,record):
        raise NotImplementedError("Subclasses must overriide create row")

    def nextPage(self):
        if self.current_page < self.getTotalPages():
            self.current_page +=1
            self.displayResults()
    def previousPage(self):
        if self.current_page> 1:
            self.current_page = self.current_page -1
            self.displayResults()

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Dental Booking System")

        self.after(10, self.maximiseWindow)


        staff.createInitialManager()
        self.attempts = 0

        self.loginFrame = LoginFrame(self)

        self.dashboardFrame = DashboardFrame(self)

        self.patient_frame = PatientFrame(self)
        self.patientDetails_frame = PatientDetailsFrame(self)
        self.add_patient_frame = AddPatientFrame(self)
        self.manageAppointment_Frame = ManageAppointmentFrame(self)
        self.new_appointment_frame = BookAppointmentFrame(self)
        self.appointmentDetails_frame = AppointmentDetailsFrame(self)
        self.staff_frame = StaffManagementFrame(self)
        self.staffDetails_frame = StaffDetailsFrame(self)
        self.recall_frame = RecallFrame(self)
        self.audit_frame = AuditLogFrame(self)



        self.frames = [
            self.loginFrame,
            self.dashboardFrame,
            self.patient_frame,
            self.patientDetails_frame,
            self.add_patient_frame,
            self.manageAppointment_Frame,
            self.new_appointment_frame,
            self.appointmentDetails_frame,
            self.staff_frame,
            self.staffDetails_frame,
            self.recall_frame,
            self.audit_frame
        ]

        self.show_frame(self.loginFrame)

    def maximiseWindow(self):
        self.state("zoomed")

    def show_frame(self, frame):
        for f in self.frames:
            f.pack_forget()

        frame.pack(fill="both",expand=True)

# all code relating to the login page
class LoginFrame(ctk.CTkFrame):

    def __init__(self, app):
        super().__init__(app)

        self.app = app
        self.username_entry = ctk.CTkEntry(self,placeholder_text="Username")
        self.password_entry = ctk.CTkEntry(self,placeholder_text="Password",show="*")
        self.login_button = ctk.CTkButton(self,text="Login",command=self.login_pressed)
        self.error_label = ctk.CTkLabel(self,text="Username or password is incorrect",text_color="red")
        self.locked_label = ctk.CTkLabel(self,text="Too many attempts. Restart application",text_color="red")

        top_padding = (self.app.winfo_screenheight() // 4) - (self.app.winfo_screenheight() // 16)
        self.username_entry.pack(pady=(top_padding, 10))
        self.password_entry.pack(pady=10)
        self.login_button.pack(pady=10)

    def login_pressed(self):

        username = self.username_entry.get()
        password = self.password_entry.get()

        self.error_label.pack_forget()

        if self.app.attempts >= 3:
            self.locked_label.pack(pady=20)

            return

        result = authentication.login(username,password)

        if result is None:
            self.app.attempts += 1
            if self.app.attempts >= 3:
                self.locked_label.pack(pady=20)
                Logging.log_action(username, "ACCOUNT_LOCKED", "Three failed login attempts")
            else:
                self.error_label.pack(pady=5)

        else:
            staff_id, role, username = result
            self.app.current_staff_id = staff_id
            self.app.current_role = role
            if role == "Manager":
                self.app.dashboardFrame.staff_button.pack(pady=10)
                self.app.dashboardFrame.audit_button.pack(pady = 10)
            else:
                self.app.dashboardFrame.staff_button.pack_forget()
                self.app.dashboardFrame.audit_button.pack_forget()

            self.app.current_user = username
            self.app.attempts = 0
            self.app.dashboardFrame.welcome_label.configure(text=f"Welcome {username}\nRole: {role}",font= ctk.CTkFont(size=30, weight="bold"))
            self.app.show_frame(self.app.dashboardFrame)

# all code relating to the main dashboard
class DashboardFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)

        self.app = app
        self.welcome_label = ctk.CTkLabel(self,text="Welcome")
        self.patient_button = ctk.CTkButton(self,text="Search Patient",command=self.open_patient_frame)
        self.add_patient_button = ctk.CTkButton(self, text="Register New Patient", command=self.open_add_patient)
        self.appointment_button = ctk.CTkButton(self,text="Manage Appointments",command=self.open_appointment_frame)
        self.recall_button = ctk.CTkButton(self,text="View Recalls",command=self.open_recall_frame)
        self.staff_button = ctk.CTkButton(self,text="Staff Management",command=self.open_staff_frame)
        self.audit_button = ctk.CTkButton(self, text="Audit Log",command=self.open_audit_frame)

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
        self.app.manageAppointment_Frame.loadAllAppointments()
        self.app.show_frame(self.app.manageAppointment_Frame)

    def open_staff_frame(self):
        self.app.show_frame(self.app.staff_frame)

    def open_recall_frame(self):
        self.app.recall_frame.loadRecalls()
        self.app.show_frame(self.app.recall_frame)

    def open_audit_frame(self):
        if self.app.current_role != "Manager":
            return
        self.app.audit_frame.loadLogs()
        self.app.show_frame(self.app.audit_frame)

    def logout(self):

        login = self.app.loginFrame

        login.username_entry.delete(0, "end")
        login.password_entry.delete(0, "end")
        login.error_label.pack_forget()
        login.locked_label.pack_forget()
        self.app.show_frame(self.app.loginFrame)


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

        self.bottom_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.bottom_frame.pack(side="bottom",fill="x",pady=(0, 20))
        self.back_button = ctk.CTkButton(self.bottom_frame,text="Back",command=self.back)
        self.search_frame.pack(fill="x",padx=20,pady=10)
        self.results_title.pack(pady=(5, 0))
        self.results_frame.pack(fill="both",expand=True,padx=20,pady=10)

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
            self.results_title.configure(text="Search Results (0 found)")
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
            text = patient[Count]
            if Count == 3:
                text = datetime.strptime(patient[3],"%Y-%m-%d").strftime("%d/%m/%Y")
            ctk.CTkLabel(row,text=text,width=widths[Count]).grid(row=0, column=Count, padx=5)
        patientID = patient[0]
        ctk.CTkButton(row,text="Open",width=80,command=partial(self.open_patient,patientID)).grid(row=0, column=5, padx=5)

    def open_patient(self, patientID):
        self.app.patientDetails_frame.load_patient(patientID)
        self.app.show_frame(self.app.patientDetails_frame)

    def back(self):
        self.app.show_frame(self.app.dashboardFrame)


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

    def load_patient(self, patientID):
        from datetime import datetime
        self.patientID = patientID
        patient = patients.get_patient_by_id(patientID)
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
        result = patients.updatePatient(self.patientID,firstname,surname,dob,phone,self.app.current_user)

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
        self.app.new_appointment_frame.loadPatient(self.patientID)
        self.app.show_frame(self.app.new_appointment_frame)

    def deletePatient(self):
        self.confirm_window = ctk.CTkToplevel(self)
        self.confirm_window.title("Confirm Delete")
        self.confirm_window.geometry("350x230")

        self.confirm_window.lift()
        self.confirm_window.focus_force()
        self.confirm_window.grab_set()
        self.confirm_window.resizable(False, False)
        firstname = self.firstname_entry.get()
        surname = self.surname_entry.get()
        ctk.CTkLabel(
            self.confirm_window,
            text=(
                f"Are you sure you want to delete:\n\n"
                f"{firstname} {surname}\n"
                f"Patient ID: {self.patientID}\n\n"
                f"All appointments will also be deleted.\n"
                f"This action cannot be undone.")).pack(pady=20)
        ctk.CTkButton(self.confirm_window, text="Yes", command=self.confirmDelete).pack(pady=5)
        ctk.CTkButton(self.confirm_window, text="No", command=self.confirm_window.destroy).pack(pady=5)

    def confirmDelete(self):
        success = patients.deletePatient(self.patientID, self.app.current_user)
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
        ctk.CTkButton(self,text="Back",command=self.back).pack(pady=20)

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
        self.app.show_frame(self.app.dashboardFrame)

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

        self.loadStaffMembers()

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

    def loadStaffMembers(self):
        self.staff_lookup = {}
        names = []
        for member in staff.getAllStaff():
            fullName = member[1] + " " + member[2]
            names.append(fullName)
            self.staff_lookup[fullName] = member[0]
        self.staff_menu.configure(values=names)
#

    def loadPatient(self, patientID):
        self.selected_slot = None
        self.selected_slot_label.configure(text="Selected Slot: None")
        self.feedback_label.configure(text="")
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.loadStaffMembers()
        self.patientID = patientID
        patient = patients.get_patient_by_id(patientID)
        self.patient_label.configure(text=f"{patient[1]} {patient[2]}")

    def chooseSlot(self, slot):
        self.selected_slot = slot
        self.selected_slot_label.configure(text=f"Selected Slot: {slot}")

    def checkDay(self):
        from datetime import datetime, timedelta
        from functools import partial
        self.selected_slot = None
        self.selected_slot_label.configure(text="Selected Slot: None")
        for w in self.results_frame.winfo_children():
            w.destroy()
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
        date = self.date_entry.get().strip()
        result = appointments.validateAppointmentDate(date)
        if result == "WRONG FORMAT":
            self.feedback_label.configure(text="Date must be DD/MM/YYYY",text_color="red")
            return
        elif result == "PAST DATE":
            self.feedback_label.configure(text="Date cannot be in the past",text_color="red")
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
        selectedDuration = int(
            self.duration_menu.get())
        slotsNeeded = selectedDuration // 15
        ctk.CTkLabel(self.results_frame,text="Time        Status",font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        #available in green and clickable, booked not clickable
        for Position in range(len(all_slots)):
            slot = all_slots[Position]
            Available = True
            for Count in range(slotsNeeded):
                CurrentPosition = Position + Count
                if CurrentPosition >= len(all_slots):
                    Available = False
                else:
                    CurrentSlot = all_slots[CurrentPosition]
                    if CurrentSlot in booked_slots:
                        Available = False
            if Available:
                button = ctk.CTkButton(self.results_frame,text=f"{slot} AVAILABLE",fg_color="green",command=partial(self.chooseSlot,slot ))
                button.pack(pady=2)
            else:
                ctk.CTkLabel(self.results_frame,text=f"{slot} BOOKED",text_color="red").pack(pady=2)

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
        result = appointments.createAppointment(self.patientID,staffID,date,self.selected_slot,duration,self.app.current_user)
        if result == "SUCCESS":
            self.checkDay()
            self.feedback_label.configure(text="Appointment Booked Successfully",text_color="green",font=ctk.CTkFont(size=18, weight="bold"))
        elif result == "END OF DAY":
            self.feedback_label.configure(text="Appointment could not be booked, must be during opening hours (09:00-17:00)", text_color="red",font=ctk.CTkFont(size=18, weight="bold"))
        elif result == "WRONG FORMAT":
            self.feedback_label.configure(text="Appointment must be in DD/MM/YYYY", text_color="red",font=ctk.CTkFont(size=18, weight="bold"))
        elif result == "PAST DATE":
            self.feedback_label.configure(text="Appointment must not be a date in the past", text_color="red",font=ctk.CTkFont(size=18, weight="bold"))
        elif result == "STAFF CONFLICT":
            self.feedback_label.configure(text="Staff member already booked at this time",text_color="red")
        elif result == "PATIENT CONFLICT":
            self.feedback_label.configure(text="Patient already has an appointment at this time",text_color="red")
        else:
            self.feedback_label.configure(text="Appointment could not be booked", text_color="red",font=ctk.CTkFont(size=18, weight="bold"))

    def back(self):
        self.app.show_frame(self.app.dashboardFrame)

class ManageAppointmentFrame(PagedFrame):
    def __init__(self, app):
        super().__init__(app)

        self.app = app

        self.current_page = 1
        self.records_per_page = 10
        self.results = []

        ctk.CTkLabel(self, text="Appointment Management", font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)

        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.search_frame, text="Patient Name").grid(row=0, column=0, padx=10)
        ctk.CTkLabel(self.search_frame, text="Date").grid(row=0, column=1, padx=10)

        self.patient_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Patient Name")
        self.date_entry = ctk.CTkEntry(self.search_frame, placeholder_text="DD/MM/YYYY")

        self.patient_entry.grid(row=1, column=0, padx=10)
        self.date_entry.grid(row=1, column=1, padx=10)

        ctk.CTkButton(self.search_frame, text="Search", command=self.searchAppointments).grid(row=1, column=2, padx=10)
        ctk.CTkButton(self.search_frame, text="Show All", command=self.loadAllAppointments).grid(row=1, column=3, padx=10)

        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x", padx=20)
        ctk.CTkLabel(self.header, text="ID", width=60).pack(side="left", padx=5)
        ctk.CTkLabel(self.header, text="Date", width=120).pack(side="left", padx=5)
        ctk.CTkLabel(self.header, text="Time", width=100).pack(side="left", padx=5)
        ctk.CTkLabel(self.header, text="Patient", width=180).pack(side="left", padx=5)
        ctk.CTkLabel(self.header, text="Staff", width=180).pack(side="left", padx=5)
        ctk.CTkLabel(self.header, text="Duration", width=100).pack(side="left",padx= 5)
        self.feedback_label = ctk.CTkLabel(self,text="")
        self.feedback_label.pack()

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", pady=(0, 20))
        self.back_button = ctk.CTkButton(self.bottom_frame, text="Back", command=self.back)
        self.back_button.pack()

        self.navigation_frame = ctk.CTkFrame(self)
        self.navigation_frame.pack(side="bottom", pady=10)
        ctk.CTkButton(self.navigation_frame, text="Previous", command=self.previousPage).pack(side="left", padx=10)
        self.page_label = ctk.CTkLabel(self.navigation_frame, text="Page 1")
        self.page_label.pack(side="left", padx=10)
        ctk.CTkButton(self.navigation_frame, text="Next", command=self.nextPage).pack(side="left", padx=10)

        self.results_frame = ctk.CTkScrollableFrame(self, width=1000, height=500)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.loadAllAppointments()

    def loadAllAppointments(self):
        self.patient_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.results = appointments.getAllAppointments()
        self.current_page = 1
        self.displayResults()

    def createRow(self, appointment):
        row = ctk.CTkFrame(self.results_frame)
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=appointment[0], width=60).pack(side="left", padx=5)
        formattedDate = datetime.strptime(appointment[1], "%Y-%m-%d").strftime("%d/%m/%Y")
        ctk.CTkLabel(row, text=formattedDate, width=120).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=appointment[2], width=100).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=appointment[3], width=180).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=appointment[4], width=180).pack(side="left", padx=5)
        ctk.CTkLabel(row, text=f"{appointment[5]} mins", width=100).pack(side="left", padx=5)
        self.emptyMessage = "No active recalls"


    def openAppointment(self, appointmentID):
        self.app.appointmentDetails_frame.loadAppointment(appointmentID)
        self.app.show_frame(self.app.appointmentDetails_frame)


    def searchAppointments(self):
        patient = self.patient_entry.get().strip()
        date = self.date_entry.get().strip()
        self.results = appointments.searchAppointments(patient, date)
        self.current_page = 1
        self.displayResults()

    def back(self):
        self.app.show_frame(self.app.dashboardFrame)

class AppointmentDetailsFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)

        self.app = app

        ctk.CTkLabel(self,text="Appointment Details",font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)

        ctk.CTkLabel(self, text="Date").pack()
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.pack(pady=5)
        ctk.CTkLabel(self, text="Time").pack()
        self.time_entry = ctk.CTkEntry(self)
        self.time_entry.pack(pady=5)
        ctk.CTkLabel(self, text="Duration").pack()
        self.duration_menu = ctk.CTkOptionMenu(self, values=["15", "30", "45", "60"])
        self.duration_menu.pack(pady=5)
        ctk.CTkLabel(self, text="Staff").pack()
        self.staff_menu = ctk.CTkOptionMenu(self, values=["Select Staff"])
        self.staff_menu.pack(pady=5)
        self.feedback_label = ctk.CTkLabel(self, text="")
        self.feedback_label.pack(pady=5)
        self.save_button = ctk.CTkButton(self,text="Save Changes", command=self.updateAppointment)
        self.save_button.pack(pady=5)
        self.delete_button = ctk.CTkButton(self,text="Cancel Appointment",command=self.deleteAppointment)
        self.delete_button.pack(pady=5)
        self.bottom_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.bottom_frame.pack(side="bottom",fill="x",pady=(0, 20))
        ctk.CTkButton(self.bottom_frame,text="Back",command=self.back).pack()
        self.staff_lookup = {}

    def loadStaffMembers(self):
        self.staff_lookup = {}
        names = []
        for member in staff.getAllStaff():
            fullName = member[1] + " " + member[2]
            names.append(fullName)
            self.staff_lookup[fullName] = member[0]
        self.staff_menu.configure(values=names)

    def loadAppointment(self, appointmentID):
        self.appointmentID = appointmentID
        self.loadStaffMembers()

        appointment = appointments.getAppointmentByID(appointmentID)
        self.patientID = appointment[3]
        self.staffID = appointment[4]
        member = staff.getStaffByID(self.staffID)
        self.staff_menu.set(f"{member[1]} {member[2]}")
        formattedDate = datetime.strptime(appointment[1],"%Y-%m-%d").strftime("%d/%m/%Y")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, formattedDate)
        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, appointment[2])
        self.duration_menu.set(str(appointment[5]))

    def updateAppointment(self):

        date = self.date_entry.get().strip()
        time = self.time_entry.get().strip()
        duration = int(self.duration_menu.get())
        selectedStaff = self.staff_menu.get()
        staffID = self.staff_lookup[selectedStaff]
        result = appointments.editAppointment(self.appointmentID,date,time,duration,self.patientID,staffID,self.app.current_user)

        if result == "SUCCESSFUL":
            self.feedback_label.configure(text="Appointment updated successfully",text_color="green")
            self.app.manageAppointment_Frame.loadAllAppointments()

        elif result == "WRONG FORMAT":
            self.feedback_label.configure(text="Date must be DD/MM/YYYY",text_color="red")

        elif result == "PAST DATE":
            self.feedback_label.configure(text="Date cannot be in the past",text_color="red")

        elif result == "INVALID TIME":
            self.feedback_label.configure(text="Time must be HH:MM",text_color="red" )
        elif result == "END OF DAY":
            self.feedback_label.configure(text="Appointment could not be booked, must be during opening hours (09:00-17:00)", text_color="red")

        elif result == "STAFF CONFLICT":
            self.feedback_label.configure(text="Staff member already booked at this time",text_color="red")

        elif result == "PATIENT CONFLICT":
            self.feedback_label.configure(text="Patient already has an appointment at this time",text_color="red")
        else:
            self.feedback_label.configure(text="Database error",text_color="red")

    def deleteAppointment(self):
        self.confirm_window = ctk.CTkToplevel(self)
        self.confirm_window.title("Confirm Delete")
        self.confirm_window.geometry("380x250")
        self.confirm_window.lift()
        self.confirm_window.focus_force()
        self.confirm_window.grab_set()
        self.confirm_window.resizable(False, False)

        date = self.date_entry.get()
        time = self.time_entry.get()
        duration = self.duration_menu.get()

        ctk.CTkLabel(
            self.confirm_window,
            text=(
                f"Are you sure you want to delete:\n\n"
                f"Appointment ID: {self.appointmentID}\n"
                f"Date: {date}\n"
                f"Time: {time}\n"
                f"Duration: {duration} mins\n\n"
                f"This action cannot be undone." )).pack(pady=20)
        ctk.CTkButton(self.confirm_window, text="Yes", command=self.confirmDelete).pack(pady=5)
        ctk.CTkButton(self.confirm_window, text="No", command=self.confirm_window.destroy).pack(pady=5)

    def confirmDelete(self):
        success = appointments.deleteAppointment(self.appointmentID,self.app.current_user)
        if success:
            self.confirm_window.destroy()
            self.app.manageAppointment_Frame.loadAllAppointments()
            self.app.manageAppointment_Frame.feedback_label.configure(text="Appointment cancelled successfully",text_color="green")
            self.app.show_frame(self.app.manageAppointment_Frame)
        else:
            self.feedback_label.configure(text="Error deleting appointment", text_color="red")


    def back(self):
        self.app.show_frame(self.app.manageAppointment_Frame)

class StaffManagementFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)
        self.app = app
        self.title_label = ctk.CTkLabel(self,text="Staff Management",font=ctk.CTkFont(size=30,weight="bold"))
        self.content_frame = ctk.CTkFrame(self)
        self.add_frame = ctk.CTkFrame(self.content_frame)
        self.search_frame = ctk.CTkFrame(self.content_frame)
        self.add_title = ctk.CTkLabel(self.add_frame,text="Add New Staff",font=ctk.CTkFont(size=22,weight="bold"))
        self.firstname_entry = ctk.CTkEntry(self.add_frame,placeholder_text="First Name")
        self.surname_entry = ctk.CTkEntry(self.add_frame,placeholder_text="Surname")
        self.username_entry = ctk.CTkEntry(self.add_frame,placeholder_text="Username")
        self.password_entry = ctk.CTkEntry(self.add_frame,placeholder_text="Password",show="*")
        self.reenter_password_entry = ctk.CTkEntry(self.add_frame,placeholder_text="Confirm Password",show="*")
        self.role_menu = ctk.CTkOptionMenu(self.add_frame,values=["Dentist","Receptionist","Manager"])
        self.register_button = ctk.CTkButton(self.add_frame,text="Register",command=self.registerStaffMember)
        self.feedback_label = ctk.CTkLabel(self.add_frame,text="")
        self.search_title = ctk.CTkLabel(self.search_frame,text="Search Staff",font=ctk.CTkFont(size=22,weight="bold"))
        self.search_controls = ctk.CTkFrame(self.search_frame,fg_color="transparent")
        self.search_entry = ctk.CTkEntry(self.search_controls,placeholder_text="Search Name")
        self.search_button = ctk.CTkButton(self.search_controls,text="Search",command=self.searchStaff)
        self.results_frame = ctk.CTkScrollableFrame(self.search_frame)
        self.back_button = ctk.CTkButton(self,text="Back",command=self.back)
        self.title_label.pack(pady=20)
        self.content_frame.pack(fill="both",expand=True,padx=20,pady=10)
        self.content_frame.grid_columnconfigure(0,weight=2)
        self.content_frame.grid_columnconfigure(1,weight=3)
        self.add_frame.grid(row=0,column=0,sticky="nsew",padx=(0,10))
        self.search_frame.grid(row=0,column=1,sticky="nsew",padx=(10,0))
        self.add_title.pack(pady=15)
        self.firstname_entry.pack(fill="x",padx=20,pady=5)
        self.surname_entry.pack(fill="x",padx=20,pady=5)
        self.username_entry.pack(fill="x",padx=20,pady=5)
        self.password_entry.pack(fill="x",padx=20,pady=5)
        self.reenter_password_entry.pack(fill="x",padx=20,pady=5)
        self.role_menu.pack(fill="x",padx=20,pady=10)
        self.register_button.pack(pady=10)
        self.feedback_label.pack(pady=5)
        self.search_title.pack(pady=15)
        self.search_controls.pack(fill="x",padx=20,pady=10)
        self.search_entry.pack(side="left",fill="x",expand=True,padx=(0,10))
        self.search_button.pack(side="left")
        self.results_header = ctk.CTkFrame(self.search_frame)
        self.results_header.pack(fill="x", padx=20)
        ctk.CTkLabel(self.results_header, text="Name", width=180).pack(side="left", padx=10)
        ctk.CTkLabel(self.results_header, text="Username", width=150).pack(side="left", padx=10)
        ctk.CTkLabel(self.results_header, text="Role", width=120).pack(side="left", padx=10)
        self.results_frame.pack(fill="both",expand=True,padx=20,pady=10)
        self.back_button.pack(pady=20)

    def registerStaffMember(self):
        firstN = self.firstname_entry.get().strip()
        surN = self.surname_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        renterPass = self.reenter_password_entry.get().strip()
        role = self.role_menu.get()
        result = staff.addStaffGUI(firstN,surN,username,password,renterPass,role,self.app.current_user)
        if result == "SUCCESS":
            self.feedback_label.configure(text="Staff member registered successfully",text_color="green")
            self.clearFields()
        elif result == "INVALID FIRST NAME OR SURNAME":
            self.feedback_label.configure(text="Invalid first name or surname",text_color="red")
        elif result == "INVALID USERNAME":
            self.feedback_label.configure(text="Invalid or duplicate username",text_color="red")
        elif result == "PASSWORD LENGTH":
            self.feedback_label.configure(text="Password must be at least 8 characters",text_color="red")
        elif result == "PASSWORD UPPERCASE":
            self.feedback_label.configure(text="Password must contain an uppercase letter",text_color="red")
        elif result == "PASSWORD LOWERCASE":
            self.feedback_label.configure(text="Password must contain a lowercase letter",text_color="red")
        elif result == "PASSWORD NUMBER":
            self.feedback_label.configure(text="Password must contain a number",text_color="red")
        elif result == "PASSWORD SPECIAL":
            self.feedback_label.configure(text="Password must contain a special character",text_color="red")
        elif result == "PASSWORD MATCH":
            self.feedback_label.configure(text="Passwords do not match",text_color="red")
        else:
            self.feedback_label.configure(text="Database error",text_color="red")

    def clearFields(self):

        self.firstname_entry.delete(0, "end")
        self.surname_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.reenter_password_entry.delete(0, "end")

        self.role_menu.set("Dentist")

    def searchStaff(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        name = self.search_entry.get().strip()
        results = staff.searchStaffName(name)
        if len(results) == 0:
            ctk.CTkLabel(self.results_frame,text="No staff members found",text_color="red").pack(pady=10)
            return

        from functools import partial

        for member in results:
            row = ctk.CTkFrame(self.results_frame)
            row.pack(fill="x",pady=2)
            ctk.CTkLabel(row,text=f"{member[1]} {member[2]}",width=180).pack(side="left",padx=10)
            ctk.CTkLabel(row,text=member[3],width=150).pack(side="left",padx=10)
            ctk.CTkLabel(row,text=member[5],width=120).pack(side="left",padx=10)
            ctk.CTkButton(row,text="Open",command=partial(self.openStaff,member[0])).pack(side="right",padx=10)

    def openStaff(self, staffID):
        self.app.staffDetails_frame.loadStaff(staffID)
        self.app.show_frame(self.app.staffDetails_frame)
    def back(self):
        self.app.show_frame(self.app.dashboardFrame)


class StaffDetailsFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title_label = ctk.CTkLabel(self,text="Staff Details",font=ctk.CTkFont(size=30,weight="bold"))
        self.firstname_label = ctk.CTkLabel(self,text="First Name")
        self.firstname_entry = ctk.CTkEntry(self)
        self.surname_label = ctk.CTkLabel(self,text="Surname")
        self.surname_entry = ctk.CTkEntry(self)
        self.username_label = ctk.CTkLabel(self,text="Username")
        self.username_entry = ctk.CTkEntry(self)
        self.role_label = ctk.CTkLabel(self,text="Role")
        self.role_menu = ctk.CTkOptionMenu(self,values=["Dentist","Receptionist","Manager"])
        self.save_button = ctk.CTkButton(self,text="Save Changes",command=self.saveChanges)
        self.reset_button = ctk.CTkButton(self,text="Reset Password",command=self.resetPassword)
        self.delete_button = ctk.CTkButton(self,text="Delete Staff",fg_color="#B22222",hover_color="#8B1A1A",command=self.deleteStaff)
        self.feedback_label = ctk.CTkLabel(self,text="")
        self.back_button = ctk.CTkButton(self,text="Back",command=self.back)
        self.title_label.pack(pady=20)
        self.firstname_label.pack()
        self.firstname_entry.pack(pady=5)
        self.surname_label.pack()
        self.surname_entry.pack(pady=5)
        self.username_label.pack()
        self.username_entry.pack(pady=5)
        self.role_label.pack()
        self.role_menu.pack(pady=5)
        self.save_button.pack(pady=10)
        self.reset_button.pack(pady=5)
        self.delete_button.pack(pady=5)
        self.feedback_label.pack(pady=10)
        self.back_button.pack(pady=20)

    def loadStaff(self, staffID):
        self.staffID = staffID
        member = staff.getStaffByID(staffID)
        self.firstname_entry.delete(0, "end")
        self.firstname_entry.insert(0, member[1])
        self.surname_entry.delete(0, "end")
        self.surname_entry.insert(0, member[2])
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, member[3])
        self.role_menu.set(member[5])

    def saveChanges(self):
        firstname = self.firstname_entry.get().strip()
        surname = self.surname_entry.get().strip()
        username = self.username_entry.get().strip()
        role = self.role_menu.get()
        result = staff.updateStaff(self.staffID,firstname,surname,username,role,self.app.current_user)

        if result == "SUCCESS":
            self.feedback_label.configure(text="Staff updated successfully",text_color="green")
            if self.staffID == self.app.current_staff_id:
                self.app.current_user = username
                self.app.current_role = role
        elif result == "INVALID_NAME":
            self.feedback_label.configure(text="Invalid name",text_color="red")
        elif result == "INVALID_USERNAME":
            self.feedback_label.configure(text="Username already exists",text_color="red")
        else:
            self.feedback_label.configure(text="Database error",text_color="red")

    def deleteStaff(self):
        self.confirm_window = ctk.CTkToplevel(self)
        self.confirm_window.title("Confirm Delete")
        self.confirm_window.geometry("350x220")

        self.confirm_window.lift()
        self.confirm_window.focus_force()
        self.confirm_window.grab_set()
        self.confirm_window.resizable(False, False)

        firstname = self.firstname_entry.get()
        surname = self.surname_entry.get()
        username = self.username_entry.get()
        ctk.CTkLabel(
            self.confirm_window,
            text=(
                f"Are you sure you want to delete:\n\n"
                f"{firstname} {surname}\n"
                f"Username: {username}\n"
                f"Staff ID: {self.staffID}\n\n"
                f"This action cannot be undone.")).pack(pady=20)
        ctk.CTkButton(self.confirm_window, text="Yes", command=self.confirmDelete).pack(pady=5)
        ctk.CTkButton(self.confirm_window, text="No", command=self.confirm_window.destroy).pack(pady=5)

    def confirmDelete(self):
        result = staff.deleteStaff(self.staffID, self.app.current_user)
        if result == "SUCCESS":
            self.app.staff_frame.searchStaff()
            self.app.staff_frame.feedback_label.configure(text="Staff member deleted successfully",text_color="green")
            self.app.show_frame(self.app.staff_frame)
        elif result == "HAS_APPOINTMENTS":
            self.feedback_label.configure(text="Staff member has appointments and cannot be deleted",text_color="red")
        elif result == "OWN_ACCOUNT":
            self.feedback_label.configure(text="You cannot delete your own account",text_color="red")
        else:
            self.feedback_label.configure(text="Error deleting staff member",text_color="red")
        self.confirm_window.destroy()


    def resetPassword(self):
        self.popup = ctk.CTkToplevel(self)
        self.popup.title("Reset Password")
        self.newpassword_entry = ctk.CTkEntry(self.popup,placeholder_text="Password",show="*")
        self.confirm_entry = ctk.CTkEntry(self.popup,placeholder_text="Confirm Password",show="*")
        self.newpassword_entry.pack(pady=5)
        self.confirm_entry.pack(pady=5)
        ctk.CTkButton(self.popup,text="Reset Password",command=self.submit).pack(pady=10)

    def submit(self):

        result = staff.resetPasswordGUI(self.staffID,self.newpassword_entry.get().strip(),self.confirm_entry.get().strip(),self.app.current_user)

        if result == "SUCCESS":
            self.feedback_label.configure(text="Password reset successfully",text_color="green")
            self.popup.destroy()
        elif result == "PASSWORD LENGTH":
            self.feedback_label.configure(text="Password must be at least 8 characters",text_color="red")
        elif result == "PASSWORD UPPERCASE":
            self.feedback_label.configure(text="Password must contain an uppercase letter",text_color="red")
        elif result == "PASSWORD LOWERCASE":
            self.feedback_label.configure(text="Password must contain a lowercase letter",text_color="red")
        elif result == "PASSWORD NUMBER":
            self.feedback_label.configure(text="Password must contain a number",text_color="red")
        elif result == "PASSWORD SPECIAL":
            self.feedback_label.configure(text="Password must contain a special character",text_color="red")
        elif result == "PASSWORD MATCH":
            self.feedback_label.configure(text="Passwords do not match",text_color="red")
        else:
            self.feedback_label.configure(text="Database error",text_color="red")

    def back(self):
        self.app.show_frame(self.app.staff_frame)

class RecallFrame(PagedFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.current_page = 1
        self.records_per_page = 10
        self.results = []

        ctk.CTkLabel(self,text="Recall Management",font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)

        self.back_button = ctk.CTkButton(self,text="Back",command=self.back)
        self.back_button.pack(side="bottom",pady=20)

        self.navigation_frame = ctk.CTkFrame(self)
        self.navigation_frame.pack(side="bottom",pady=10)
        ctk.CTkButton(self.navigation_frame,text="Previous",command=self.previousPage).pack(side="left",padx=10)
        self.page_label = ctk.CTkLabel(self.navigation_frame,text="Page 1")
        self.page_label.pack(side="left",padx=10)
        ctk.CTkButton(self.navigation_frame,text="Next",command=self.nextPage).pack(side="left",padx=10)

        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x",padx=20)
        ctk.CTkLabel(self.header,text="Recall ID",width=80).pack(side="left")
        ctk.CTkLabel(self.header,text="Patient",width=200).pack(side="left")
        ctk.CTkLabel(self.header,text="Suggested Date",width=140).pack(side="left")
        ctk.CTkLabel(self.header,text="Priority",width=120).pack(side="left")

        self.results_frame = ctk.CTkScrollableFrame(self, width=900, height=500)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def loadRecalls(self, keepPage=False):
        self.results = Recalls.getActiveRecalls()
        if not keepPage:
            self.current_page = 1
        totalPages = max(1, (len(self.results) + self.records_per_page - 1) // self.records_per_page)
        if self.current_page > totalPages:
            self.current_page = totalPages
        self.displayResults()

    def displayResults(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        totalPages = max(1, (len(self.results) + self.records_per_page - 1) // self.records_per_page)
        self.page_label.configure(text=f"Page {self.current_page} of {totalPages}")

        if len(self.results) == 0:
            ctk.CTkLabel(self.results_frame,text="No active recalls").pack(pady=20)
            return


    def nextPage(self):
        if self.current_page * self.records_per_page < len(self.results):
            self.current_page += 1
            self.displayResults()

    def previousPage(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.displayResults()

    def createRow(self, recallData):

        from functools import partial

        recallID = recallData[0]
        patientID = recallData[1]
        name = f"{recallData[2]} {recallData[3]}"
        priority = recallData[5]

        suggestedDate = datetime.strptime(recallData[4],"%Y-%m-%d").strftime("%d/%m/%Y")

        row = ctk.CTkFrame(self.results_frame)
        row.pack(fill="x", pady=2)

        ctk.CTkLabel(row,text=recallID,width=80).pack(side="left", padx=5)
        ctk.CTkLabel(row,text=name,width=200).pack(side="left", padx=5)
        ctk.CTkLabel(row,text=suggestedDate,width=140).pack(side="left", padx=5)
        priority_menu = ctk.CTkOptionMenu(row,values=["1", "2", "3", "4", "5"])
        priority_menu.set(str(priority))
        ctk.CTkButton(row,text="Book",command=partial(self.bookRecall,patientID)).pack(side="right", padx=5)
        ctk.CTkButton(row,text="Complete",command=partial(self.completeRecall,recallID)).pack(side="right", padx=5)
        priority_menu.pack(side="left", padx=5)
        ctk.CTkButton(row,text="Save",width=60,command=partial(self.savePriority,recallID,priority_menu )).pack(side="right", padx=5)

    def bookRecall(self, patientID):
        from datetime import timedelta
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%d/%m/%Y")
        self.app.new_appointment_frame.loadPatient(patientID)
        self.app.new_appointment_frame.date_entry.delete(0,"end")

        self.app.new_appointment_frame.date_entry.insert(0,tomorrow)
        self.app.show_frame(self.app.new_appointment_frame)

    def completeRecall(self, recallID):
        Recalls.completeRecall(recallID)
        self.loadRecalls(keepPage=True)

    def savePriority(self, recallID, priority_menu):
        priority = int(priority_menu.get())
        Recalls.updatePriority(recallID,priority)
        self.loadRecalls(keepPage=True)


    def back(self):
        self.app.show_frame(self.app.dashboardFrame)

class AuditLogFrame(PagedFrame):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.current_page = 1
        self.records_per_page = 10
        self.results = []

        ctk.CTkLabel(self,text="Audit Log",font=ctk.CTkFont(size=30, weight="bold")).pack(pady=20)
        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x", padx=20)
        ctk.CTkLabel(self.header,text="User",width=140).pack(side="left")
        ctk.CTkLabel(self.header,text="Action",width=150).pack(side="left")
        ctk.CTkLabel(self.header,text="Details",width=300).pack(side="left")
        ctk.CTkLabel(self.header,text="Timestamp",width=180).pack(side="left")

        self.bottom_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.bottom_frame.pack(side="bottom",fill="x",pady=(0, 20))

        self.buildNavigation()

        self.results_frame = ctk.CTkScrollableFrame(self,width=1000,height=500)
        self.results_frame.pack(fill="both",expand=True,padx=20,pady=10)


    def loadLogs(self):
        self.results = Logging.getAuditLogs()
        self.current_page = 1
        self.displayResults()


    def createRow(self,log):
        row = ctk.CTkFrame(self.results_frame)
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row,text=log[1],width=140).pack(side="left")
        ctk.CTkLabel(row,text=log[2],width=150).pack(side="left")
        ctk.CTkLabel( row,text=log[3],width=300).pack(side="left")
        ctk.CTkLabel(row,text=log[4],width=180).pack(side="left")

    def back(self):
        self.app.show_frame(self.app.dashboardFrame)
app = App()
app.mainloop()