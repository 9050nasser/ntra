# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TrainingPlan(Document):

	def validate(self):
		self.check_duplicates()

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
		all_courses = []
		for row in self.table_tqgd:
			# Fetch all matching courses for the current training_course
			courses = frappe.db.get_all(
				"Course Costing",
				filters={"training_course": row.training_course},
				fields=["training_course", "total_actual_cost", "total_estimated_cost"]
			)
			# Add the fetched courses to the main list
			all_courses.extend(courses)
		return all_courses



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
	
	def check_duplicates(self):
		# Check for duplicate training courses
		for row in self.table_oyzi:
			requests = frappe.db.sql("""
			SELECT tp.name as name, tpe.training_course as course FROM `tabTraining Plan` tp
			LEFT JOIN `tabTraining Plan Employee` tpe ON tp.name = tpe.parent
			WHERE tp.name != %s AND tpe.training_course = %s
			""", (self.name, row.training_course), as_dict=True)
			if requests:
            # Create a list of training plan names that already have the course
				plan_courses = [request.get('course') for request in requests]
				frappe.throw(f"Training Course {plan_courses} already exists in Training Plans: <a href='/app/training-plan/{requests[0].name}'>{requests[0].name}</a>")
