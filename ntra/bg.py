import frappe


@frappe.whitelist()
def trigger_employee_checkin_validate():
    batch_size = 1000  # Number of records to process at a time
    offset = 0
    total_updated = 0
    while True:
        employee_checkin = frappe.db.get_all("Employee Checkin", filters={"shift": ["is", "not set"]}, fields=["name", "employee"], limit=batch_size, start=offset)
        for checkin in employee_checkin:
            if frappe.db.get_value("Employee", checkin.employee, "status") != "Active":
                continue
            doc = frappe.get_doc("Employee Checkin", checkin.name)
            # generate random string
            doc.device_id = frappe.generate_hash(length=8)
            doc.save()
            frappe.db.commit()
            print(f"Employee Checkin Validated: {doc.name}")
        return "Employee Checkin Validated"


@frappe.whitelist()
def checkin_validate():
    batch_size = 1000  # Number of records to process at a time
    offset = 0
    total_validated = 0
    errors = []

    while True:
        # Fetch a batch of employee check-ins
        employee_checkins = frappe.db.get_all(
            "Employee Checkin",
            filters={"shift": ["is", "not set"]},
            fields=["name", "employee"],
            limit=batch_size,
            start=offset
        )

        if not employee_checkins:
            break  # Exit loop if no more records

        for checkin in employee_checkins:
            try:
                # Skip if the employee is not active
                if frappe.db.get_value("Employee", checkin.employee, "status") != "Active":
                    continue

                # Get the document and update the device_id
                doc = frappe.get_doc("Employee Checkin", checkin.name)
                doc.device_id = frappe.generate_hash(length=8)
                doc.save()

                total_validated += 1
                print(f"Employee Checkin Validated: {doc.name}")

            except Exception as e:
                # Log the error for the current record
                errors.append({
                    "checkin_name": checkin.name,
                    "error": str(e)
                })
                print(f"Error processing Employee Checkin {checkin.name}: {e}")

        # Commit after each batch
        frappe.db.commit()
        offset += batch_size
        print(f"Processed batch: {offset}, Total validated: {total_validated}")

    # Log errors if any
    if errors:
        error_log = "\n".join(
            [f"Checkin: {error['checkin_name']}, Error: {error['error']}" for error in errors]
        )
        print(f"Errors encountered during processing:\n{error_log}")

    return {
        "message": f"Employee Checkin Validated: {total_validated} records updated",
        "errors": errors
    }

