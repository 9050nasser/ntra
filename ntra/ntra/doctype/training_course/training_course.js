// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Course", {
    refresh(frm) {
        frm.add_custom_button(__('Course Costing'), function () {
            frappe.new_doc('Course Costing', {
                training_course: frm.doc.course_name,
            });

        }, __("Create"));

    },

});


