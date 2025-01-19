# Copyright (c) 2025, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, flt


class RetroPay(Document):
	def validate(self):
		self.calculate_unpaid_days()

	def calculate_unpaid_days(self):
		# Ensure employee joining date is available
		if not self.employee_joining_date:
			frappe.throw("Employee Joining Date is missing.")
		
		# Fetch the first salary slip start date
		first_salary_slip = frappe.db.sql("""
			SELECT MIN(start_date) FROM `tabSalary Slip`
			WHERE employee = %s
		""", (self.employee), as_dict=False)

		# Extract the first start_date from the query result
		first_salary_date = first_salary_slip[0][0] if first_salary_slip else None
		attendance = frappe.db.sql("""SELECT count(name) FROM `tabAttendance` WHERE employee = %s AND status = 'Present' AND attendance_date BETWEEN %s AND %s AND docstatus = 1""", (self.employee, self.employee_joining_date, first_salary_date), as_dict=False)
		attendance = attendance[0][0] if attendance else None
		print(attendance)
		self.actual_working_days = attendance
		self.first_salary_date = first_salary_date
		if not first_salary_date:
			frappe.throw(f"No salary slips found for Employee {self.employee}.")

		# Calculate unpaid days
		unpaid_days = date_diff(first_salary_date, self.employee_joining_date)
		# Update the uncalculated_days field
		self.uncalculated_days = unpaid_days

		# Optionally, calculate retro pay based on unpaid days
		if self.net_salary:
			daily_wage = flt(self.net_salary) / 30  # Assuming 30 days in a month
			retro_pay_amount = daily_wage * attendance
			self.retro_pay_amount = retro_pay_amount
		else:
			self.retro_pay_amount = 0

