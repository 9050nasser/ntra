import frappe
from frappe import _

def before_submit(doc, method):
    goals = frappe.db.get_list("Goal", {"employee": doc.employee, "status": ["!=", "Completed"]})
    if len(goals):
        frappe.throw(_("Employee {0} has {1} in Progess").format(doc.employee, len(goals)))