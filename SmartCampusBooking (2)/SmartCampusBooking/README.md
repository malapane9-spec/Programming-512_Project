# Smart Campus Resource Booking System

**Programming 512 Assignment – Richfield Graduate Institution**

A complete Python application that allows lecturers, campus administrators and system operators to manage and book shared academic resources across multiple campuses.

## Features

- **Three user roles** (OOP with inheritance & encapsulation):
  - **Lecturer** – register, login, book resources, view/cancel own bookings
  - **Campus Administrator** – manage resources, view campus bookings & reports
  - **System Operator** – full system access, cross-campus comparison reports

- **Three campuses** with different booking policies:
  | Campus              | Max Duration | Allowed Hours |
  |---------------------|--------------|---------------|
  | Johannesburg        | 2 hours      | 08:00 – 17:00 |
  | Cape Town           | 3 hours      | 07:00 – 19:00 |
  | Durban              | 4 hours      | 08:00 – 18:00 |

- Tkinter GUI (login, registration, role-based dashboards)
- SQLite persistence (users, campuses, resources, bookings)
- Overlap prevention, input validation, error handling
- Campus-level and cross-campus reporting

## How to Run

```bash
# From the project folder
python main.py
```

**Default System Operator account**
- Username: `operator`
- Password: `operator123`

Register new Lecturer or Campus Administrator accounts from the Login window.

## Project Structure

```
SmartCampusBooking/
├── main.py                 # Entry point
├── database/
│   └── db_manager.py       # SQLite operations & seeding
├── models/
│   ├── user.py             # User hierarchy (Lecturer, Admin, Operator)
│   └── booking_rules.py    # Campus-specific policies (extensible)
├── gui/
│   ├── login_window.py     # Login & registration
│   └── main_window.py      # Role-based main application
└── README.md
```

## Requirements

- Python 3.8+
- Standard library only (tkinter, sqlite3) – no external packages needed

## Notes for Markers

- All data persists between runs via SQLite (`database/campus_booking.db`)
- Booking rules are isolated in `models/booking_rules.py` for easy extension
- Code is commented and structured for readability
- Input validation and overlap checking are implemented
"""
