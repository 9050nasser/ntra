import frappe
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip, LEAVE_TYPE_MAP
import unicodedata
from datetime import date

import frappe
from frappe import _, msgprint
from frappe.model.naming import make_autoname
from frappe.query_builder import Order
from frappe.query_builder.functions import Count, Sum
from frappe.utils import (
    getdate

)

class CustomSalarySlip(SalarySlip):
    def get_leave_type_map(self) -> dict:
        """Returns (partially paid leaves/leave without pay) leave types by name"""

        def _get_leave_type_map():
            leave_types = frappe.get_all(
                "Leave Type",
                or_filters={"is_ppl": 1, "is_lwp": 1, "custom_is_death_leave":1},
                fields=["name", "is_lwp", "is_ppl", "fraction_of_daily_salary_per_leave", "include_holiday"],
            )
            return {leave_type.name: leave_type for leave_type in leave_types}

        return frappe.cache().get_value(LEAVE_TYPE_MAP, _get_leave_type_map)
    pass
    def calculate_lwp_ppl_and_absent_days_based_on_attendance(
        self, holidays, daily_wages_fraction_for_half_day, consider_marked_attendance_on_holidays
    ):
        lwp = 0
        absent = 0

        leave_type_map = self.get_leave_type_map()
        attendance_details = self.get_employee_attendance(
            start_date=self.start_date, end_date=self.actual_end_date
        )
        
        for d in attendance_details:
            if (
                d.status in ("Half Day", "On Leave")
                and d.leave_type
                and d.leave_type not in leave_type_map.keys()
            ):
                continue

            # skip counting absent on holidays
            if not consider_marked_attendance_on_holidays and getdate(d.attendance_date) in holidays:
                if d.status in ["Absent", "Half Day"] or (
                    d.leave_type
                    and d.leave_type in leave_type_map.keys()
                    and not leave_type_map[d.leave_type]["include_holiday"]
                ):
                    continue

            if d.leave_type:
                fraction_of_daily_salary_per_leave = leave_type_map[d.leave_type][
                    "fraction_of_daily_salary_per_leave"
                ]
            if d.leave_type:
                leave_type = frappe.get_cached_doc('Leave Type', d.leave_type)
            if d.status == "Half Day":
                equivalent_lwp = 1 - daily_wages_fraction_for_half_day

                if d.leave_type in leave_type_map.keys() and leave_type_map[d.leave_type]["is_ppl"]:
                    equivalent_lwp *= (
                        fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
                    )
                lwp += equivalent_lwp

            elif (d.status == "On Leave" and d.leave_type and d.leave_type in leave_type_map.keys() and d.custom_unpaid) or (d.status == "On Leave" and d.leave_type and d.leave_type in leave_type_map.keys() and not leave_type.custom_is_death_leave):
                equivalent_lwp = 1
                if leave_type_map[d.leave_type]["is_ppl"]:
                    equivalent_lwp *= (
                        fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
                    )
                lwp += equivalent_lwp

            elif d.status == "Absent":
                absent += 1

        return lwp, absent
    
    def get_employee_attendance(self, start_date, end_date):
        attendance = frappe.qb.DocType("Attendance")

        attendance_details = (
            frappe.qb.from_(attendance)
            .select(attendance.attendance_date, attendance.status, attendance.leave_type, attendance.custom_unpaid)
            .where(
                (attendance.status.isin(["Absent", "Half Day", "On Leave"]))
                & (attendance.employee == self.employee)
                & (attendance.docstatus == 1)
                & (attendance.attendance_date.between(start_date, end_date))
            )
        ).run(as_dict=1)

        return attendance_details