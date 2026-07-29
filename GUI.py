import customtkinter as ctk

import authentication


def loginButtonPressed():
    global attempts
    attempts = 0

    username = usernameEntry.get()
    password = passwordEntry.get()
    result = authentication.login(
        username,
        password
    )
    if result is None:

        attempts += 1
    else:
        staffID, role, username = result
        print("success")
        attempts = 0

app = ctk.CTk()

app.title("Dental Booking System")
app.geometry("800x600")

usernameEntry = ctk.CTkEntry(app,placeholder_text="Username")
passwordEntry = ctk.CTkEntry(app,placeholder_text="Password")
login_button = ctk.CTkButton(app,text="Login",command=loginButtonPressed)

usernameEntry.pack()
passwordEntry.pack()
login_button.pack()


app.mainloop()