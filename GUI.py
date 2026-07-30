import customtkinter as ctk

import authentication
import Logging

attempts = 0

## LOGIN FRAMES ##

def loginButtonPressed():
    global attempts
    username = usernameEntry.get()
    password = passwordEntry.get()
    if attempts >= 3:
        locked_out_label.pack(pady=50)
        error_message.pack_forget()
        Logging.log_action(
            username,
            "ACCOUNT_LOCKED",
            "Three failed login attempts"
        )
        return
    else:
        result = authentication.login(username, password)
        error_message.pack_forget()
        if result is None:
            attempts += 1
            error_message.pack()
        else:
            staffID, role, username = result
            attempts = 0
            login_frame.pack_forget()
            welcomeLabel.configure(text=f"Welcome {username}\nRole: {role}")
            dashboardFrame.pack(fill="both", expand=True)


def logout():
    dashboardFrame.pack_forget()
    error_message.pack_forget()
    usernameEntry.delete(0, "end")
    passwordEntry.delete(0, "end")
    login_frame.pack(fill="both", expand=True)


## PATIENTS FRAMES ##

def searchPatientPressed()


## APPOINTMENT FRAMES ##


## RECALLS FRAMES


app = ctk.CTk()
app.title("Dental Booking System")
app.geometry("800x600")

# login frame
login_frame = ctk.CTkFrame(app)
usernameEntry = ctk.CTkEntry(login_frame,placeholder_text="Username")
passwordEntry = ctk.CTkEntry(login_frame,placeholder_text="Password",show="*")
login_button = ctk.CTkButton(login_frame,text="Login",command=loginButtonPressed)
error_message = ctk.CTkLabel(login_frame,text="Username or password is incorrect",text_color="red")
locked_out_label = ctk.CTkLabel(login_frame,text="Too many attempts. Restart the application",text_color="red")

# dashboard frame
dashboardFrame = ctk.CTkFrame(app)
welcomeLabel = ctk.CTkLabel(dashboardFrame,text="Welcome")
logout_button = ctk.CTkButton(dashboardFrame,text="Logout",command=logout)
searchPatient_Button = ctk.CTkButton(dashboardFrame,text="Search Patient", command=searchPatientPressed)

# display widgets
login_frame.pack(fill="both",expand=True)
usernameEntry.pack(pady=10)
passwordEntry.pack(pady=10)
login_button.pack(pady=10)
welcomeLabel.pack(pady=30)
logout_button.pack(pady=50)


app.mainloop()