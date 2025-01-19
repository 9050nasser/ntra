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
			filters = {
				"status": "Approved",
				"date_imcq": ["Between", [self.from_date, self.to_date]],
				"training_course": course.training_course,
			}

			# Fetch approved requests that are not already in another training plan
			requests = frappe.db.sql("""
				SELECT 
					tr.name AS training_request,
					tr.employee,
					tr.designation,
					tr.training_course
				FROM 
					`tabTraining Request` tr
				WHERE 
					tr.status = 'Approved'
					AND tr.date_imcq BETWEEN %(from_date)s AND %(to_date)s
					AND tr.training_course = %(training_course)s
					AND NOT EXISTS (
						SELECT 1 
						FROM `tabTraining Plan` tp 
						JOIN `tabTraining Plan Employee` tpd ON tpd.parent = tp.name
						WHERE tpd.training_request = tr.name and tp.docstatus = 1
					)
			""", {
				"from_date": self.from_date,
				"to_date": self.to_date,
				"training_course": course.training_course
			}, as_dict=True)

			reqs.extend(requests)
		
		return reqs

	
	def check_duplicates(self):
    # Iterate through each row in the child table
		for row in self.table_oyzi:
			# Query to find duplicates
			requests = frappe.db.sql("""
				SELECT tp.name as training_plan, tpe.training_request
				FROM `tabTraining Plan` tp
				LEFT JOIN `tabTraining Plan Employee` tpe ON tp.name = tpe.parent
				WHERE tp.name != %s 
				AND tpe.training_request = %s
				AND tp.docstatus = 1
			""", (self.name, row.training_request), as_dict=True)

			# If duplicates are found, throw an error
			if requests:
				# Extract duplicate training plan details
				plan_names = [request.get('training_plan') for request in requests]
				frappe.throw(
					f"Training Request {row.training_request} already exists in Training Plan(s): " +
					", ".join([f"<a href='/app/training-plan/{name}'>{name}</a>" for name in plan_names])
				)
	@frappe.whitelist()
	def check_correct_courses(self):
		# Create a set of valid training courses from table_oyzi
		valid_courses = {row2.training_course for row2 in self.table_oyzi}
		
		# Filter rows in table_tqgd where training_course is in valid_courses
		self.table_tqgd = [row for row in self.table_tqgd if row.training_course in valid_courses]


