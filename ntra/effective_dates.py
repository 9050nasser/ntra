import frappe
from frappe.utils import nowdate

def before_save(doc, method):
    if not doc.get("__islocal"):  # Check if this is an update
        # Fetch the latest version of this employee
        latest_doc = frappe.get_doc(doc.doctype, doc.name)
        
        # Archive the current version
        latest_doc.custom_to_effective_date = nowdate()

        # Create a new version
        new_doc = frappe.copy_doc(latest_doc)
        new_doc.name = f"{latest_doc.name}-v{latest_doc.custom_version_number + 1}"
        new_doc.custom_version_number = (latest_doc.custom_version_number or 0) + 1
        new_doc.custom_from_effective_date = nowdate()
        new_doc.custom_to_effective_date = None
        new_doc.flags.ignore_permissions = True
        new_doc.insert()
        frappe.db.commit()
        
        # Prevent saving the current document (it's now archived)
        frappe.throw("A new version has been created for this employee.")

@frappe.whitelist()
def get_version_history(employee_name):
    versions = frappe.get_all(
        "Employee",
        filters={"name": employee_name},
        fields=["custom_version_number", "custom_from_effective_date", "custom_to_effective_date"],
        order_by="custom_version_number asc"
    )
    return versions

