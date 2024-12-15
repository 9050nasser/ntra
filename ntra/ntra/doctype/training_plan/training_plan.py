# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TrainingPlan(Document):
	@frappe.whitelist()
	def get_employees(self):
		filters = {"status": "Approved", "date_imcq": ["Between", [self.from_date, self.to_date]]}
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


	@frappe.whitelist()
	def get_training_actual_cost(self):
		for row in self.table_tqgd:
			courses = frappe.db.get_all("Course Costing", filters={"training_course": row.training_course}, fields=["*"])
			return courses


	@frappe.whitelist()
	def get_training_requests(self):
		reqs = []
		for course in self.table_tqgd:
			filters = {"status": "Approved", "date_imcq": ["Between", [self.from_date, self.to_date]], "training_course": course.training_course}
			requests = frappe.db.get_all("Training Request", filters=filters, fields=["*"])
			for request in requests:
				reqs.append({
					"training_request": request.name,
					"employee": request.employee,
					"designation": request.designation,
					"training_course": request.training_course
				})
		return reqs