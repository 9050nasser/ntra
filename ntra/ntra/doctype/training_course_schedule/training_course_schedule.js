// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Course Schedule", {
	refresh(frm) {
        frm.add_custom_button(__('Course Assignment'), function() {
            frappe.call({
                method: 'ntra.api.create_bulk_assignment',
                args: {
                    'training_course_schedule': frm.doc.name,
                    'training_plan': frm.doc.training_plan
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.show_alert(__('Course Assignments Created Successfully'), 5);
                    } else {
                        frappe.throw(__("Error"))
                    }
                }
               });
               
        }, __("Create"));
	},
});
