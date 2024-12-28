# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
import json
from frappe.model.document import Document


class CourseAttendanceTool(Document):
	pass


@frappe.whitelist()
def get_student_attendance_records(training_course, date, session):
	employees = frappe.db.get_list("Course Assignment", {"training_course": training_course}, ["name as parent", "employee as name", "employee_name", "'Absent' as Status"])
	students = []
	for employee in employees:
		if frappe.db.get_value("Session Assignment", {"date": date, "parent": employee.parent, "training_session": session}, ["name"]):
			employee.status = frappe.db.get_value("Session Assignment", {"date": date, "parent": employee.parent, "training_session": session}, ["attendance"])
			students.append(employee)
	return students

@frappe.whitelist()
def mark_student_present_or_absent(date, session, students):
	students = json.loads(students)
	for student in students:
		frappe.db.set_value("Session Assignment", {"date": date, "parent": student['parent'], "training_session": session}, "attendance", "Present" if student['checked'] else "Absent")
	
	return 