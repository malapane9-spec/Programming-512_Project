"""
Smart Campus Resource Booking System
Programming 512 Assignment – Richfield Graduate Institution

Main entry point.
Run this file to start the application:
    python main.py
"""

import tkinter as tk
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from gui.login_window import LoginWindow
from gui.main_window import MainWindow


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide root window; we use Toplevels
        self.title("Smart Campus Resource Booking System")
        self.db = DatabaseManager()
        self.current_main = None
        self.show_login()

    def show_login(self):
        if self.current_main:
            self.current_main.destroy()
            self.current_main = None
        LoginWindow(self, self.db, self.on_login_success)

    def on_login_success(self, user):
        self.current_main = MainWindow(self, self.db, user)


if __name__ == "__main__":
    app = Application()
    app.mainloop()
