// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on('Course Assignment', {
    refresh(frm) {
        frm.add_custom_button(__('Expense Claim'), function () {
            frappe.call({
                method: "expense_claim", // Replace with actual method path
                doc: frm.doc,
                freeze: true,
                freeze_message: __("Creating Expense Claim..."),
                callback: function (r) {
                    if (r.message) {
                        // Handle specific error messages from the server
                        if (r.message === "No course costing found for this course") {
                            frappe.msgprint(__("No course costing found for this course."));
                        } else if (r.message === "Claims not included in course costing") {
                            frappe.msgprint(__("Claims are not included in the course costing."));
                        } else {
                            // If the message is valid (not an error), navigate to the new document
                            frappe.set_route("Form", "Expense Claim", r.message);
                        }
                    } else {
                        // Handle unexpected responses (e.g., if there's no message)
                        frappe.msgprint(__("Unexpected error occurred while creating Expense Claim."));
                    }
                },
                error: function (err) {
                    // Catch any unexpected errors that occur during the API call
                    frappe.msgprint(__("An error occurred: ") + err.message);
                }
            });
        });
    }
});

