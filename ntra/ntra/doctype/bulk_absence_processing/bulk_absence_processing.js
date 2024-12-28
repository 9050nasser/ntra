// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Absence Processing", {
	refresh(frm) {
        frm.disable_save();
        frm.add_custom_button('Process Absence', () => {
			frm.call({
				method: "process_absences",
				doc: frm.doc,
			})
		})
	},
        get_employees(frm) {
		if (!frm.doc.from_date || !frm.doc.to_date) return  frappe.throw(__("Please Select From and To Date"))
		frm.call({
			method: "get_employees",
			args: {
				advanced_filters: frm.advanced_filters || [],
			},
			doc: frm.doc,
		}).then((r) => {
                        console.log(r.message)
                        refresh_field('employee_table')
                });
	},
        from_date(frm) {
		// frm.trigger("get_employees");
	},
        to_date(frm) {
		frm.trigger("get_employees");
	},

	async company(frm) {
		frm.trigger("get_employees");
	},

	branch(frm) {
		frm.trigger("get_employees");
	},

	department(frm) {
		frm.trigger("get_employees");
	},

	employment_type(frm) {
		frm.trigger("get_employees");
	},

	designation(frm) {
		frm.trigger("get_employees");
	},

	employee_grade(frm) {
		frm.trigger("get_employees");
	},

});
