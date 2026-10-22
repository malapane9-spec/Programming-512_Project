"""
User models using Object-Oriented Programming principles:
- Base User class with encapsulation
- Inheritance for Lecturer, CampusAdministrator, SystemOperator
"""

from abc import ABC, abstractmethod


class User(ABC):
    """Abstract base class for all system users."""

    def __init__(self, user_id, username, full_name, role, campus_id=None):
        self._user_id = user_id
        self._username = username
        self._full_name = full_name
        self._role = role
        self._campus_id = campus_id

    # Encapsulated getters
    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @property
    def full_name(self):
        return self._full_name

    @property
    def role(self):
        return self._role

    @property
    def campus_id(self):
        return self._campus_id

    def __str__(self):
        return f"{self._full_name} ({self._role})"

    @abstractmethod
    def get_permissions(self):
        """Return a list of permissions for this role."""
        pass


class Lecturer(User):
    """Lecturer can register, login, book resources, view/cancel own bookings."""

    def __init__(self, user_id, username, full_name, campus_id=None):
        super().__init__(user_id, username, full_name, "lecturer", campus_id)

    def get_permissions(self):
        return [
            "book_resource",
            "view_own_bookings",
            "cancel_own_booking",
            "view_available_resources"
        ]


class CampusAdministrator(User):
    """Campus Admin manages resources and views bookings for their campus."""

    def __init__(self, user_id, username, full_name, campus_id):
        super().__init__(user_id, username, full_name, "admin", campus_id)

    def get_permissions(self):
        return [
            "manage_resources",
            "view_campus_bookings",
            "view_campus_reports",
            "monitor_availability"
        ]


class SystemOperator(User):
    """System Operator has full system-wide access and can generate cross-campus reports."""

    def __init__(self, user_id, username, full_name):
        super().__init__(user_id, username, full_name, "operator", None)

    def get_permissions(self):
        return [
            "view_all_bookings",
            "view_all_resources",
            "generate_cross_campus_reports",
            "view_all_campuses"
        ]


def create_user_from_dict(user_data):
    """Factory function to create the correct User subclass from a database row."""
    role = user_data["role"]
    if role == "lecturer":
        return Lecturer(
            user_data["user_id"],
            user_data["username"],
            user_data["full_name"],
            user_data.get("campus_id")
        )
    elif role == "admin":
        return CampusAdministrator(
            user_data["user_id"],
            user_data["username"],
            user_data["full_name"],
            user_data["campus_id"]
        )
    elif role == "operator":
        return SystemOperator(
            user_data["user_id"],
            user_data["username"],
            user_data["full_name"]
        )
    else:
        raise ValueError(f"Unknown role: {role}")
