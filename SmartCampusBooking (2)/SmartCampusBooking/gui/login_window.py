"""
Login and Registration window (Tkinter).
Clear Login form + prominent Register button.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models.user import create_user_from_dict


class LoginWindow(tk.Toplevel):
    def __init__(self, parent, db, on_success):
        super().__init__(parent)
        self.db = db
        self.on_success = on_success
        self.title("Smart Campus Resource Booking – Login")
        self.geometry("450x520")
        self.resizable(False, False)
        self.configure(bg="#f0f4f8")

        # Centre the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 225
        y = (self.winfo_screenheight() // 2) - 260
        self.geometry(f"+{x}+{y}")

        self._mode = "login"  # or "register"
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg="#1a365d", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Smart Campus Resource Booking",
            font=("Segoe UI", 14, "bold"), fg="white", bg="#1a365d"
        ).pack(pady=20)

        # Content area (switched between login and register)
        self.content = tk.Frame(self, bg="#f0f4f8")
        self.content.pack(fill="both", expand=True, padx=25, pady=15)

        self._show_login()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ------------------------------------------------------------------ LOGIN VIEW
    def _show_login(self):
        self._mode = "login"
        self._clear_content()

        tk.Label(
            self.content, text="Login to your account",
            font=("Segoe UI", 13, "bold"), bg="#f0f4f8", fg="#1a365d"
        ).pack(pady=(10, 20))

        tk.Label(self.content, text="Username", font=("Segoe UI", 10), bg="#f0f4f8").pack(anchor="w")
        self.login_user = ttk.Entry(self.content, width=35, font=("Segoe UI", 11))
        self.login_user.pack(pady=(2, 12), ipady=3)

        tk.Label(self.content, text="Password", font=("Segoe UI", 10), bg="#f0f4f8").pack(anchor="w")
        self.login_pass = ttk.Entry(self.content, width=35, show="•", font=("Segoe UI", 11))
        self.login_pass.pack(pady=(2, 18), ipady=3)
        self.login_pass.bind("<Return>", lambda e: self._do_login())

        # Login button
        tk.Button(
            self.content, text="Login", command=self._do_login,
            bg="#2b6cb0", fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", width=20, height=1, cursor="hand2",
            activebackground="#2c5282"
        ).pack(pady=5)

        # Demo tip
        tk.Label(
            self.content,
            text="Demo account:  operator  /  operator123",
            font=("Segoe UI", 8), fg="#666", bg="#f0f4f8"
        ).pack(pady=(15, 25))

        # Separator
        ttk.Separator(self.content, orient="horizontal").pack(fill="x", pady=5)

        # Prominent Register section
        tk.Label(
            self.content, text="Don't have an account?",
            font=("Segoe UI", 10), bg="#f0f4f8", fg="#333"
        ).pack(pady=(15, 8))

        tk.Button(
            self.content, text="Register New Account", command=self._show_register,
            bg="#38a169", fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", width=22, height=1, cursor="hand2",
            activebackground="#2f855a"
        ).pack(pady=5)

    # ------------------------------------------------------------------ REGISTER VIEW
    def _show_register(self):
        self._mode = "register"
        self._clear_content()

        tk.Label(
            self.content, text="Create a new account",
            font=("Segoe UI", 13, "bold"), bg="#f0f4f8", fg="#1a365d"
        ).pack(pady=(5, 12))

        tk.Label(self.content, text="Full Name", font=("Segoe UI", 10), bg="#f0f4f8").pack(anchor="w")
        self.reg_name = ttk.Entry(self.content, width=35, font=("Segoe UI", 11))
        self.reg_name.pack(pady=(2, 8), ipady=2)

        tk.Label(self.content, text="Username", font=("Segoe UI", 10), bg="#f0f4f8").pack(anchor="w")
        self.reg_user = ttk.Entry(self.content, width=35, font=("Segoe UI", 11))
        self.reg_user.pack(pady=(2, 8), ipady=2)

        tk.Label(self.content, text="Password", font=("Segoe UI", 10), bg="#f0f4f8").pack(anchor="w")
        self.reg_pass = ttk.Entry(self.content, width=35, show="•", font=("Segoe UI", 11))
        self.reg_pass.pack(pady=(2, 8), ipady=2)

        tk.Label(self.content, text="Role", font=("Segoe UI", 10), bg="#f0f4f8").pack(anchor="w")
        self.reg_role = ttk.Combobox(
            self.content, values=["lecturer", "admin"], state="readonly", width=33
        )
        self.reg_role.set("lecturer")
        self.reg_role.pack(pady=(2, 8), ipady=2)
        self.reg_role.bind("<<ComboboxSelected>>", self._on_role_change)

        # Campus (only for admin) – create and place in a fixed slot
        self.campus_frame = tk.Frame(self.content, bg="#f0f4f8")
        tk.Label(self.campus_frame, text="Campus (required for Admin)", font=("Segoe UI", 10), bg="#f0f4f8").pack(anchor="w")
        campuses = self.db.get_all_campuses()
        self.campus_names = {c["name"]: c["campus_id"] for c in campuses}
        self.reg_campus = ttk.Combobox(
            self.campus_frame, values=list(self.campus_names.keys()), state="readonly", width=33
        )
        if self.campus_names:
            self.reg_campus.current(0)
        self.reg_campus.pack(pady=(2, 5), ipady=2)

        # Buttons frame (always at bottom of form)
        self.btn_frame = tk.Frame(self.content, bg="#f0f4f8")
        self.btn_frame.pack(pady=(12, 5))

        tk.Button(
            self.btn_frame, text="Register", command=self._do_register,
            bg="#38a169", fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", width=20, height=1, cursor="hand2",
            activebackground="#2f855a"
        ).pack(pady=4)

        tk.Button(
            self.btn_frame, text="← Back to Login", command=self._show_login,
            bg="#718096", fg="white", font=("Segoe UI", 9),
            relief="flat", width=18, cursor="hand2"
        ).pack(pady=4)

    def _on_role_change(self, event=None):
        if self.reg_role.get() == "admin":
            # Pack campus_frame just above the buttons
            self.campus_frame.pack(fill="x", pady=(0, 5), before=self.btn_frame)
        else:
            self.campus_frame.pack_forget()

    def _do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password.")
            return
        user_data = self.db.authenticate_user(username, password)
        if user_data:
            user = create_user_from_dict(user_data)
            self.destroy()
            self.on_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def _do_register(self):
        full_name = self.reg_name.get().strip()
        username = self.reg_user.get().strip()
        password = self.reg_pass.get()
        role = self.reg_role.get()

        if not full_name or not username or not password:
            messagebox.showwarning("Input Error", "All fields are required.")
            return
        if len(password) < 4:
            messagebox.showwarning("Input Error", "Password must be at least 4 characters.")
            return

        campus_id = None
        if role == "admin":
            campus_name = self.reg_campus.get()
            if not campus_name:
                messagebox.showwarning("Input Error", "Please select a campus for the administrator.")
                return
            campus_id = self.campus_names[campus_name]

        success, msg = self.db.register_user(username, password, full_name, role, campus_id)
        if success:
            messagebox.showinfo("Success", msg + "\nYou can now log in.")
            self._show_login()
        else:
            messagebox.showerror("Registration Failed", msg)

    def _on_close(self):
        self.master.destroy()
