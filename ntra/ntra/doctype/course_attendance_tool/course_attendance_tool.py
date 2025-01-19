# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
import json
from frappe.model.document import Document


class CourseAttendanceTool(Document):
	pass


@frappe.whitelist()
def get_student_attendance_records(date, training_course = None, session = None, employee = None):
	conditions = ""
	if training_course:
		conditions += f" AND p.training_course = \"{training_course}\" "
	if session:
		conditions += f" AND c.training_session = \"{session}\" "
	if employee:
		conditions += f" AND p.employee = \"{employee}\" "
	students = frappe.db.sql(f"""
			SELECT
				c.attendance as status,
				c.name as parent,
				p.employee as name, 
				p.employee_name,
				c.training_session as session,
				p.training_course as course
			From `tabSession Assignment` c
			INNER JOIN `tabCourse Assignment` p ON c.parent = p.name
			where c.date ="{date}" {conditions}
	""", as_dict=True)
	return students

@frappe.whitelist()
def mark_student_present_or_absent(session_names):
	cnames = json.loads(session_names)
	for cname in cnames:
		frappe.db.set_value("Session Assignment", cname["name"], "attendance", "Present" if cname['checked'] else "Absent")
	
	return