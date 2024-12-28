frappe.ui.form.on("Appraisal", {
    employee(frm){
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Task',
                filters: [["status", "!=", "Completed"], ["custom_ad_hoc_task", "=", 1], ["custom_employee", "=", frm.doc.employee]],         // Apply the filters
                fields: ['name as task'],
                limit_page_length: 0
            },
            callback: function(response) {
                if (response.message) {
                    frm.set_value("custom_ad_hoc_task", response.message)
                }
            }
        });
    }
})