import frappe
from datetime import datetime, timedelta
from frappe.utils import nowdate, getdate, today, flt, cint, date_diff
from frappe import _
from datetime import datetime, timedelta
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
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

@frappe.whitelist()
def calculate_employee_record(doc,method=None):
    filters = {
            "skip_auto_attendance": 0,
            "attendance": ("is", "not set"),
            "shift": doc.shift,
            "employee": doc.employee
        }
    logs = frappe.db.get_list(
        "Employee Checkin", fields="*", filters=filters, order_by="time"
    )
    # if logs:
    #     shift = frappe.get_doc("Shift Type", doc.shift)
    #     if shift.enable_break:
    #         calculate_break_time(logs, doc, shift)
    pass

def get_dates_different_in_minutes(date1: datetime, date2: datetime) -> float:
    return (date1 - date2).total_seconds() / 60
def get_date(date_time):
        if type(date_time) == datetime:
            date_time = date_time.strftime(DATE_FORMAT)
        return date_time
def _handle_multiple_same_checks(date1, date2):
        if get_date(date1) is None or get_date(date2) is None:
            return
        checkin_date = datetime.strptime(get_date(date1), DATE_FORMAT)
        checkout_date = datetime.strptime(get_date(date2), DATE_FORMAT)
        minutes = (get_dates_different_in_minutes(checkout_date, checkin_date))
        if minutes > 5:
            return True

def calculate_break_time(logs, doc, shift):
    total_hours = break_duration = break_times= allowed_break_duration = 0
    in_break = out_break = None
    out_time = doc.out_time
    while len(logs) >= 2:
        if _handle_multiple_same_checks( logs[0].time,logs[1].time):         
            total_hours += time_diff_in_hours(logs[0].time, logs[1].time)
            in_break = logs[1].time
            if len(logs) > 2:
                break_times +=1
                out_break = logs[2].time
                if out_break == out_time:
                    doc.out_time = None
                on_time = 0
                # if shift.break_type =="Fixed":
                in_break = datetime.strptime(get_date(in_break), '%Y-%m-%d %H:%M:%S')
                out_break = datetime.strptime(get_date(out_break), '%Y-%m-%d %H:%M:%S')
                    # shift_in_break = datetime.strptime(str(shift.in_break), '%H:%M:%S')
                    # shift_out_break = datetime.strptime(str(shift.out_break), '%H:%M:%S')
                    # allowed_break_duration = (shift_out_break - shift_in_break).total_seconds()
                    # shift.break_duration = allowed_break_duration
                    # if (in_break.time() >= shift_in_break.time()) and (out_break.time() <= shift_out_break.time()):
                        # on_time = 1
                emp_record = frappe.new_doc("Employee Record")
                emp_record.employee = doc.employee
                emp_record.date = doc.attendance_date
                emp_record.start_time = doc.in_break
                emp_record.end_time = doc.out_break
                emp_record.duration = doc.working_hours - total_hours

                emp_record.insert()
            in_break = out_break = None
            del logs[:2]
        else:
            del logs[1]

def time_diff_in_hours(start, end):
    return round(float((end - start).total_seconds()) / 3600, 2)

@frappe.whitelist()
def validate_employee_checkin(doc, method):
    # frappe.msgprint(f"{doc.shift}")
    last_log = frappe.db.sql(f"""SELECT * from `tabEmployee Checkin` where employee = '{doc.employee}' and shift ='{doc.shift}' order by creation DESC limit 1 """, as_dict=1)
    if last_log:
        if last_log[0]['name'] == doc.name:
                return
        minutes = _check_if_created_checkin_or_not(last_log[0]['time'], doc.time)
        if minutes <= 5:
            frappe.throw("لقد تم تسجيل البصمة بالفعل")
    pass

def _check_if_created_checkin_or_not(date1, date2):
        if get_date(date1) is None or get_date(date2) is None:
            return
        
        checkin_date = datetime.strptime(get_date(date1), DATE_FORMAT)
        checkout_date = datetime.strptime(get_date(date2), DATE_FORMAT)
        minutes = (get_dates_different_in_minutes(checkout_date, checkin_date))
        return minutes