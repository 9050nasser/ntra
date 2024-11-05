# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ObjectiveTemplate(Document):
	def validate(self):
		self.check_kra_percentage()

	def check_kra_percentage(self):
		total = 0
		for row in self.kras:
			total += row.weightage_
		if total != 100:
			frappe.throw("Total Whieghtage must equal 100%")
