# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingRequest(Document):
	@frappe.whitelist()
	def employee_skills(self, employee):
		skill_map = frappe.get_doc("Employee Skill Map", employee)
		skills = []
		courses = []
		

		for skill in skill_map.employee_skills:
			skills.append({
				"skill": skill.skill,
				"proficiency": skill.proficiency,
				"evaluation_date": skill.evaluation_date
			})
		
		for course in skill_map.custom_courses:
			courses.append({
				"course_assignment": course.course_assignment,
				"date": course.date
			})
		
		return {
			"skills": skills,
			"courses": courses
		}
