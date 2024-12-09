# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils import (
	add_days,
	cint,
	cstr,
	format_date,
	get_datetime,
	get_link_to_form,
	getdate,
	nowdate,
)



class MissionApplication(Document):
    def on_submit(self):
        self.make_attendance()

    def make_attendance(self):
        names = []
        if self.mission_type == "Days":
            # Parse the dates into datetime objects
            start_date = datetime.strptime(self.from_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.to_date, "%Y-%m-%d")

            # Iterate through each date in the range
            current_date = start_date
            while current_date <= end_date:
                # Check if an attendance record already exists
                existing_attendance = frappe.db.exists(
                    "Attendance", 
                    {"employee": self.employee, "attendance_date": current_date.strftime("%Y-%m-%d"), "status": "Approved"}
                )

                if not existing_attendance:
                    # Create a new attendance record
                    attendance = frappe.get_doc({
                        "doctype": "Attendance",
                        "employee": self.employee,
                        "attendance_date": current_date.strftime("%Y-%m-%d"),
                        "status": "Present",
                        "custom_reason": self.doctype,
                        "custom_permission": self.name
                    })
                    attendance.insert(ignore_permissions=True)
                    attendance.submit()
                    names.append(attendance.name)  # Append the name to the list

                # Move to the next date
                current_date += timedelta(days=1)

            # Generate links for created records
            if names:
                duplicate_links = ", ".join(
                    [get_link_to_form("Attendance", name) for name in names]
                )
                frappe.msgprint(f"Attendance created successfully: {duplicate_links}")

