import frappe
from frappe import _
from datetime import datetime
from frappe.utils import today
from frappe.desk.form import assign_to
from frappe.utils import add_to_date, today, date_diff


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


def validate_maternity_leave(doc, method):
    maternity_leaves = frappe.db.get_all("Leave Type", filters={"custom_maternity_leave": 1}, fields=["name"], pluck="name")

    leaves = tuple(maternity_leaves)
    gender = frappe.get_doc("Employee", doc.employee).gender
    if doc.leave_type in leaves and gender != "Female":
        frappe.throw(_("Only female employees are eligible for Maternity Leave."))

def validate_attachment(doc, method):
    maternity_leaves = frappe.db.get_all("Leave Type", filters={"custom_maternity_leave": 1}, fields=["name"], pluck="name")
    leaves = tuple(maternity_leaves)
    files = frappe.db.get_all("File", filters={"attached_to_doctype": doc.doctype, "attached_to_name": doc.name})
    if doc.leave_type in leaves:
        if len(files) < 1:
            frappe.throw(_("An attachment is required for Maternity Leave."))

@frappe.whitelist()
def get_leave_balance(leave_type_name, employee):

    # Get the leave type document to fetch max allocation
    leave_type = frappe.get_doc("Leave Type", leave_type_name)
    maximum_allocation = leave_type.max_leaves_allowed

    # Fetch all approved leave applications for the given leave type
    all_leaves = frappe.db.get_all("Leave Application", filters={"leave_type": leave_type.name, "status": "Approved", "employee": employee}, fields=["total_leave_days"])

    # Sum up the total leave days from all approved leave applications
    total_leave_taken = sum(leave.get("total_leave_days", 0) for leave in all_leaves)

    # Return the remaining balance
    return maximum_allocation - total_leave_taken


@frappe.whitelist()
def leave_without_pay(doc, method):
    leave_types = frappe.db.get_all("Leave Type", filters={"is_lwp": 1}, fields=["name"], pluck="name")

    lwp = tuple(leave_types)
    leave_type = frappe.get_doc("Leave Type", doc.leave_type)
    employee = frappe.get_doc("Employee", doc.employee)
    from_date = employee.date_of_joining
    end_date = add_to_date(from_date, years=leave_type.custom_recalculation_period_years, days=-1)
    order_date = doc.from_date

    maximum_allowed = date_diff(end_date, order_date)
    all_maximum_allowed = leave_type.max_leaves_allowed

    if doc.leave_type in lwp:
        if datetime.strptime(doc.to_date, "%Y-%m-%d").date() > end_date:
            frappe.throw(_(f"You Cannot Submit a Leave Application After {end_date}"))
