"""
Campus-specific booking rules.
Rules are separated from core logic so new campuses / policies can be added easily.
"""

from datetime import datetime, time


class BookingRule:
    """Base class for campus booking policies."""

    def __init__(self, campus_name, max_duration_hours, start_hour, end_hour, description=""):
        self.campus_name = campus_name
        self.max_duration_hours = max_duration_hours
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.description = description

    def validate(self, duration_hours, start_time_str):
        """
        Validate a proposed booking against this campus's rules.
        Returns (is_valid: bool, message: str)
        """
        # Check max duration
        if duration_hours > self.max_duration_hours:
            return False, (
                f"Maximum booking duration at {self.campus_name} is "
                f"{self.max_duration_hours} hour(s). You requested {duration_hours}."
            )
        if duration_hours <= 0:
            return False, "Duration must be greater than 0."

        # Check allowed hours
        try:
            start_t = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            return False, "Invalid start time format. Use HH:MM."

        allowed_start = time(self.start_hour, 0)
        allowed_end = time(self.end_hour, 0)

        if not (allowed_start <= start_t < allowed_end):
            return False, (
                f"Bookings at {self.campus_name} are only allowed between "
                f"{self.start_hour:02d}:00 and {self.end_hour:02d}:00."
            )

        # Also ensure the booking ends within allowed hours
        end_minutes = int(duration_hours * 60)
        end_hour = start_t.hour + (start_t.minute + end_minutes) // 60
        end_minute = (start_t.minute + end_minutes) % 60
        end_t = time(end_hour % 24, end_minute)

        if end_t > allowed_end or end_hour >= 24:
            return False, (
                f"Booking would end after the allowed hours "
                f"({self.end_hour:02d}:00) at {self.campus_name}."
            )

        return True, "Booking complies with campus policy."

    def get_policy_summary(self):
        return (
            f"{self.campus_name} Policy:\n"
            f"• Max duration: {self.max_duration_hours} hour(s)\n"
            f"• Allowed hours: {self.start_hour:02d}:00 – {self.end_hour:02d}:00\n"
            f"• {self.description}"
        )


class JohannesburgRules(BookingRule):
    def __init__(self):
        super().__init__(
            "Johannesburg Campus",
            max_duration_hours=2.0,
            start_hour=8,
            end_hour=17,
            description="Strict daytime policy for high-demand campus."
        )


class CapeTownRules(BookingRule):
    def __init__(self):
        super().__init__(
            "Cape Town Campus",
            max_duration_hours=3.0,
            start_hour=7,
            end_hour=19,
            description="Extended hours to accommodate evening classes."
        )


class DurbanRules(BookingRule):
    def __init__(self):
        super().__init__(
            "Durban Campus",
            max_duration_hours=4.0,
            start_hour=8,
            end_hour=18,
            description="Flexible duration for longer practical sessions."
        )


# Registry – easy to extend with new campuses
RULE_REGISTRY = {
    "Johannesburg Campus": JohannesburgRules,
    "Cape Town Campus": CapeTownRules,
    "Durban Campus": DurbanRules,
}


def get_rules_for_campus(campus_name):
    """Return the correct BookingRule instance for a campus name."""
    rule_class = RULE_REGISTRY.get(campus_name)
    if rule_class:
        return rule_class()
    # Fallback generic rule if campus not in registry
    return BookingRule(campus_name, 2.0, 8, 17, "Default policy.")
