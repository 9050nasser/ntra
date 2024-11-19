// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Plan", {
	get_training_requests(frm) {
        get_employee_details(frm)
	},
});


function get_employee_details (frm) {
    frappe.call({
        doc: frm.doc,
        method: 'get_employees',
        freeze: true,
        freeze_message: __("Getting Courses"),
        callback: function(r) {
        if (!r.exc) {
            console.log(r.message)
            frm.set_value("table_tqgd", [])
            r.message.forEach(row => {
                let child = frm.add_child("table_tqgd");
                child.training_course = row.training_course
                child.number_of_courses = row.count
            })
            frm.refresh_field("table_tqgd")
            
        }
        }
       });
       
}
