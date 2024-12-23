import frappe
from frappe import _
from frappe.utils import nowdate, add_days
# def after_insert(doc, method):
#     if not frappe.db.exists("Task", {"custom_objective": doc.name}):
#         create_task(doc.goal_name, doc.description, doc.is_group, doc.parent_goal, doc.name)
def validate(doc, method):
    if not frappe.db.exists("Task", {"custom_objective": doc.name}):
        create_task(doc.goal_name, doc.description, doc.is_group, doc.parent_goal, doc.name)
    else:
        frappe.db.set_value("Task", {"custom_objective": doc.name}, {
            "description": doc.description,
            "subject": doc.goal_name
        })


def create_task(goal_name, description, is_group, parent_goal, name, priority="Medium"):
    if parent_goal:
        parent_task = frappe.db.get_value("Task", {"custom_objective": parent_goal, "is_group": 1})
    else:
        parent_task = ""
    task = frappe.get_doc({
        "doctype": "Task",
        "subject": goal_name,
        "status": "Open",
        "description": description,
        "priority": priority,
        "is_group": is_group,
        "parent_task": parent_task,
        "exp_start_date": nowdate(),
        "exp_end_date": add_days(nowdate(), 7),
        "custom_objective": name
    })
    task.insert()
    frappe.db.set_value("Task", task.name, "custom_objective", name)


@frappe.whitelist()
def create_edit_task(goal_name, description, employee, objective):
    rt_employee = frappe.db.get_value("Employee", employee, "reports_to")
    rt_id = frappe.db.get_value("Employee", rt_employee, "user_id")
    if not rt_id:
        frappe.throw(_("Reports to Person must have linked user"))
    goal = frappe.get_doc({
        "doctype": "Task",
        "subject": goal_name,
        "status": "Open",
        "description": description,
        "completed_by": rt_id,
        "priority": "Medium",
        "exp_start_date": nowdate(),
        "exp_end_date": add_days(nowdate(), 7),
        "custom_objective": objective,
        "custom_is_edit": 1
    })
    goal.insert()
    return goal.name

@frappe.whitelist()
def edit_objective(objective, description, goal_name):
    objective = frappe.get_doc("Goal", objective)
    objective.description = description
    objective.goal_name = goal_name
    objective.save()
    return True