import frappe
from datetime import datetime, timedelta

def validate_attendance(doc, method):
    # Fetch approved permissions for the employee on the attendance date
    try:
        permissions = frappe.db.get_all(
            "Permission",
            filters={
                "employee": doc.employee,
                "status": "Approved",
                "date": doc.attendance_date,
                "docstatus": 1
            },
            fields=["*"]
        )
        if not permissions:
            doc.db_set('custom_calculated_working_hours', float_to_hhmmss(doc.working_hours or 0))
            doc.db_set('custom_actual_working_hours', float_to_hhmmss(doc.working_hours or 0))
            return
        # Update actual working hours
        doc.db_set('custom_actual_working_hours', float_to_hhmmss(doc.working_hours or 0))

        for permission in permissions:
            permission_type = frappe.get_doc("Permission Type", permission.permission_type)
            if permission_type.allow_without_deduction:
                try:
                        # Calculate time difference based on time formats
                        if isinstance(permission.to_time, timedelta) and isinstance(permission.from_time, timedelta):
                            time_diff = permission.to_time - permission.from_time
                        else:
                            time_diff = datetime.strptime(permission.to_time, "%H:%M:%S") - datetime.strptime(permission.from_time, "%H:%M:%S")

                        # Update working hours and custom fields
                        additional_hours = time_diff.total_seconds() / 3600
                        updated_working_hours = ((doc.working_hours + additional_hours) or 0)
                        doc.db_set('custom_calculated_working_hours', float_to_hhmmss(updated_working_hours or 0))
                        doc.db_set('working_hours', updated_working_hours)
                        doc.db_set('status', 'Present')
                        doc.db_set('custom_reason', permission.doctype)
                        doc.db_set('custom_permission', permission.name)

                except Exception as e:
                    frappe.log_error(f"Error processing permission {permission.name}: {str(e)}", "Attendance Validation")
    except Exception as e:
        frappe.log_error(f"Error processing permission {permission.name}: {str(e)}", "Attendance Validation2")

from datetime import datetime, date
import calendar
from frappe.utils import add_to_date, today, date_diff

def month_day(start, end):
    diff = date_diff(end, start)
    return diff

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

def security_shift(doc, method):
    month_start, month_end = get_month_start_end(doc.attendance_date)
    month_days = month_day(month_start, month_end)
    shift_list = frappe.db.get_all(
        "Shift Assignment",
        filters={"employee": doc.employee, "status": "Active", "start_date": ["<=", today()]},
        fields=["shift_type"]
    )
    if len(shift_list):
        shift= shift_list[0]
    else:
        shift = None
    if shift:
        shift_type = frappe.get_doc("Shift Type", shift.shift_type)
        if shift_type.custom_security_shift:
            attendance = frappe.db.get_all(
                "Attendance",
                filters={
                    "attendance_date": add_to_date(doc.attendance_date, days=-1),
                    "employee": doc.employee,
                    "docstatus": ["=", 1]
                },
                fields=["custom_remaining_hours"]
            )
            
            holiday_list = shift_type.holiday_list
            count = frappe.db.sql(
                """SELECT COUNT(holiday_date) as count 
                   FROM `tabHoliday` 
                   WHERE parent = %s AND holiday_date BETWEEN %s AND %s""",
                (holiday_list, month_start, month_end),
                as_dict=True
            )
            working_days = month_days - count[0].count
            working_hours = working_days * shift_type.custom_daily_working_hour
            doc.db_set("custom_target_working_hours", working_hours)

            # Handle empty attendance
            previous_remaining_hours = working_hours
            if attendance:
                previous_remaining_hours = attendance[0].custom_remaining_hours or working_hours
            
            attendance_working_hours = calculate_hours_difference(doc.in_time, doc.out_time)
            remaining_hours = float(previous_remaining_hours - attendance_working_hours)
            doc.db_set("custom_remaining_hours", remaining_hours)




def calculate_hours_difference(in_time, out_time, time_format="%d-%m-%Y %H:%M:%S", round_to=2):
    # Return 0 if either in_time or out_time is None
    if not in_time or not out_time:
        return 0.0

    # If in_time or out_time is a string, parse it into a datetime object
    if isinstance(in_time, str):
        in_time = datetime.strptime(in_time, time_format)
    if isinstance(out_time, str):
        out_time = datetime.strptime(out_time, time_format)
    
    # Calculate the time difference
    time_difference = out_time - in_time
    
    # Convert the difference to hours and round it
    return round(time_difference.total_seconds() / 3600, round_to)



def float_to_hhmmss(hours):
    # Calculate total seconds from the float hours
    total_seconds = int(hours * 3600)

    # Get hours, minutes, and seconds using divmod
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format as HH:MM:SS
    return f"{hours:02}:{minutes:02}:{seconds:02}"
