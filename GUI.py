import customtkinter as ctk
import authentication
import Logging

attempts = 0

app = ctk.CTk()
app.title("Dental Booking System")
app.geometry("800x600")

def hide_all_frames():
    login_frame.pack_forget()
    dashboard_frame.pack_forget()
    patient_frame.pack_forget()
    appointment_frame.pack_forget()
    recall_frame.pack_forget()

def show_frame(frame):
    hide_all_frames()
    frame.pack(fill="both", expand=True)


def login_button_pressed():
    global attempts
    username = username_entry.get()
    password = password_entry.get()
    error_label.pack_forget()
    if attempts == 3:
        locked_out_label.pack(pady=20)
        Logging.log_action(
            username,
            "ACCOUNT_LOCKED",
            "Three failed login attempts"
        )
        return

    result = authentication.login(username,password)

    if result is None:
        attempts += 1
        error_label.pack(pady=5)
    else:
        staff_id, role, username = result
        attempts = 0
        welcome_label.configure(text=f"Welcome {username}\nRole: {role}")
        show_frame(dashboard_frame)

def logout():
    username_entry.delete(0, "end")
    password_entry.delete(0, "end")
    error_label.pack_forget()
    locked_out_label.pack_forget()
    show_frame(login_frame)


# dashboard

def search_patient_pressed():
    show_frame(patient_frame)
def manage_appointment_pressed():
    show_frame(appointment_frame)
def view_recalls_pressed():
    show_frame(recall_frame)
def back_to_dashboard():
    show_frame(dashboard_frame)

# login frame

def create_login_frame():
    frame = ctk.CTkFrame(app)
    username = ctk.CTkEntry(frame,placeholder_text="Username")
    password = ctk.CTkEntry(frame,placeholder_text="Password",show="*")

    login_button = ctk.CTkButton(frame,text="Login",command=login_button_pressed)

    error = ctk.CTkLabel(frame,text="Username or password is incorrect",text_color="red")
    locked = ctk.CTkLabel(frame,text="Too many attempts. Restart the application",text_color="red")

    username.pack(pady=10)
    password.pack(pady=10)
    login_button.pack(pady=10)

    return frame, username, password, error, locked


# dashboard frame

def create_dashboard_frame():
    frame = ctk.CTkFrame(app)
    welcome = ctk.CTkLabel(frame,text="Welcome")
    search_button = ctk.CTkButton(frame,text="Search Patient",command=search_patient_pressed)
    appointment_button = ctk.CTkButton(frame,text="Manage Appointments",command=manage_appointment_pressed)
    recall_button = ctk.CTkButton(frame,text="View Recalls",command=view_recalls_pressed)
    logout_button = ctk.CTkButton(frame,text="Logout",command=logout)

    welcome.pack(pady=20)
    search_button.pack(pady=10)
    appointment_button.pack(pady=10)
    recall_button.pack(pady=10)
    logout_button.pack(pady=50)

    return frame, welcome


# patient frame

def create_patient_frame():
    frame = ctk.CTkFrame(app)
    title = ctk.CTkLabel(frame,text="Patient Management")
    search_label = ctk.CTkLabel(frame,text="Search Patient")

    search_entry = ctk.CTkEntry(frame,placeholder_text="Patient Name")

    search_button = ctk.CTkButton(frame,text="Search",command=search_patient)
    back_button = ctk.CTkButton(frame,text="Back",command=back_to_dashboard)

    title.pack(pady=20)
    search_label.pack(pady=20)
    search_entry.pack(pady=20)
    search_button.pack(pady=5)
    back_button.pack(pady=20)

    return frame, search_entry

def search_patient():
    name = search_entry.get()

# appointment frame
def create_appointment_frame():
    frame = ctk.CTkFrame(app)
    title = ctk.CTkLabel(frame,text="Appointment Management")
    back_button = ctk.CTkButton(frame,text="Back",command=back_to_dashboard)

    title.pack(pady=20)
    back_button.pack(pady=20)

    return frame

def create_recall_frame():
    frame = ctk.CTkFrame(app)
    title = ctk.CTkLabel(frame,text="Recall Management")
    back_button = ctk.CTkButton(frame,text="Back",command=back_to_dashboard)

    title.pack(pady=20)
    back_button.pack(pady=20)

    return frame

# Create Frames

(login_frame,username_entry,password_entry,error_label,locked_out_label) = create_login_frame()

(dashboard_frame,welcome_label) = create_dashboard_frame()
patient_frame, search_entry = create_patient_frame()
appointment_frame = create_appointment_frame()
recall_frame = create_recall_frame()
show_frame(login_frame)

app.mainloop()