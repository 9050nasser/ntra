// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Onboarding", {
	refresh(frm) {
        frm.set_query("user", "activities", function (doc, cdt, cdn) {
            let row = locals[cdt][cdn];
            console.log(row.department)
            return {
                filters: {
                    department: row.department
                }
            };
        });
	},
    onload_post_render(frm){
        if (!frm.doc.employee && frm.doc.docstatus === 1) {
            frm.remove_custom_button("Employee", "Create")
			frm.add_custom_button(
				__("Employee"),
				function () {
					frappe.model.open_mapped_doc({
						method: "ntra.event.employee_onboarding.make_employee",
						frm: frm,
					});
				},
				__("Create"),
			);
            frm.page.set_inner_btn_group_as_primary(__("Create"));
		}
    }
});