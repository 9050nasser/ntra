import frappe

def update_actual_cost(doc, method):
    for row in doc.items:
        # Retrieve the item details
        item = frappe.get_doc("Item", row.item_code)
        
        if item.custom_course_item:
            # Retrieve all relevant "Course Costing" records
            costings = frappe.db.get_all(
                "Course Costing",
                filters={"training_course": row.item_code, "docstatus": 1},
                fields=["name"]
            )
            
            if costings:
                # Perform bulk updates for efficiency
                frappe.db.set_value(
                    "Course Costing",
                    [costing["name"] for costing in costings],
                    "total_actual_cost",
                    row.rate
                )
