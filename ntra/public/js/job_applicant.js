// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Applicant", {
	refresh(frm) {
        frm.add_custom_button(__("Security Clearance"), function() {
    
                    // frappe.call({
                    //     method: 'frappe.client.insert',
                    //     args: {
                    //         doc: {
                    //             doctype: 'Security Clearance',
                    //             applicant_name: frm.doc.applicant_name,
                    //             email_address: frm.doc.email_id,
                    //             phone_number: frm.doc.phone_number,
                    //             designation: frm.doc.designation
                    //         },
                    //     },
                    //     callback: function (r) {
                    //         // Route to the newly created Work Order
                    //         frappe.set_route("Form", "Security Clearance", r.message.name);
                    //     }
                    // },__("Create"));
                    let new_doc = frappe.model.get_new_doc("Security Clearance")
                    new_doc.clearance_for = "New Hiring"
                    new_doc.applicant_name = frm.doc.applicant_name
                    new_doc.email_address = frm.doc.email_id
                    new_doc.phone_number = frm.doc.phone_number
                    new_doc.designation = frm.doc.designation
                    new_doc.job_applicant = frm.doc.name
                    frappe.set_route("Form", "Security Clearance", new_doc.name);
    
        },__("Create"));
	},
});