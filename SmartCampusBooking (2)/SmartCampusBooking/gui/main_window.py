"""
Main application window – role-based dashboard with campus selection,
resource management, booking, and reporting.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from models.booking_rules import get_rules_for_campus


class MainWindow(tk.Toplevel):
    def __init__(self, parent, db, user):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.current_campus = None
        self.current_campus_id = None

        self.title(f"Smart Campus Booking – {user.full_name} ({user.role.title()})")
        self.geometry("1000x650")
        self.minsize(900, 550)
        self.configure(bg="#e8eef5")

        # Centre window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 500
        y = (self.winfo_screenheight() // 2) - 325
        self.geometry(f"+{x}+{y}")

        self._build_header()
        self._build_body()
        self.protocol("WM_DELETE_WINDOW", self._logout)

        # Force campus selection first (except operator who can see all)
        if user.role != "operator":
            self._select_campus()
        else:
            self._show_operator_home()

    # ------------------------------------------------------------------ Header
    def _build_header(self):
        header = tk.Frame(self, bg="#1a365d", height=55)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Smart Campus Resource Booking System",
            font=("Segoe UI", 13, "bold"), fg="white", bg="#1a365d"
        ).pack(side="left", padx=15)

        self.campus_label = tk.Label(
            header, text="No campus selected",
            font=("Segoe UI", 10), fg="#a0c4e8", bg="#1a365d"
        )
        self.campus_label.pack(side="left", padx=20)

        self.policy_label = tk.Label(
            header, text="", font=("Segoe UI", 9), fg="#fbd38d", bg="#1a365d"
        )
        self.policy_label.pack(side="left", padx=10)

        tk.Button(
            header, text="Logout", command=self._logout,
            bg="#c53030", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=12, cursor="hand2"
        ).pack(side="right", padx=15, pady=10)

        tk.Label(
            header, text=f"{self.user.full_name}  |  {self.user.role.title()}",
            font=("Segoe UI", 9), fg="#cbd5e0", bg="#1a365d"
        ).pack(side="right", padx=10)

    # ------------------------------------------------------------------ Body
    def _build_body(self):
        self.body = tk.Frame(self, bg="#e8eef5")
        self.body.pack(fill="both", expand=True, padx=10, pady=10)

    def _clear_body(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------ Campus Selection
    def _select_campus(self):
        self._clear_body()
        frame = tk.Frame(self.body, bg="#e8eef5")
        frame.pack(expand=True)

        tk.Label(
            frame, text="Select a Campus to Continue",
            font=("Segoe UI", 16, "bold"), bg="#e8eef5", fg="#1a365d"
        ).pack(pady=(40, 20))

        campuses = self.db.get_all_campuses()

        # If admin, pre-select their assigned campus
        if self.user.role == "admin" and self.user.campus_id:
            for c in campuses:
                if c["campus_id"] == self.user.campus_id:
                    self._set_campus(c)
                    return

        for campus in campuses:
            btn = tk.Button(
                frame,
                text=f"{campus['name']}\n{campus['location']}",
                font=("Segoe UI", 11),
                width=35, height=3,
                bg="#2b6cb0", fg="white",
                activebackground="#2c5282",
                relief="flat", cursor="hand2",
                command=lambda c=campus: self._set_campus(c)
            )
            btn.pack(pady=8)

    def _set_campus(self, campus):
        self.current_campus = campus
        self.current_campus_id = campus["campus_id"]
        self.campus_label.config(text=f"📍 {campus['name']}")

        rules = get_rules_for_campus(campus["name"])
        self.policy_label.config(
            text=f"Policy: Max {rules.max_duration_hours}h  |  "
                 f"{rules.start_hour:02d}:00–{rules.end_hour:02d}:00"
        )
        self._show_role_home()

    # ------------------------------------------------------------------ Role Homes
    def _show_role_home(self):
        if self.user.role == "lecturer":
            self._show_lecturer_home()
        elif self.user.role == "admin":
            self._show_admin_home()
        else:
            self._show_operator_home()

    # ======================== LECTURER ========================
    def _show_lecturer_home(self):
        self._clear_body()

        # Navigation buttons
        nav = tk.Frame(self.body, bg="#e8eef5")
        nav.pack(fill="x", pady=(0, 10))

        buttons = [
            ("Available Resources", self._lecturer_resources),
            ("Make a Booking", self._lecturer_book),
            ("My Active Bookings", lambda: self._lecturer_bookings("active")),
            ("Booking History", lambda: self._lecturer_bookings(None)),
            ("Change Campus", self._select_campus),
        ]
        for text, cmd in buttons:
            tk.Button(
                nav, text=text, command=cmd,
                bg="#2b6cb0", fg="white", font=("Segoe UI", 9),
                relief="flat", padx=10, pady=5, cursor="hand2"
            ).pack(side="left", padx=4)

        # Default view
        self._lecturer_resources()

    def _lecturer_resources(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text=f"Resources at {self.current_campus['name']}",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        resources = self.db.get_resources_by_campus(self.current_campus_id)
        if not resources:
            tk.Label(content, text="No resources registered for this campus.",
                     bg="white", font=("Segoe UI", 10)).pack(pady=30)
            return

        cols = ("ID", "Name", "Type", "Capacity", "Description")
        tree = ttk.Treeview(content, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120 if col != "Description" else 250)
        tree.column("ID", width=50)

        for r in resources:
            tree.insert("", "end", values=(
                r["resource_id"], r["name"], r["resource_type"],
                r["capacity"], r["description"] or ""
            ))
        tree.pack(fill="both", expand=True, padx=15, pady=5)

        scrollbar = ttk.Scrollbar(content, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

    def _lecturer_book(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text="Create a New Booking",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        form = tk.Frame(content, bg="white")
        form.pack(padx=20, pady=5, anchor="w")

        # Resource
        tk.Label(form, text="Resource:", bg="white", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=6)
        resources = self.db.get_resources_by_campus(self.current_campus_id)
        res_map = {f"{r['name']} ({r['resource_type']})": r["resource_id"] for r in resources}
        res_combo = ttk.Combobox(form, values=list(res_map.keys()), state="readonly", width=40)
        if res_map:
            res_combo.current(0)
        res_combo.grid(row=0, column=1, pady=6, padx=10)

        # Date
        tk.Label(form, text="Date (YYYY-MM-DD):", bg="white", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=6)
        date_entry = ttk.Entry(form, width=42)
        date_entry.insert(0, date.today().isoformat())
        date_entry.grid(row=1, column=1, pady=6, padx=10)

        # Start time
        tk.Label(form, text="Start Time (HH:MM):", bg="white", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=6)
        time_entry = ttk.Entry(form, width=42)
        time_entry.insert(0, "09:00")
        time_entry.grid(row=2, column=1, pady=6, padx=10)

        # Duration
        rules = get_rules_for_campus(self.current_campus["name"])
        tk.Label(form, text=f"Duration (hours, max {rules.max_duration_hours}):",
                 bg="white", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", pady=6)
        dur_entry = ttk.Entry(form, width=42)
        dur_entry.insert(0, "1")
        dur_entry.grid(row=3, column=1, pady=6, padx=10)

        # Policy info
        policy_frame = tk.LabelFrame(content, text="Current Campus Booking Policy", bg="white",
                                     font=("Segoe UI", 9, "bold"), fg="#2b6cb0")
        policy_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(policy_frame, text=rules.get_policy_summary(), bg="white",
                 font=("Segoe UI", 9), justify="left").pack(anchor="w", padx=10, pady=8)

        def submit():
            res_label = res_combo.get()
            if not res_label:
                messagebox.showwarning("Input", "Please select a resource.")
                return
            resource_id = res_map[res_label]
            booking_date = date_entry.get().strip()
            start_time = time_entry.get().strip()
            try:
                duration = float(dur_entry.get().strip())
            except ValueError:
                messagebox.showwarning("Input", "Duration must be a number.")
                return

            # Validate date format
            try:
                datetime.strptime(booking_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Input", "Date must be YYYY-MM-DD.")
                return

            # Apply campus rules
            valid, msg = rules.validate(duration, start_time)
            if not valid:
                messagebox.showerror("Policy Violation", msg)
                return

            success, msg = self.db.create_booking(
                resource_id, self.user.user_id, self.current_campus_id,
                booking_date, start_time, duration
            )
            if success:
                messagebox.showinfo("Success", msg)
                self._lecturer_bookings("active")
            else:
                messagebox.showerror("Booking Failed", msg)

        tk.Button(
            content, text="Submit Booking", command=submit,
            bg="#38a169", fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=20, pady=8, cursor="hand2"
        ).pack(pady=10)

    def _lecturer_bookings(self, status_filter):
        self._clear_content_area()
        content = self._get_content_frame()

        title = "My Active Bookings" if status_filter == "active" else "My Booking History"
        tk.Label(content, text=title, font=("Segoe UI", 13, "bold"),
                 bg="white", fg="#1a365d").pack(anchor="w", padx=15, pady=10)

        bookings = self.db.get_bookings_by_user(self.user.user_id, status_filter)

        cols = ("ID", "Resource", "Campus", "Date", "Start", "Duration", "End", "Status")
        tree = ttk.Treeview(content, columns=cols, show="headings", height=12)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=90)
        tree.column("Resource", width=150)
        tree.column("Campus", width=140)

        for b in bookings:
            tree.insert("", "end", values=(
                b["booking_id"], b["resource_name"], b["campus_name"],
                b["booking_date"], b["start_time"], f"{b['duration_hours']}h",
                b["end_time"], b["status"]
            ))
        tree.pack(fill="both", expand=True, padx=15, pady=5)

        if status_filter == "active":
            def cancel_selected():
                sel = tree.selection()
                if not sel:
                    messagebox.showwarning("Select", "Please select a booking to cancel.")
                    return
                item = tree.item(sel[0])
                booking_id = item["values"][0]
                if messagebox.askyesno("Confirm", "Cancel this booking?"):
                    success, msg = self.db.cancel_booking(booking_id, self.user.user_id)
                    if success:
                        messagebox.showinfo("Done", msg)
                        self._lecturer_bookings("active")
                    else:
                        messagebox.showerror("Error", msg)

            tk.Button(
                content, text="Cancel Selected Booking", command=cancel_selected,
                bg="#c53030", fg="white", font=("Segoe UI", 9, "bold"),
                relief="flat", padx=12, pady=5, cursor="hand2"
            ).pack(pady=8)

    # ======================== ADMIN ========================
    def _show_admin_home(self):
        self._clear_body()

        nav = tk.Frame(self.body, bg="#e8eef5")
        nav.pack(fill="x", pady=(0, 10))

        buttons = [
            ("Manage Resources", self._admin_resources),
            ("Campus Bookings", self._admin_bookings),
            ("Campus Report", self._admin_report),
            ("Change Campus", self._select_campus),
        ]
        for text, cmd in buttons:
            tk.Button(
                nav, text=text, command=cmd,
                bg="#2b6cb0", fg="white", font=("Segoe UI", 9),
                relief="flat", padx=10, pady=5, cursor="hand2"
            ).pack(side="left", padx=4)

        self._admin_resources()

    def _admin_resources(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text=f"Resource Management – {self.current_campus['name']}",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        # Treeview
        cols = ("ID", "Name", "Type", "Capacity", "Description")
        tree = ttk.Treeview(content, columns=cols, show="headings", height=10)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=110 if col != "Description" else 220)
        tree.column("ID", width=50)

        def refresh():
            tree.delete(*tree.get_children())
            for r in self.db.get_resources_by_campus(self.current_campus_id):
                tree.insert("", "end", values=(
                    r["resource_id"], r["name"], r["resource_type"],
                    r["capacity"], r["description"] or ""
                ))

        refresh()
        tree.pack(fill="both", expand=True, padx=15, pady=5)

        # Action buttons + form
        action_frame = tk.Frame(content, bg="white")
        action_frame.pack(fill="x", padx=15, pady=8)

        form = tk.Frame(content, bg="white")
        form.pack(padx=15, pady=5, anchor="w")

        tk.Label(form, text="Name:", bg="white").grid(row=0, column=0, sticky="w")
        name_e = ttk.Entry(form, width=25)
        name_e.grid(row=0, column=1, padx=5)

        tk.Label(form, text="Type:", bg="white").grid(row=0, column=2, sticky="w")
        type_e = ttk.Combobox(form, values=["Computer Laboratory", "Seminar Room", "Projector",
                                            "Presentation Equipment", "Auditorium", "Other"],
                              width=20)
        type_e.grid(row=0, column=3, padx=5)

        tk.Label(form, text="Capacity:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        cap_e = ttk.Entry(form, width=25)
        cap_e.insert(0, "1")
        cap_e.grid(row=1, column=1, padx=5)

        tk.Label(form, text="Description:", bg="white").grid(row=1, column=2, sticky="w")
        desc_e = ttk.Entry(form, width=25)
        desc_e.grid(row=1, column=3, padx=5)

        def add_res():
            name = name_e.get().strip()
            rtype = type_e.get().strip()
            try:
                cap = int(cap_e.get().strip())
            except ValueError:
                messagebox.showwarning("Input", "Capacity must be an integer.")
                return
            if not name or not rtype:
                messagebox.showwarning("Input", "Name and Type are required.")
                return
            success, msg = self.db.add_resource(
                self.current_campus_id, name, rtype, cap, desc_e.get().strip()
            )
            if success:
                messagebox.showinfo("Success", msg)
                refresh()
                name_e.delete(0, tk.END)
                desc_e.delete(0, tk.END)
            else:
                messagebox.showerror("Error", msg)

        def delete_res():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a resource to delete.")
                return
            rid = tree.item(sel[0])["values"][0]
            if messagebox.askyesno("Confirm", "Delete this resource?"):
                success, msg = self.db.delete_resource(rid)
                if success:
                    messagebox.showinfo("Done", msg)
                    refresh()
                else:
                    messagebox.showerror("Error", msg)

        def update_res():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Select", "Select a resource to update.")
                return
            rid = tree.item(sel[0])["values"][0]
            name = name_e.get().strip()
            rtype = type_e.get().strip()
            try:
                cap = int(cap_e.get().strip())
            except ValueError:
                messagebox.showwarning("Input", "Capacity must be an integer.")
                return
            if not name or not rtype:
                messagebox.showwarning("Input", "Name and Type are required.")
                return
            success, msg = self.db.update_resource(rid, name, rtype, cap, desc_e.get().strip())
            if success:
                messagebox.showinfo("Success", msg)
                refresh()
            else:
                messagebox.showerror("Error", msg)

        def on_select(event):
            sel = tree.selection()
            if sel:
                vals = tree.item(sel[0])["values"]
                name_e.delete(0, tk.END)
                name_e.insert(0, vals[1])
                type_e.set(vals[2])
                cap_e.delete(0, tk.END)
                cap_e.insert(0, vals[3])
                desc_e.delete(0, tk.END)
                desc_e.insert(0, vals[4] if vals[4] else "")

        tree.bind("<<TreeviewSelect>>", on_select)

        tk.Button(action_frame, text="Add Resource", command=add_res,
                  bg="#38a169", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=4)
        tk.Button(action_frame, text="Update Selected", command=update_res,
                  bg="#dd6b20", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=4)
        tk.Button(action_frame, text="Delete Selected", command=delete_res,
                  bg="#c53030", fg="white", relief="flat", padx=10, cursor="hand2").pack(side="left", padx=4)

    def _admin_bookings(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text=f"All Bookings – {self.current_campus['name']}",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        bookings = self.db.get_bookings_by_campus(self.current_campus_id)

        cols = ("ID", "Resource", "Lecturer", "Date", "Start", "Duration", "End", "Status")
        tree = ttk.Treeview(content, columns=cols, show="headings", height=14)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=90)
        tree.column("Resource", width=140)
        tree.column("Lecturer", width=130)

        for b in bookings:
            tree.insert("", "end", values=(
                b["booking_id"], b["resource_name"], b["lecturer_name"],
                b["booking_date"], b["start_time"], f"{b['duration_hours']}h",
                b["end_time"], b["status"]
            ))
        tree.pack(fill="both", expand=True, padx=15, pady=5)

    def _admin_report(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text=f"Campus Report – {self.current_campus['name']}",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        report = self.db.get_campus_report(self.current_campus_id)

        info = tk.Frame(content, bg="white")
        info.pack(padx=20, pady=10, anchor="w")

        tk.Label(info, text=f"Total Bookings:  {report['total_bookings']}",
                 font=("Segoe UI", 12), bg="white").pack(anchor="w", pady=4)
        tk.Label(info, text=f"Average Duration:  {report['average_duration']} hours",
                 font=("Segoe UI", 12), bg="white").pack(anchor="w", pady=4)

        tk.Label(content, text="Most Frequently Used Resources:",
                 font=("Segoe UI", 11, "bold"), bg="white").pack(anchor="w", padx=20, pady=(15, 5))

        if report["top_resources"]:
            for i, r in enumerate(report["top_resources"], 1):
                tk.Label(
                    content, text=f"  {i}. {r['name']}  –  {r['count']} booking(s)",
                    font=("Segoe UI", 10), bg="white"
                ).pack(anchor="w", padx=30)
        else:
            tk.Label(content, text="  No bookings yet.", bg="white").pack(anchor="w", padx=30)

    # ======================== OPERATOR ========================
    def _show_operator_home(self):
        self._clear_body()

        nav = tk.Frame(self.body, bg="#e8eef5")
        nav.pack(fill="x", pady=(0, 10))

        buttons = [
            ("All Campuses Overview", self._operator_overview),
            ("Cross-Campus Report", self._operator_report),
            ("All Bookings", self._operator_all_bookings),
            ("Select Campus View", self._select_campus),
        ]
        for text, cmd in buttons:
            tk.Button(
                nav, text=text, command=cmd,
                bg="#2b6cb0", fg="white", font=("Segoe UI", 9),
                relief="flat", padx=10, pady=5, cursor="hand2"
            ).pack(side="left", padx=4)

        self._operator_overview()

    def _operator_overview(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text="System-Wide Campus Overview",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        campuses = self.db.get_all_campuses()
        for c in campuses:
            frame = tk.LabelFrame(content, text=c["name"], bg="white",
                                  font=("Segoe UI", 10, "bold"), fg="#2b6cb0")
            frame.pack(fill="x", padx=15, pady=6)

            resources = self.db.get_resources_by_campus(c["campus_id"])
            report = self.db.get_campus_report(c["campus_id"])
            rules = get_rules_for_campus(c["name"])

            info = (
                f"Location: {c['location']}\n"
                f"Resources: {len(resources)}  |  Total Bookings: {report['total_bookings']}  |  "
                f"Avg Duration: {report['average_duration']}h\n"
                f"Policy: Max {rules.max_duration_hours}h, Hours {rules.start_hour:02d}:00–{rules.end_hour:02d}:00"
            )
            tk.Label(frame, text=info, bg="white", font=("Segoe UI", 9), justify="left").pack(anchor="w", padx=10, pady=6)

    def _operator_report(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text="Cross-Campus Comparison Report",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        data = self.db.get_cross_campus_report()

        cols = ("Campus", "Total Bookings", "Avg Duration (h)", "Max Allowed Duration")
        tree = ttk.Treeview(content, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=160)

        for row in data:
            avg = round(row["avg_duration"], 2) if row["avg_duration"] else 0
            tree.insert("", "end", values=(
                row["campus_name"], row["total_bookings"], avg, row["max_duration_hours"]
            ))
        tree.pack(fill="x", padx=15, pady=10)

        # Insights
        tk.Label(content, text="Insights / Trends:", font=("Segoe UI", 11, "bold"),
                 bg="white").pack(anchor="w", padx=15, pady=(15, 5))

        if data:
            most = max(data, key=lambda x: x["total_bookings"] or 0)
            least = min(data, key=lambda x: x["total_bookings"] or 0)
            tk.Label(
                content,
                text=f"• Highest usage: {most['campus_name']} ({most['total_bookings']} bookings)\n"
                     f"• Lowest usage: {least['campus_name']} ({least['total_bookings']} bookings)\n"
                     f"• Differences may result from campus-specific max-duration and allowed-hours policies.",
                bg="white", font=("Segoe UI", 10), justify="left"
            ).pack(anchor="w", padx=25)

    def _operator_all_bookings(self):
        self._clear_content_area()
        content = self._get_content_frame()

        tk.Label(
            content, text="All Bookings Across Campuses",
            font=("Segoe UI", 13, "bold"), bg="white", fg="#1a365d"
        ).pack(anchor="w", padx=15, pady=10)

        bookings = self.db.get_all_bookings()

        cols = ("ID", "Resource", "Campus", "Lecturer", "Date", "Start", "Duration", "Status")
        tree = ttk.Treeview(content, columns=cols, show="headings", height=14)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=90)
        tree.column("Resource", width=130)
        tree.column("Campus", width=140)
        tree.column("Lecturer", width=120)

        for b in bookings:
            tree.insert("", "end", values=(
                b["booking_id"], b["resource_name"], b["campus_name"],
                b["lecturer_name"], b["booking_date"], b["start_time"],
                f"{b['duration_hours']}h", b["status"]
            ))
        tree.pack(fill="both", expand=True, padx=15, pady=5)

    # ------------------------------------------------------------------ Helpers
    def _clear_content_area(self):
        """Clear everything below the navigation bar."""
        children = self.body.winfo_children()
        # Keep the first child (nav) if it exists, destroy the rest
        for i, w in enumerate(children):
            if i > 0:
                w.destroy()

    def _get_content_frame(self):
        frame = tk.Frame(self.body, bg="white", relief="groove", bd=1)
        frame.pack(fill="both", expand=True)
        return frame

    def _logout(self):
        self.destroy()
        # Re-open login by calling the parent's restart method if available
        if hasattr(self.master, "show_login"):
            self.master.show_login()
        else:
            self.master.destroy()
