# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Contracts(Document):
	def autoname(self):
		if self.number_of_extension > 1:
			self.name = f"{self.contract_reference}-{self.number_of_extension-1}"
		else:
			self.name = f"{self.contract_reference}"
	def before_insert(self):
		self.validate()
	def validate(self):
		number = frappe.db.get_value(self.doctype, {"employee": self.employee, "docstatus": 1, "document_status": "Approved"}, "Max(number_of_extension)")

		contract_reference = frappe.db.get_value(self.doctype, {}, "Max(Contract_reference)")
		self.number_of_extension = int(number) + 1 if number else 1
		if not self.contract_reference:
			self.contract_reference =  int(contract_reference) + 1 if contract_reference else 1
