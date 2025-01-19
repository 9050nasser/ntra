# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CourseCosting(Document):
	def validate(self):
		# self.calculate_totals() 
		pass

	def calculate_totals(self):
		total = 0
		total_actual = 0
		for row in self.table_qyub:
			total += row.estimated_cost
			total_actual += row.actual_cost
		self.total_estimated_cost = total
		self.total_actual_cost = total_actual


