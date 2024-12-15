import frappe

@frappe.whitelist()
def create_bulk_assignment(training_course_schedule, training_plan):
    try:
        # Fetch the required documents
        course_schedule = frappe.get_doc("Training Course Schedule", training_course_schedule)
        plan = frappe.get_doc("Training Plan", training_plan)

        # Validate data presence
        if not course_schedule.table_exht:
            frappe.throw("No sessions found in the course schedule.")
        if not plan.table_oyzi:
            frappe.throw("No employees found in the training plan.")

        # Iterate over employees and create assignments
        for employee in plan.table_oyzi:
            assignment = frappe.new_doc("Course Assignment")
            assignment.employee = employee.employee
            assignment.date = plan.from_date
            assignment.to_date = plan.to_date
            assignment.training_course = employee.training_course
            for cost in plan.table_tqgd:
                assignment.enrollment_cost = cost.actual_cost_per_course if cost.training_course == employee.training_course else 0
            
            # Append sessions to the child table
            for session in course_schedule.table_exht:
                assignment.append("table_oozg", {
                    "training_session": session.session,
                    "date": session.date,
                    "time": session.time,
                    "location": session.location
                })
            
            assignment.insert()

        # Commit all changes
        frappe.db.commit()
        return {"status": "success", "message": "Assignments created successfully."}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Bulk Assignment Error")
        return {"status": "error", "message": str(e)}
    
@frappe.whitelist()
def update_employee_trainings():
    # Fetch all attended course assignments
    assignments = frappe.db.get_all(
        "Course Assignment",
        filters={"enrollment_status": "Attended"},
        fields=["employee", "training_course", "date", "enrollment_cost"]
    )

    for assignment in assignments:
        try:
            # Fetch the corresponding Employee document
            employee_doc = frappe.get_doc("Employee", assignment.employee)
            # Append the course details if not already present
            employee_doc.set("custom_employee_courses", [])
            employee_doc.append("custom_employee_courses", {
                "course": assignment.training_course,
                "date": assignment.date,
                "cost": assignment.enrollment_cost
            })

            # Save the Employee document
            employee_doc.save(ignore_permissions=True)
            frappe.db.commit()
            print(f"Updated training for employee: {employee_doc.name}")
            frappe.log(f"Updated training for employee: {employee_doc.name}")

        except frappe.DoesNotExistError:
            frappe.log_error(f"Employee {assignment.employee} does not exist.", "Update Employee Trainings")
        except Exception as e:
            print(f"Error updating employee {assignment.employee}: {str(e)}", "Update Employee Trainings")
            frappe.log_error(f"Error updating employee {assignment.employee}: {str(e)}", "Update Employee Trainings")


