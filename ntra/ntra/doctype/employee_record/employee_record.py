# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeRecord(Document):
	def create_permission(self):
		permission = frappe.new_doc("Mission Application")
		permission.employee = self.employee
		permission.permission_type = self.permission_type
		permission.from_time = self.start_time
		permission.to_time = self.end_time
		permission.posting_date = self.date
		permission.date = self.date
		permission.reason = self.reason
		permission.status = self.status
		permission.insert()
		pass
	def create_mission(self):
		mission = frappe.new_doc("Mission Application")
		mission.employee = self.employee
		mission.mission_type = self.mission_type
		mission.from_time = self.start_time
		mission.to_time = self.end_time
		mission.posting_date = self.date
		mission.reason = self.reason
		mission.status = self.status

		mission.insert()
		pass
	def on_submit(self):
		if self.type == "Permission":
			self.create_permission()
		elif self.type == "Mission":
			self.create_mission()
		pass
	pass
