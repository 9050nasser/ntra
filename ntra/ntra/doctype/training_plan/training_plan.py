# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingPlan(Document):
	@frappe.whitelist()
	def get_employees(self):
		filters = {"status": "Approved", "date_imcq": ["Between", [getattr(self, "from"), self.to]]}
		if self.branch:
			filters.update({"branch": self.branch})
		if self.department:
			filters.update({"department": self.department})
		if self.designation:
			filters.update({"designation": self.designation})
		if self.training_course_type:
			filters.update({"training_course_type": self.training_course_type})
		courses = []
		x = frappe.db.get_all("Training Request", filters=filters, fields=["training_course", "COUNT(*) as count"], group_by="training_course")
		for y in x:
			courses.append({
				"training_course": y.training_course,
				"count":  y.count
			})
		return courses
