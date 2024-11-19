# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TrainingCourse(Document):
	def validate(self):
		self.create_course_item()

	def create_course_item(self):
		exist = frappe.db.exists("Item", self.course_name)

		if not exist:
			course_item = frappe.get_doc({
				"doctype": "Item",
				"item_code": self.course_name,
				"item_group": "Services",
				"is_stock_item": 0,
				"custom_course_item": 1

			})
			course_item.insert()
		
