import frappe
from frappe import _
@frappe.whitelist()
def create_bulk_assignment(training_course_schedule, training_plan):
    try:
        # Fetch the required documents
        course_schedule = frappe.get_doc("Training Course Schedule", training_course_schedule)
        plan = frappe.get_doc("Training Plan", training_plan)
        is_duplicated = frappe.db.exists({"doctype": "Course Assignment", "training_course": course_schedule.training_course, "training_course_schedule": course_schedule.name})
        if is_duplicated:
            frappe.throw(_("Assignments already created for this course schedule."))
        # Validate data presence
        if not course_schedule.table_exht:
            frappe.throw("No sessions found in the course schedule.")
        if not plan.table_oyzi:
            frappe.throw("No employees found in the training plan.")

        # Iterate over employees and create assignments
        for employee in plan.table_oyzi:
            if employee.training_course == course_schedule.training_course:
                assignment = frappe.new_doc("Course Assignment")
                assignment.employee = employee.employee
                assignment.date = course_schedule.from_date
                assignment.to_date = course_schedule.to_date
                assignment.training_course = employee.training_course
                assignment.training_course_schedule = course_schedule.name
                for cost in plan.table_tqgd:
                    assignment.enrollment_cost = cost.actual_cost_per_course
                
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
        fields=["name", "employee", "training_course", "date", "enrollment_cost"]
    )

    # Log the number of assignments fetched for debugging
    frappe.log(f"Fetched {len(assignments)} course assignments.")

    for assignment in assignments:
        try:
            # Fetch the corresponding Employee document
            employee_doc = frappe.get_doc("Employee", assignment.employee)
            frappe.log(f"Found employee: {employee_doc.name}")

            # Ensure that the Employee Skill Map exists
            try:
                employee_skillmap = frappe.get_doc("Employee Skill Map", assignment.employee)
                frappe.log(f"Found Employee Skill Map for {employee_doc.name}")
            except frappe.DoesNotExistError:
                employee_skillmap = None
                frappe.log(f"No Employee Skill Map found for {employee_doc.name}")

            # Remove duplicates from custom_employee_courses
            courses_to_remove = []
            for course in employee_doc.custom_employee_courses:
                if course.course == assignment.training_course and course.date == assignment.date:
                    courses_to_remove.append(course)

            if courses_to_remove:
                frappe.log(f"Removing {len(courses_to_remove)} duplicate courses from Employee's custom_employee_courses.")
            for course in courses_to_remove:
                employee_doc.custom_employee_courses.remove(course)

            # Remove duplicates from custom_courses if Employee Skill Map exists
            if employee_skillmap:
                courses_to_remove_skillmap = []
                for course2 in employee_skillmap.custom_courses:
                    if course2.course_assignment == assignment.training_course and course2.date == assignment.date:
                        courses_to_remove_skillmap.append(course2)

                if courses_to_remove_skillmap:
                    frappe.log(f"Removing {len(courses_to_remove_skillmap)} duplicate courses from Employee Skill Map.")
                for course2 in courses_to_remove_skillmap:
                    employee_skillmap.custom_courses.remove(course2)

            # Append the new course details
            employee_doc.append("custom_employee_courses", {
                "course": assignment.training_course,
                "date": assignment.date,
                "cost": assignment.enrollment_cost
            })

            if employee_skillmap:
                employee_skillmap.append("custom_courses", {
                    "course_assignment": assignment.name,
                    "date": assignment.date,
                })
                employee_skillmap.save(ignore_permissions=True)
                frappe.log(f"Saved Employee Skill Map for {employee_doc.name}")

            employee_doc.save(ignore_permissions=True)
            frappe.log(f"Updated training for employee: {employee_doc.name}")

        except frappe.DoesNotExistError as e:
            frappe.log_error(f"Employee {assignment.employee} does not exist: {str(e)}", "Update Employee Trainings")
        except Exception as e:
            frappe.log_error(f"Error updating employee {assignment.employee}: {str(e)}", "Update Employee Trainings")
            frappe.log(f"Error updating employee {assignment.employee}: {str(e)}")
    
    frappe.db.commit()
    frappe.log("Employee training update completed.")



@frappe.whitelist()
def get_designation_wise_employees(doctype, txt, searchfield, start, page_len, filters):
    # Example logic: Fetch employees based on a designation filter
    designation = filters.get("designation")
    if not designation:
        return []

    return frappe.db.sql("""
        SELECT tc.name 
        FROM `tabTraining Course` tc
        LEFT JOIN `tabDesignations` d ON tc.name = d.parent
        WHERE FIND_IN_SET(%s, d.designation) > 0;
    """, (designation))

