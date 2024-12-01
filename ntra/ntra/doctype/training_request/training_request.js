// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Request", {
	refresh(frm) {
        if (frm.doc.employee){
            frm.trigger("make_dashboard")
        }
	},
    make_dashboard: function (frm) {
        let map;
        let course;

        frappe.call({
            doc: frm.doc,
            method: "employee_skills",
            async: false,
            args: {
                "employee": frm.doc.employee
            },
            callback: function (r) {
                if (!r.exc) {
                    map = r.message["skills"];
                    course = r.message["courses"]
                }
            },
        });

        $("div").remove(".form-dashboard-section.custom");

        frm.dashboard.add_section(
            frappe.render_template("training_request_dashboard", {
                data: map,
            }),
            __("Employee Skills"),
        );
        frm.dashboard.show();
        frm.dashboard.add_section(
            frappe.render_template("training_request_dashboard_course", {
                data: course,
            }),
            __("Employee Courses"),
        );
        frm.dashboard.show();

    },
    employee (frm) {
        frm.trigger("make_dashboard")
    }
});
