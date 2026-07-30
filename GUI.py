import customtkinter as ctk
import authentication
import Logging


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Dental Booking System")
        self.geometry("800x600")

        self.attempts = 0

        self.login_frame = LoginFrame(self)
        self.dashboard_frame = DashboardFrame(self)
        self.patient_frame = PatientFrame(self)
        self.appointment_frame = AppointmentFrame(self)
        self.recall_frame = RecallFrame(self)

        self.frames = [
            self.login_frame,
            self.dashboard_frame,
            self.patient_frame,
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
        self.username_entry = ctk.CTkEntry(
            self,
            placeholder_text="Username"
        )
        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*"
        )
        self.login_button = ctk.CTkButton(
            self,
            text="Login",
            command=self.login_pressed
        )
        self.error_label = ctk.CTkLabel(
            self,
            text="Username or password is incorrect",
            text_color="red"
        )
        self.locked_label = ctk.CTkLabel(
            self,
            text="Too many attempts. Restart application",
            text_color="red"
        )

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
        self.title_label = ctk.CTkLabel(self,text="Patient Management")
        self.search_entry = ctk.CTkEntry(self,placeholder_text="Patient Name")
        self.search_button = ctk.CTkButton(self,text="Search")
        self.back_button = ctk.CTkButton(self,text="Back",command=lambda:app.show_frame(app.dashboard_frame))

        self.title_label.pack(pady=20)
        self.search_entry.pack(pady=10)
        self.search_button.pack(pady=10)
        self.back_button.pack(pady=20)


class AppointmentFrame(ctk.CTkFrame):

    def __init__(self, app):

        super().__init__(app)

        ctk.CTkLabel(self,text="Appointment Management").pack(pady=20)

        ctk.CTkButton(self,text="Back",command=lambda:app.show_frame(app.dashboard_frame)).pack(pady=20)


class RecallFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)

        ctk.CTkLabel(self,text="Recall Management").pack(pady=20)

        ctk.CTkButton(self,text="Back",command=lambda:app.show_frame(app.dashboard_frame)).pack(pady=20)
app = App()
app.mainloop()