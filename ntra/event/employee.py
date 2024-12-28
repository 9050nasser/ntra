import frappe

def validate(doc, method):
    if doc.get("__islocal"):
        if not doc.custom_contract_type:
            frappe.throw("Contract Type is Mandatory")
        doc.employee_number = str(frappe.db.get_value("Contract Type", doc.custom_contract_type, "current_number"))
        frappe.db.set_value("Contract Type", doc.custom_contract_type, "current_number", int(doc.employee_number) + 1 )