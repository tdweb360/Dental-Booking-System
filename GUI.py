import customtkinter as ctk
import authentication
import Logging
import patients
from tkinter import ttk

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
        self.appointment_frame = AppointmentFrame(self)
        self.recall_frame = RecallFrame(self)



        self.frames = [
            self.login_frame,
            self.dashboard_frame,
            self.patient_frame,
            self.patient_details_frame,
            self.appointment_frame,
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
            self.app.attempts = 0
            self.app.dashboard_frame.welcome_label.configure(text=f"Welcome {username}\nRole: {role}")
            self.app.show_frame(self.app.dashboard_frame)


class DashboardFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)

        self.app = app
        self.welcome_label = ctk.CTkLabel(self,text="Welcome")
        self.patient_button = ctk.CTkButton(self,text="Search Patient",command=self.open_patient_frame)
        self.appointment_button = ctk.CTkButton(self,text="Manage Appointments",command=self.open_appointment_frame)
        self.recall_button = ctk.CTkButton(self,text="View Recalls",command=self.open_recall_frame)
        self.logout_button = ctk.CTkButton(self,text="Logout",command=self.logout)

        self.welcome_label.pack(pady=20)
        self.patient_button.pack(pady=10)
        self.appointment_button.pack(pady=10)
        self.recall_button.pack(pady=10)
        self.logout_button.pack(pady=50)


    def open_patient_frame(self):
        self.app.show_frame(
            self.app.patient_frame
        )

    def open_appointment_frame(self):
        self.app.show_frame(
            self.app.appointment_frame
        )

    def open_recall_frame(self):
        self.app.show_frame(
            self.app.recall_frame
        )

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
        self.search_frame.pack(fill="x",padx=20,pady=10)
        self.results_title.pack(pady=(5, 0))
        self.results_frame.pack(fill="both",expand=True,padx=20,pady=10)
        self.bottom_frame = ctk.CTkFrame(self,fg_color="transparent")
        self.bottom_frame.pack(side="bottom",fill="x",pady=(0, 20))
        self.back_button = ctk.CTkButton(self.bottom_frame,text="Back",command=self.back)
        self.back_button.pack()


    def search_patient(self):
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
        if not results:
            no_results_label = ctk.CTkLabel(self.results_frame,text="No patients found",text_color="red")
            no_results_label.pack(pady=10)
            return
        for patient in results:
            self.create_patient_row(patient)
        self.results_title.configure(text=f"Search Results ({len(results)} found)")


    def create_patient_row(self, patient):

        row = ctk.CTkFrame(self.results_frame)
        row.pack(fill="x", pady=2)
        widths = [60, 120, 120, 120, 120]
        for col, value in enumerate(patient[:5]):
            ctk.CTkLabel(row,text=value,width=widths[col]).grid(row=0,column=col,padx=5)
        patient_id = patient[0]
        ctk.CTkButton(row,text="Open",width=80,command=lambda: self.open_patient(patient_id)).grid(row=0,column=5,padx=5)

    def open_patient(self, patient_id):
        print(patient_id)
        self.app.patient_details_frame.load_patient(patient_id)
        self.app.show_frame(self.app.patient_details_frame)

    def back(self):
        self.app.show_frame(self.app.dashboard_frame)

class PatientDetailsFrame(ctk.CTkFrame):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title_label = ctk.CTkLabel(self,text="Patient Details")
        self.patient_info = ctk.CTkLabel(self,text="")

        self.title_label.pack(pady=20)
        self.patient_info.pack(pady=20)

    def load_patient(self, patient_id):
        patient = patients.get_patient_by_id(
            patient_id
        )

        self.patient_info.configure(
            text=f"""
                ID: {patient[0]}
                Name: {patient[1]} {patient[2]}
                DOB: {patient[3]}
                Phone: {patient[4]}
                """
                    )

    def back(self):
        self.app.show_frame(self.app.patient_frame)

class AppointmentFrame(ctk.CTkFrame):

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        ctk.CTkLabel(self,text="Appointment Management").pack(pady=20)
        ctk.CTkButton(self,text="Back",command=self.back).pack(pady=20)

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