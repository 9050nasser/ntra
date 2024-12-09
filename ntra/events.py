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
    
    if doc.leave_type in lwp:
        from_date = employee.date_of_joining
        order_date = datetime.strptime(doc.from_date, "%Y-%m-%d").date()
        end_date = add_to_date(from_date, years=leave_type.custom_recalculation_period_years, days=-1)
        
        # Calculate the start of the current 5-year period
        recalculation_period_years = leave_type.custom_recalculation_period_years
        while from_date <= order_date:
            end_date = add_to_date(from_date, years=recalculation_period_years, days=-1)
            if order_date <= end_date:
                break
            from_date = add_to_date(from_date, years=recalculation_period_years)
        
        # Get leave balance for the current period
        used_leave_days = frappe.db.sql("""
            SELECT SUM(total_leave_days) 
            FROM `tabLeave Application`
            WHERE employee = %s AND leave_type = %s 
            AND docstatus = 1
            AND from_date BETWEEN %s AND %s
        """, (employee.name, doc.leave_type, from_date, end_date))[0][0] or 0
        
        max_leaves_allowed = leave_type.max_leaves_allowed
        
        # Validate leave
        requested_days = date_diff(doc.to_date, doc.from_date) + 1
        if used_leave_days + requested_days > max_leaves_allowed:
            frappe.throw(_(f"You cannot take more than {max_leaves_allowed} leave days in the current period."))
        
        if order_date > end_date:
            frappe.throw(_(f"You cannot submit a Leave Application after {end_date}."))


from frappe.utils import date_diff, getdate, add_months, flt
from datetime import timedelta

@frappe.whitelist()
def calculate_sick_leave_salary(doc, method):
    # جلب الشرائح من Leave Type
    slabs = frappe.get_doc("Leave Type", doc.leave_type)
    monthly_salary = frappe.db.get_all("Salary Structure Assignment", filters={"employee": doc.employee}, order_by="from_date desc", fields=["*"])[0]
    if slabs.custom_is_sick_leave:
    # حساب عدد الأيام الكلية

        total_days = date_diff(doc.to_date, doc.from_date) + 1
        current_date = getdate(doc.from_date)
        ledger_entries = []

        while current_date <= getdate(doc.to_date):
            # تحديد الشهر الحالي
            month_start = current_date.replace(day=1)
            month_end = add_months(month_start, 1).replace(day=1) - timedelta(days=1)
            days_in_month = min(date_diff(doc.to_date, current_date) + 1, date_diff(month_end, current_date) + 1)
            
            # تحقق من الشريحة
            leave_days = date_diff(current_date, doc.from_date) + 1
            slab = next(
                (s for s in slabs.custom_sick_leave_rule 
                if leave_days >= s.from__day_ and leave_days <= s.to__day_), 
                None
            )
            print(slab.fraction)
            
            if slab:
                # حساب الراتب
                daily_salary = flt(monthly_salary.base) / 30
                calculated_salary = daily_salary * (days_in_month if days_in_month <= 30 else 30) * (slab.fraction / 100)
                calculated_amount_for_duration = daily_salary * (days_in_month if days_in_month <= 30 else 30)
                # إنشاء سجل في Sick Leave Ledger
                ledger_entries.append({
                    "employee": doc.employee,
                    "month": current_date.strftime("%Y-%m-%d"),
                    "leave_days": days_in_month,
                    "calculated_salary": calculated_salary,
                    "calculated_amount_for_duration": calculated_amount_for_duration,
                    "fraction": slab.fraction,
                    "month_start": month_start,
                    "month_end": month_end
                })
            else:
                frappe.throw("No applicable slab found for leave days: {}".format(leave_days))

            # انتقل إلى الشهر التالي
            current_date = add_months(current_date, 1)

        # إدخال السجلات في Sick Leave Ledger
        for entry in ledger_entries:
            frappe.get_doc({
                "doctype": "Sick leave Ledger",
                "employee": entry["employee"],
                "leave_from_date": entry["month_start"],
                "leave_to_date": entry["month_end"],
                "duration": entry["leave_days"],
                "posting_date": doc.posting_date,
                "payroll_date": entry["month"],
                "sick_leave_percent": entry["fraction"],
                "factor": entry["fraction"],
                "calculated_amount": entry["calculated_salary"],
                "calculated_amount_for_duration": entry["calculated_amount_for_duration"],
                "deducted_amount": entry["calculated_amount_for_duration"] - entry["calculated_salary"]
            }).insert()


@frappe.whitelist()
def append_sickleave(doc, method):
    ledgers = frappe.db.get_all("Sick leave Ledger", filters={"employee": doc.employee, "payroll_date": ["Between", [doc.start_date, doc.end_date]]}, fields=["*"])

    for ledger in ledgers:
        doc.append("deductions", {
            "salary_component": ledger.salary_component,
            "amount": ledger.deducted_amount
        })
    doc.save()
    frappe.db.commit()
