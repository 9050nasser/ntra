# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ConsolidatedOvertime(Document):
	def on_submit(self):
		attendance_rule = frappe.db.get_value("Employee", self.employee, "custom_attendance_rule")
		overtime_salary_component = frappe.db.get_value("Attendance Rule", attendance_rule, "overtime_salary_component")
		self.make_additional_salary(overtime_salary_component)

	def make_additional_salary(self, salary_component):
		additional_salary = frappe.get_doc(dict(
			doctype = "Additional Salary",
			employee = self.employee,
			salary_component = salary_component,
			payroll_date = self.date,
			amount = self.amount,
			ref_doctype = "Consolidated Overtime",
			ref_docname = self.name
		))
		additional_salary.insert(ignore_if_duplicate=True)
		additional_salary.submit()
