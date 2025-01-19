// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contract Renewal", {
	on_submit: function(frm) {
        frm.call({
            method:"create_new_contract",
            args:{
                status: frm.doc.status,
                employee_contract: frm.doc.employee_contract
            },
            callback: function(r){
                if (r.message){
                    frappe.set_route('Form', "Contracts", r.message);
                }
            }
        })
    }
});
