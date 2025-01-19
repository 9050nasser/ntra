import frappe
from frappe import _
from datetime import datetime, timedelta, date

def get_month_start_end(input_date):
    # Convert input_date to a datetime object if it's a string
    if isinstance(input_date, str):
        try:
            input_date = datetime.strptime(input_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format for input_date: {input_date}. Expected 'YYYY-MM-DD'.")
    
    # Ensure the input_date is now a date object
    if not isinstance(input_date, date):
        raise TypeError("input_date must be a datetime.date object or a string in 'YYYY-MM-DD' format.")
    
    month_start = date(input_date.year, input_date.month, 1)
    month_end = date(input_date.year, input_date.month + 1, 1) - timedelta(days=1) if input_date.month < 12 else date(input_date.year, 12, 31)
    
    return month_start, month_end


def validate_maximum_leaves_time(doc, method):
    month_start, month_end = get_month_start_end(doc.from_date)
    shifts = frappe.db.get_all("Shift Type", filters={"custom_security_shift": ["=", 1]}, fields=["*"])
    for shift in shifts:
        leaves = frappe.db.get_all("Leave Application", filters={"employee": doc.employee, "leave_type": shift.custom_leave_type, "status": "Approved", "docstatus": ["=", 1], "from_date": ["Between", [month_start, month_end]], "to_date": ["Between", [month_start, month_end]]}, fields=["SUM(total_leave_days) as total_leaves"])

        if (shift.custom_monthly_leave_allocation > 0) and shift.custom_leave_type:
            if leaves[0].total_leaves:
                if (leaves[0].total_leaves >= shift.custom_monthly_leave_allocation) and (shift.custom_leave_type == doc.leave_type):
                    
                    frappe.throw(_(f"Remaining Leaves for This Month is {int(shift.custom_monthly_leave_allocation - leaves[0].total_leaves)} of {int(shift.custom_monthly_leave_allocation)}"))
    

def on_submit(doc, method):
    attendance_list = frappe.db.get_list("Attendance", [["docstatus", "=", 1],["employee", "=", doc.employee], ["attendance_date", "between", [doc.from_date, doc.to_date]]])
    for attendance in attendance_list:
        frappe.db.set_value("Attendance", attendance.name, dict(
            status = "On Leave",
            working_hours = 0,
            leave_type = doc.leave_type,
            leave_application = doc.name
        ))