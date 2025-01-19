# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CourseAssignment(Document):
	def validate(self):
		pass
	@frappe.whitelist()
	def expense_claim(self):
		course_costing = frappe.db.get_value("Course Costing", {"training_course": self.training_course, "date": ["Between", [self.date, self.to_date]], "docstatus": 1}, ["name", "total_actual_cost", "total_estimated_cost", "claims_included"], as_dict=1)
		if course_costing:
			course_costing_doc = frappe.get_doc("Course Costing", course_costing.name)
			if course_costing.claims_included:
				expense_claim = frappe.new_doc("Expense Claim")
				expense_claim.employee = self.employee
				expense_claim.posting_date = self.date
				expense_claim.company = frappe.db.get_single_value("Global Defaults", "default_company")
				expense_claim.custom_course_assignment = self.name
				for row in course_costing_doc.expenses_details:
					expense_claim.append("expenses", {
						"expense_type": row.claim_type,
						"amount": row.amount,
						"sanctioned_amount": row.amount,
						"description": row.claim_type
					})
				expense_claim.save(ignore_permissions=True)
				return expense_claim.name
			else:
				return "Claims not included in course costing"
		else:
			return "No course costing found for this course"
		
