# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingCourseSchedule(Document):
	def validate(self):
		self.make_assignment()
	
	def make_assignment(self):
        # Fetch the training plan document
		plans = frappe.get_doc("Training Plan", self.training_plan)

        # Iterate through the training plan's courses and employees
		# for course in plans.table_tqgd:  # Assuming this table holds courses
			
		for employee in plans.table_oyzi:  # Assuming this table holds employees
			if employee.training_course == self.training_course:
				assignment = frappe.get_doc({
					"doctype": "Course Assignment",
					"employee": employee.employee,
					"date": plans.from_date,  # Access 'from_date' instead of 'from'
					"to_date": plans.to_date,
					"training_course": employee.training_course,  # Assuming each course has a 'training_course' field
					"table_oozg": [
						{
							"training_session": session.session,
							"date": session.date,
							"time": session.time,
							"location": session.location,
						}
						for session in self.table_exht  # Ensure 'table_exht' is properly defined in this document
					]
				})
				assignment.insert(ignore_permissions=True)


			



