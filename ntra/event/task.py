import frappe
def after_save(doc, method):
    p_task_subject = frappe.db.get_value("Task", doc.parent_task, "subject")
    p_goal_name = frappe.db.get_value("Goal", {"goal_name":p_task_subject, "is_group": 1})
    frappe.db.set_value("Goal", {"goal_name": doc.subject, "parent_goal": p_goal_name}, "custom_weight_progress", doc.progress)
    frappe.db.set_value("Goal", doc.custom_objective, "custom_weight_progress", doc.progress)

@frappe.whitelist()
def update_complete(objective):
    frappe.db.set_value("Task", objective, "status", "Completed")
    frappe.db.set_value("Task", objective, "progress", 100)
    frappe.db.commit()
    return True