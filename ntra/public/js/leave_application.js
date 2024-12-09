// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Application", {
	custom_maternity_leave(frm) {
			
			frm.set_query("employee", function(){
				return {
					"filters": [
						["Employee", "gender", "=", "Female"],
						["Employee", "status", "=", "Active"]
					]
				}
			});
			frm.set_query("leave_type", function(){
				return {
					"filters": [
						["Leave Type", "custom_maternity_leave", "=", 1]
					]
				}
			});
		
	},
	after_save(frm) {
		if (frm.doc.custom_maternity_leave) {
			frappe.call({
				method: 'ntra.events.get_leave_balance',
				args: {
					'leave_type_name': frm.doc.leave_type,
					'employee': frm.doc.employee
				},
				callback: function(r) {
					if (!r.exc) {
						frm.set_intro(`Remaining Balance is : ${r.message}`, 'blue')
					}
				}
			});
			   
		}
	}
});