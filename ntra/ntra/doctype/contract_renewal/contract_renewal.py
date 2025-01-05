# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractRenewal(Document):
	pass
@frappe.whitelist()
def create_new_contract(status, employee_contract):
	if status == "Confirmed":
		old_contract = frappe.get_doc("Contracts", employee_contract)
		contract_copy = frappe.copy_doc(old_contract)
		contract_copy.start = contract_copy.end = None
		contract_copy.insert()
		frappe.db.commit()
		return contract_copy.name