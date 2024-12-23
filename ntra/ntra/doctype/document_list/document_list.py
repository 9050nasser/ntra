# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DocumentList(Document):

	def validate(self):

		# frappe.db.get_list('Employee', filter=, pluck='name')
		pass
