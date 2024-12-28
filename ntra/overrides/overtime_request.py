import frappe
from hr_attendance.attendance.doctype.overtime_request.overtime_request import OvertimeRequest

class CustomOvertimeRequest(OvertimeRequest):
    def on_submit(self):
        # Define DocTypes
        AttendanceRule = frappe.qb.DocType("Attendance Rule")
        Employee = frappe.qb.DocType("Employee")

        # Query to fetch the checkbox value
        query = (
            frappe.qb.from_(AttendanceRule)
            .select(AttendanceRule.enable_overtime_based_on_target_hours)
            .where(
                AttendanceRule.name == frappe.qb.from_(Employee)
                .select(Employee.custom_attendance_rule)
                .where(Employee.name == self.employee)
            )
        )

        # Execute the query
        result = query.run(as_dict=True)

        if result and "enable_overtime_based_on_target_hours" in result[0]:
            enable_overtime_based_on_target_hours = result[0]["enable_overtime_based_on_target_hours"]
            if not enable_overtime_based_on_target_hours:
                # Call parent method if the condition is met
                super().on_submit()
        else:
            # Call parent method if no result or key is missing
            super().on_submit()
