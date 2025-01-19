# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.query_builder.custom import ConstantColumn
from frappe.query_builder.functions import Coalesce
from frappe.query_builder.terms import SubQuery
from collections import defaultdict
from functools import reduce  # To combine conditions dynamically
class BulkAbsenceProcessing(Document):
    @frappe.whitelist()
    def process_absences(self):
        hr_setting = frappe.get_cached_doc("Additional HR Setting")
        employee_attendance = defaultdict(lambda: {"employee": None, "attendance": []})
        if not hr_setting.enable_absence_auto_processing:
            return
        for record in self.employee_table:
            employee = record.employee
            attendance_entry = {
                "name": record.attendance,
                "date": record.attendance_date,
                "shift": record.shift
            }
            if not employee_attendance[employee]["employee"]:
                employee_attendance[employee]["employee"] = employee
            employee_attendance[employee]["attendance"].append(attendance_entry)

        # Convert defaultdict to a list
        result = list(employee_attendance.values())
        for record in result:
            # frappe.throw(f"{record}")
            # employee = frappe.get_doc("Employee", record["employee"])
            employee = record['employee']
            attendance = record.get('attendance', [])
            
            # Get leave balances
            casual_leave_balance = get_leave_balance_on(
                employee, hr_setting.first_fallback_leave_type, self.from_date, self.to_date,
                consider_all_leaves_in_the_allocation_period=True, for_consumption=True
            ).get("leave_balance", 0)
            
            annual_leave_balance = get_leave_balance_on(
                employee, hr_setting.second_fallback_leave_type, self.from_date, self.to_date,
                consider_all_leaves_in_the_allocation_period=True, for_consumption=True
            ).get("leave_balance", 0)
            # frappe.throw(f"{casual_leave_balance} {annual_leave_balance}")
            # Get shift hours
            
            
            # Initialize index
            idx = -1

            # Deduct casual leaves
            frappe.msgprint(f"{casual_leave_balance}       {annual_leave_balance}")
            deduction = min(casual_leave_balance, hr_setting.max_day_per_month)
            frappe.msgprint(f"{deduction}")
            
            if deduction:
                for x in range(deduction):
                    casual_leave_balance = get_leave_balance_on(
                        employee, hr_setting.first_fallback_leave_type, self.from_date, self.to_date,
                        consider_all_leaves_in_the_allocation_period=True, for_consumption=True
                    ).get("leave_balance", 0)
                    if casual_leave_balance > 0:
                        if x < len(attendance):
                            attendance_date = attendance[x].get('date')
                            deduct_leave(employee, "Casual Leave", attendance_date)
                            idx = x
            if idx == -1:
                idx=0
            # Deduct annual leaves
            for x in range(idx + 1, len(attendance)):
                annual_leave_balance = get_leave_balance_on(
                    employee, hr_setting.second_fallback_leave_type, self.from_date, self.to_date,
                    consider_all_leaves_in_the_allocation_period=True, for_consumption=True
                ).get("leave_balance", 0)
                if annual_leave_balance > 0:
                    attendance_date = attendance[x].get('date')
                    deduct_leave(employee, "Annual Leave", attendance_date)

            # Update attendance if no leave balance
            if not casual_leave_balance and not annual_leave_balance:
                for att in attendance:
                    if att.get('shift',None):
                        shift_hours = get_shift_hours(employee, att.get('shift',None), date = self.from_date)
                    else:
                        shift_hours = get_shift_hours(employee , date = self.from_date)
                    attendance_name = att.get('name')
                    if attendance_name:
                        frappe.db.set_value("Attendance", attendance_name, "working_hours", -shift_hours)
                        # frappe.db.set_value("Attendance", attendance_name, "status", "")

        frappe.db.commit()
        frappe.msgprint(f"{len(self.employee_table)} records processed successfully.")
        return {"message": f"{len(self.employee_table)} records processed successfully."}


    @frappe.whitelist()
    def get_employees(self, advanced_filters: list) -> list:
        quick_filter_fields = [
            "company",
            "employment_type",
            "branch",
            "department",
            "designation",
            "grade",
        ]
        filters = [[d, "=", self.get(d)] for d in quick_filter_fields if self.get(d)]
        filters += advanced_filters

        Attendance = frappe.qb.DocType("Attendance")
        employees_with_assignments = SubQuery(
            frappe.qb.from_(Attendance)
            .select(Attendance.employee)
            .distinct()
            .where((Attendance.attendance_date >= self.from_date) & (Attendance.attendance_date <= self.to_date)& (Attendance.docstatus == 1))
        )

        Employee = frappe.qb.DocType("Employee")
        Grade = frappe.qb.DocType("Employee Grade")
        conditions = [
            (Employee.status == "Active"),
            (Attendance.status == "Absent"),
            (Attendance.attendance_date >= self.from_date),
            (Attendance.attendance_date <= self.to_date),
            (Attendance.docstatus == 1),
        ]

        # Add optional conditions
        if self.employee_grade:
            conditions.append(Employee.grade == self.employee_grade)
        if self.employment_type:
            conditions.append(Employee.employment_type == self.employment_type)
        if self.branch:
            conditions.append(Employee.branch == self.branch)
        if self.designation:
            conditions.append(Employee.designation == self.designation)
        if self.department:
            conditions.append(Employee.department == self.department)
        combined_conditions = reduce(lambda x, y: x & y, conditions)
        query = (
            frappe.qb.get_query(
                Employee,
                fields=[Employee.employee, Employee.employee_name],
                filters=filters,
            )
            
            .left_join(Attendance)
            .on(Employee.name == Attendance.employee)
            .where(
               combined_conditions
            )
            .select(
                Coalesce(Attendance.attendance_date).as_("attendance_date"),
                Coalesce(Attendance.name).as_("attendance_name"),
                Coalesce(Attendance.status).as_("status"),
                Coalesce(Employee.designation).as_("designation"),
                Coalesce(Attendance.shift).as_("shift"),
            ).orderby(Employee.name, Attendance.attendance_date)
        )
        data =  query.run(as_dict=True)
        self.employee_table = []
        for x in data:
            self.append('employee_table',{
                "employee":x.employee,
                "employee_name":x.employee_name,
                "attendance_date":x.attendance_date,
                "attendance":x.attendance_name,
                "current_status":x.status,
                "designation":x.designation,
                "shift":x.shift,
            })
            pass
        return data
    pass

from hrms.hr.doctype.leave_application.leave_application import get_leave_details, get_leave_balance_on

def get_leave_balance(employee, leave_type,from_date ):
    # Fetch leave balance from Leave Ledger Entry
    available_leave = get_leave_details(employee, from_date)
    remaining = 0
    if leave_type in available_leave["leave_allocation"]:
        # opening balance
        remaining = available_leave["leave_allocation"][leave_type]["remaining_leaves"]

    return remaining
def deduct_leave(employee, leave_type, date):
    leave_application = frappe.new_doc("Leave Application")
    leave_application.employee = employee
    leave_application.leave_type = leave_type
    leave_application.from_date = date
    leave_application.to_date = date
    leave_application.custom_is_an_exception = 1
    leave_application.status = "Approved"
    leave_application.follow_via_email =0
    leave_application.insert()
    leave_application.submit()

from datetime import datetime
def get_shift_hours(employee, shift=None, date=None):
    # Fetch shift duration for the employee
    employee = frappe.get_cached_doc("Employee", employee)
    shift_type =None
    if(shift):
        shift_type = frappe.get_cached_doc('Shift Type', shift)

    if employee.default_shift and not shift:
        shift_type = frappe.get_cached_doc('Shift Type', employee.default_shift)
    if not shift_type:
        data = frappe.db.sql(f"SELECT shift_type FROM `tabShift Assignment` WHERE employee = '{employee.name}' AND docstatus = 1 order by start_date DESC" ,as_dict=True)
        if data:
            shift_type = frappe.get_cached_doc('Shift Type', data[0]['shift_type'])
    # frappe.throw(f"{shift_type}")
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
    
    