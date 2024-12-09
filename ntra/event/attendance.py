import frappe
from datetime import datetime, timedelta

def validate_attendance(doc, method):
    # Fetch approved permissions for the employee on the attendance date
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
                    updated_working_hours = doc.working_hours + additional_hours
                    doc.db_set('custom_calculated_working_hours', float_to_hhmmss(updated_working_hours or 0))
                    doc.db_set('working_hours', updated_working_hours)
                    doc.db_set('status', 'Present')
                    doc.db_set('custom_reason', permission.doctype)
                    doc.db_set('custom_permission', permission.name)

            except Exception as e:
                frappe.log_error(f"Error processing permission {permission.name}: {str(e)}", "Attendance Validation")

def float_to_hhmmss(hours):
    # Calculate total seconds from the float hours
    total_seconds = int(hours * 3600)

    # Get hours, minutes, and seconds using divmod
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format as HH:MM:SS
    return f"{hours:02}:{minutes:02}:{seconds:02}"
