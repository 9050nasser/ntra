# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date


class SecurityClearance(Document):
	def validate(self):
		self.set_exp_date()
		self.update_job_applicant()

	def set_exp_date(self):
		if self.date:
			self.expiration_date = add_to_date(self.date, years=5)

	def update_job_applicant(self):
		if self.job_applicant:
			job_applicant = frappe.get_doc("Job Applicant", self.job_applicant)
			if self.status == "Waiting Response" or self.docstatus == 0:
				job_applicant.status = "Waiting Security Clearance"
			if self.status == "Clearance Granted":
				job_applicant.status = "Clearance Granted"
			if self.status == "Clearance Denied":
				job_applicant.status = "Clearance Denied"
			job_applicant.save()
			frappe.db.commit()
