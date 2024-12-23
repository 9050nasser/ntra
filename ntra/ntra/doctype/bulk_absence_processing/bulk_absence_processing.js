// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Absence Processing", {
	refresh(frm) {
        frm.disable_save();
        frm.add_custom_button('Process Absence', () => console.log('Clicked custom button'))
	},
        employee:function(frm){
                if(!frm.doc.from_date || !frm.doc.to_date)
                        frappe.throw(__("Please Select From and To Date"))
        }

});
