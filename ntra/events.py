import frappe
from frappe import _
from datetime import datetime
from frappe.utils import today
from frappe.desk.form import assign_to

def calculate_rating(doc, method):
    for row in doc.feedback_ratings:
        row.custom_criterial_score_weighted = row.per_weightage * row.custom_criteria_rating_ /100
        row.rating = (row.custom_criterial_score_weighted /100) * 1

def calculate_rating2(doc, method):
    # for row in doc.self_ratings:
    #     row.custom_criterial_score_weighted = row.per_weightage * row.custom_criteria_rating_ /100
    #     row.rating = (row.custom_criterial_score_weighted /100) * 1
    pass

def goal_validation(doc, method):
    if str(doc.end_date) < today():
        frappe.throw(_("You Cannot Update Progress After End Date"))

def create_task(doc, method):
    user = frappe.db.get_value("Employee", doc.employee, "user_id")
    new_task = frappe.new_doc("Task")
    new_task.subject = doc.goal_name
    new_task.exp_start_date = doc.start_date
    new_task.exp_end_date = doc.end_date
    new_task.is_group = doc.is_group
    new_task.insert()
    if user:
       assign_task_to_users(doc, new_task, user) 

def assign_task_to_users(self, task, users):
    args = {
        "assign_to": [users],
        "doctype": task.doctype,
        "name": task.name,
        "description": task.description or task.subject,
    }
    assign_to.add(args)

def update_weight(doc, method):
    # Fetch the total custom weight progress result of child goals
        goals2 = frappe.db.sql("""
            SELECT SUM(custom_weight_progress_result) AS total 
            FROM `tabGoal` 
            WHERE parent_goal = %s
        """, (doc.parent_goal,), as_dict=True)

        # Update the parent goal's custom weight progress
        frappe.db.set_value("Goal", doc.parent_goal, "custom_weight_progress", goals2[0].get("total") or 0)

def create_task(doc, method):
    task = frappe.get_doc({
        "doctype": "Task",
        "subject": doc.goal_name,
        "custom_parent_objective": doc.name,  
    })