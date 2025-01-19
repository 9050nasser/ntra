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

def get_shift_hours(employee, date=None):
    # Fetch shift duration for the employee
    shift_type =None

    data = frappe.db.sql(f"SELECT shift_type FROM `tabShift Assignment` WHERE employee = '{employee}' AND docstatus = 1 order by start_date DESC" ,as_dict=True)
    if data:
        shift_type = frappe.get_cached_doc('Shift Type', data[0]['shift_type'])
    if not data:
        employee = frappe.get_cached_doc("Employee", employee)
        if employee.default_shift:
            shift_type = frappe.get_cached_doc('Shift Type', employee.default_shift)
    def get_working_hours(start_time, end_time):
        # Parse the time strings into datetime objects
        start = datetime.strptime(str(start_time), "%H:%M:%S")
        end = datetime.strptime(str(end_time), "%H:%M:%S")
        
        # Calculate the difference in hours
        time_difference = end - start
        working_hours = time_difference.total_seconds() / 3600  # Convert seconds to hours
    
        return working_hours
    if not shift_type:
        return 0
    return get_working_hours(shift_type.start_time, shift_type.end_time) or 0

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
            hours = get_shift_hours(self.employee, date=self.from_date)

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
                        "working_hours": hours,
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
        elif self.mission_type == "Hours":
            start_date = datetime.strptime(self.from_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.to_date, "%Y-%m-%d")
            start_time = self.from_time
            end_time = self.to_time
            if isinstance(end_time, timedelta) and isinstance(start_time, timedelta):
                time_diff = end_time - start_time
            else:
                time_diff = datetime.strptime(end_time, "%H:%M:%S") - datetime.strptime(start_time, "%H:%M:%S")
            diff = time_diff.total_seconds() / 3600
            current_date = start_date
            while current_date <= end_date:
                # Check if an attendance record already exists
                existing_attendance = frappe.db.exists(
                    "Attendance", 
                    {"employee": self.employee, "attendance_date": current_date.strftime("%Y-%m-%d")}
                )
                if existing_attendance:
                    doc = frappe.get_doc("Attendance", existing_attendance)
                    doc.db_set("working_hours", doc.working_hours + diff)
                    doc.db_set("status", "Present")
                    doc.db_set("custom_reason", self.doctype)
                    doc.db_set("custom_permission", self.name)
                    frappe.db.commit()

                current_date += timedelta(days=1)




def float_to_hhmmss(hours):
    # Calculate total seconds from the float hours
    total_seconds = int(hours * 3600)

    # Get hours, minutes, and seconds using divmod
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format as HH:MM:SS
    return f"{hours:02}:{minutes:02}:{seconds:02}"


