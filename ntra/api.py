import frappe
from frappe import _
@frappe.whitelist()
def create_bulk_assignment(training_course_schedule, training_plan):
    try:
        # Fetch the required documents
        course_schedule = frappe.get_doc("Training Course Schedule", training_course_schedule)
        plan = frappe.get_doc("Training Plan", training_plan)

        # Check if assignments are already created
        is_duplicated = frappe.db.exists({
            "doctype": "Course Assignment",
            "training_course": course_schedule.training_course,
            "training_course_schedule": course_schedule.name
        })
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
                
                # Match enrollment cost to the course
                matching_cost = next(
                    (cost.actual_cost_per_course for cost in plan.table_tqgd if cost.training_course == employee.training_course),
                    None
                )
                if matching_cost is not None:
                    assignment.enrollment_cost = matching_cost
                else:
                    assignment.enrollment_cost = 0  # Set a default value if no match is found
                
                # Append sessions to the child table
                for session in course_schedule.table_exht:
                    assignment.append("table_oozg", {
                        "training_session": session.session,
                        "date": session.date,
                        "time": session.time,
                        "location": session.location
                    })

                # Insert the new assignment document
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
                    if course2.course_assignment == assignment.name and course2.date == assignment.date:
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


@frappe.whitelist()
def cancel(doctype, name):
    # Example logic: Fetch employees based on a designation filter
   try:
        doc = frappe.get_doc(doctype, name)
        doc.cancel()
        return {"status": "success", "message": f"{name} cancelled successfully."}
   except  Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_medical_provider():
    # Example logic: Fetch employees based on a designation filter
    condition = ''
    if frappe.form_dict.get("governorate"):
        condition += f"AND MN.governorate ={frappe.form_dict.get("governorate")}"
    if frappe.form_dict.get("area"):
        condition += f"AND MN.city ={frappe.form_dict.get("area")}"
    if frappe.form_dict.get("speciality"):
        condition += f"AND SL.speciality ={frappe.form_dict.get("speciality")}"
    if frappe.form_dict.get("provider_type"):
        condition += f"AND MN.provider_type ={frappe.form_dict.get("provider_type")}"
    if frappe.form_dict.get("name"):
        condition += f"AND MN.name Like '%{frappe.form_dict.get("name")}%'"

    limit_start = int(frappe.form_dict.get("limit_start", 0))
    limit_page_length = int(frappe.form_dict.get("limit_page_length", 20)) 
    query=f"""
        SELECT * from `tabMedical Network` MN JOIN `tabSpeciality List` SL ON SL.parent = MN.name 
        WHERE
        1 = 1
{condition}
LIMIT {limit_start}, {limit_page_length}
        """
    query_2=f"""
        SELECT count(MN.name)as cnt from `tabMedical Network` MN JOIN `tabSpeciality List` SL ON SL.parent = MN.name 
        WHERE
        1 = 1
{condition}
        """
    data_1 = frappe.db.sql(query, as_dict = 1)
    data_2 = frappe.db.sql(query_2, as_dict = 1)
    cnt = data_2[0]['cnt']if data_2 else 0
    return {
        "count":cnt,
        "data":data_1
    }
