import frappe
def after_insert(doc, method):
    parent_task = ""
    if doc.parent_goal:
        p_goal_name = frappe.db.get_value("Goal", doc.parent_goal, "goal_name")
        parent_task = frappe.db.get_value("Task", {"subject": p_goal_name, "is_group": 1})
    if not frappe.db.exists("Task", {"subject": doc.goal_name, "parent": parent_task}):
        task = frappe.get_doc({
            "doctype": "Task",
            "subject": doc.goal_name,
            "status": "Open",
            "description": doc.description,
            "priority": "Medium",
            "is_group": doc.is_group,
            "parent_task": parent_task
        })
        
        task.insert()

