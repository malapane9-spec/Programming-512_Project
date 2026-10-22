"""
Database Manager - Handles all SQLite operations for the Smart Campus Resource Booking System.
All data persists between program runs.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campus_booking.db")


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.seed_initial_data()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create all required tables if they do not exist."""
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('lecturer', 'admin', 'operator')),
                campus_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
            );

            CREATE TABLE IF NOT EXISTS campuses (
                campus_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                location TEXT NOT NULL,
                max_duration_hours REAL NOT NULL,
                booking_start_hour INTEGER NOT NULL,
                booking_end_hour INTEGER NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS resources (
                resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                campus_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                capacity INTEGER DEFAULT 1,
                description TEXT,
                UNIQUE(campus_id, name),
                FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
            );

            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                campus_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                duration_hours REAL NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'cancelled', 'completed')),
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
            );
        """)
        self.conn.commit()

    def seed_initial_data(self):
        """Insert default campuses, a system operator, and sample resources if empty."""
        self.cursor.execute("SELECT COUNT(*) FROM campuses")
        if self.cursor.fetchone()[0] == 0:
            campuses = [
                ("Johannesburg Campus", "Johannesburg, Gauteng", 2.0, 8, 17,
                 "Max 2 hours per booking. Bookings only 08:00-17:00."),
                ("Cape Town Campus", "Cape Town, Western Cape", 3.0, 7, 19,
                 "Max 3 hours per booking. Bookings only 07:00-19:00."),
                ("Durban Campus", "Durban, KwaZulu-Natal", 4.0, 8, 18,
                 "Max 4 hours per booking. Bookings only 08:00-18:00."),
            ]
            self.cursor.executemany(
                "INSERT INTO campuses (name, location, max_duration_hours, booking_start_hour, booking_end_hour, description) VALUES (?, ?, ?, ?, ?, ?)",
                campuses
            )
            self.conn.commit()

        # Default system operator (username: operator / password: operator123)
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'operator'")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO users (username, password, full_name, role, campus_id) VALUES (?, ?, ?, ?, ?)",
                ("operator", "operator123", "System Operator", "operator", None)
            )
            self.conn.commit()

        # Sample resources for each campus
        self.cursor.execute("SELECT COUNT(*) FROM resources")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("SELECT campus_id, name FROM campuses")
            campus_map = {row["name"]: row["campus_id"] for row in self.cursor.fetchall()}

            resources = [
                (campus_map["Johannesburg Campus"], "Computer Lab A", "Computer Laboratory", 30, "30 PCs with dual monitors"),
                (campus_map["Johannesburg Campus"], "Multimedia Projector 1", "Projector", 1, "Epson high-lumen projector"),
                (campus_map["Johannesburg Campus"], "Seminar Room 101", "Seminar Room", 20, "Boardroom style seating"),
                (campus_map["Cape Town Campus"], "Computer Lab B", "Computer Laboratory", 25, "25 iMacs"),
                (campus_map["Cape Town Campus"], "Auditorium", "Auditorium", 100, "Main lecture auditorium"),
                (campus_map["Cape Town Campus"], "Presentation Kit", "Presentation Equipment", 1, "Laptop + wireless mic + clicker"),
                (campus_map["Durban Campus"], "Computer Lab C", "Computer Laboratory", 40, "40 Windows workstations"),
                (campus_map["Durban Campus"], "Seminar Room 201", "Seminar Room", 15, "Interactive whiteboard"),
                (campus_map["Durban Campus"], "Multimedia Projector 2", "Projector", 1, "Portable laser projector"),
            ]
            self.cursor.executemany(
                "INSERT INTO resources (campus_id, name, resource_type, capacity, description) VALUES (?, ?, ?, ?, ?)",
                resources
            )
            self.conn.commit()

    # ---------- User operations ----------
    def register_user(self, username, password, full_name, role, campus_id=None):
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, full_name, role, campus_id) VALUES (?, ?, ?, ?, ?)",
                (username, password, full_name, role, campus_id)
            )
            self.conn.commit()
            return True, "Registration successful."
        except sqlite3.IntegrityError:
            return False, "Username already exists."

    def authenticate_user(self, username, password):
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_id(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ---------- Campus operations ----------
    def get_all_campuses(self):
        self.cursor.execute("SELECT * FROM campuses ORDER BY name")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_campus_by_id(self, campus_id):
        self.cursor.execute("SELECT * FROM campuses WHERE campus_id = ?", (campus_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ---------- Resource operations ----------
    def get_resources_by_campus(self, campus_id):
        self.cursor.execute(
            "SELECT * FROM resources WHERE campus_id = ? ORDER BY name",
            (campus_id,)
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def add_resource(self, campus_id, name, resource_type, capacity, description):
        try:
            self.cursor.execute(
                "INSERT INTO resources (campus_id, name, resource_type, capacity, description) VALUES (?, ?, ?, ?, ?)",
                (campus_id, name, resource_type, capacity, description)
            )
            self.conn.commit()
            return True, "Resource added successfully."
        except sqlite3.IntegrityError:
            return False, "A resource with this name already exists at this campus."

    def update_resource(self, resource_id, name, resource_type, capacity, description):
        try:
            self.cursor.execute(
                "UPDATE resources SET name=?, resource_type=?, capacity=?, description=? WHERE resource_id=?",
                (name, resource_type, capacity, description, resource_id)
            )
            self.conn.commit()
            return True, "Resource updated successfully."
        except sqlite3.IntegrityError:
            return False, "Duplicate resource name at this campus."

    def delete_resource(self, resource_id):
        # Check for active bookings
        self.cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE resource_id=? AND status='active'",
            (resource_id,)
        )
        if self.cursor.fetchone()[0] > 0:
            return False, "Cannot delete resource with active bookings."
        self.cursor.execute("DELETE FROM resources WHERE resource_id=?", (resource_id,))
        self.conn.commit()
        return True, "Resource deleted successfully."

    def get_resource_by_id(self, resource_id):
        self.cursor.execute("SELECT * FROM resources WHERE resource_id=?", (resource_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ---------- Booking operations ----------
    def has_overlapping_booking(self, resource_id, booking_date, start_time, end_time, exclude_booking_id=None):
        """Check if a proposed booking overlaps with any existing active booking."""
        query = """
            SELECT * FROM bookings
            WHERE resource_id = ? AND booking_date = ? AND status = 'active'
              AND NOT (end_time <= ? OR start_time >= ?)
        """
        params = [resource_id, booking_date, start_time, end_time]
        if exclude_booking_id:
            query += " AND booking_id != ?"
            params.append(exclude_booking_id)
        self.cursor.execute(query, params)
        return self.cursor.fetchone() is not None

    def create_booking(self, resource_id, user_id, campus_id, booking_date, start_time, duration_hours):
        # Calculate end time
        start_dt = datetime.strptime(f"{booking_date} {start_time}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(hours=duration_hours)
        end_time = end_dt.strftime("%H:%M")

        if self.has_overlapping_booking(resource_id, booking_date, start_time, end_time):
            return False, "This resource is already booked for the selected time slot."

        self.cursor.execute(
            """INSERT INTO bookings
               (resource_id, user_id, campus_id, booking_date, start_time, duration_hours, end_time, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'active')""",
            (resource_id, user_id, campus_id, booking_date, start_time, duration_hours, end_time)
        )
        self.conn.commit()
        return True, "Booking created successfully."

    def get_bookings_by_user(self, user_id, status=None):
        if status:
            self.cursor.execute(
                """SELECT b.*, r.name as resource_name, c.name as campus_name
                   FROM bookings b
                   JOIN resources r ON b.resource_id = r.resource_id
                   JOIN campuses c ON b.campus_id = c.campus_id
                   WHERE b.user_id = ? AND b.status = ?
                   ORDER BY b.booking_date DESC, b.start_time DESC""",
                (user_id, status)
            )
        else:
            self.cursor.execute(
                """SELECT b.*, r.name as resource_name, c.name as campus_name
                   FROM bookings b
                   JOIN resources r ON b.resource_id = r.resource_id
                   JOIN campuses c ON b.campus_id = c.campus_id
                   WHERE b.user_id = ?
                   ORDER BY b.booking_date DESC, b.start_time DESC""",
                (user_id,)
            )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_bookings_by_campus(self, campus_id, status=None):
        if status:
            self.cursor.execute(
                """SELECT b.*, r.name as resource_name, u.full_name as lecturer_name
                   FROM bookings b
                   JOIN resources r ON b.resource_id = r.resource_id
                   JOIN users u ON b.user_id = u.user_id
                   WHERE b.campus_id = ? AND b.status = ?
                   ORDER BY b.booking_date DESC, b.start_time DESC""",
                (campus_id, status)
            )
        else:
            self.cursor.execute(
                """SELECT b.*, r.name as resource_name, u.full_name as lecturer_name
                   FROM bookings b
                   JOIN resources r ON b.resource_id = r.resource_id
                   JOIN users u ON b.user_id = u.user_id
                   WHERE b.campus_id = ?
                   ORDER BY b.booking_date DESC, b.start_time DESC""",
                (campus_id,)
            )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_bookings(self):
        self.cursor.execute(
            """SELECT b.*, r.name as resource_name, c.name as campus_name, u.full_name as lecturer_name
               FROM bookings b
               JOIN resources r ON b.resource_id = r.resource_id
               JOIN campuses c ON b.campus_id = c.campus_id
               JOIN users u ON b.user_id = u.user_id
               ORDER BY b.booking_date DESC, b.start_time DESC"""
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def cancel_booking(self, booking_id, user_id=None):
        """Cancel a booking. If user_id is given, only the owner can cancel."""
        if user_id:
            self.cursor.execute(
                "SELECT * FROM bookings WHERE booking_id=? AND user_id=? AND status='active'",
                (booking_id, user_id)
            )
        else:
            self.cursor.execute(
                "SELECT * FROM bookings WHERE booking_id=? AND status='active'",
                (booking_id,)
            )
        if not self.cursor.fetchone():
            return False, "Booking not found or already cancelled."

        self.cursor.execute(
            "UPDATE bookings SET status='cancelled' WHERE booking_id=?",
            (booking_id,)
        )
        self.conn.commit()
        return True, "Booking cancelled successfully."

    # ---------- Reporting ----------
    def get_campus_report(self, campus_id):
        # Total bookings
        self.cursor.execute(
            "SELECT COUNT(*) as total FROM bookings WHERE campus_id=? AND status != 'cancelled'",
            (campus_id,)
        )
        total = self.cursor.fetchone()["total"]

        # Most frequently used resources
        self.cursor.execute(
            """SELECT r.name, COUNT(*) as count
               FROM bookings b
               JOIN resources r ON b.resource_id = r.resource_id
               WHERE b.campus_id=? AND b.status != 'cancelled'
               GROUP BY r.resource_id
               ORDER BY count DESC
               LIMIT 5""",
            (campus_id,)
        )
        top_resources = [dict(row) for row in self.cursor.fetchall()]

        # Average duration
        self.cursor.execute(
            "SELECT AVG(duration_hours) as avg_duration FROM bookings WHERE campus_id=? AND status != 'cancelled'",
            (campus_id,)
        )
        avg = self.cursor.fetchone()["avg_duration"]
        avg_duration = round(avg, 2) if avg else 0

        return {
            "total_bookings": total,
            "top_resources": top_resources,
            "average_duration": avg_duration
        }

    def get_cross_campus_report(self):
        self.cursor.execute(
            """SELECT c.name as campus_name,
                      COUNT(b.booking_id) as total_bookings,
                      AVG(b.duration_hours) as avg_duration,
                      c.max_duration_hours
               FROM campuses c
               LEFT JOIN bookings b ON c.campus_id = b.campus_id AND b.status != 'cancelled'
               GROUP BY c.campus_id
               ORDER BY total_bookings DESC"""
        )
        return [dict(row) for row in self.cursor.fetchall()]
