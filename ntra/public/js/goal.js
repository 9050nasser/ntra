frappe.ui.form.on("Goal", {
	refresh(frm) {        
        if(frappe.user_roles.includes("Objective") && frm.doc.employee){
            frm.add_custom_button('Review', () => {
                let dialog = new frappe.ui.Dialog({
                    title: 'Custom Dialog',
                    fields: [
                        {
                            label: 'Goal Name',
                            fieldname: 'goal_name',
                            fieldtype: 'Data',
                            reqd: 1
                        },
                        {
                            label: 'Description',
                            fieldname: 'description',
                            fieldtype: 'Text',
                            reqd: 1
                        },
                        {
                            label: 'Reason',
                            fieldname: 'reason',
                            fieldtype: 'Select',
                            options: [
                                "Not intelligent",
                                "Unqualified",
                                "Not aligned with the main objective" 
                            ],
                            reqd: 1
                        },
                    ],
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        // Perform an action with the dialog input
                        frappe.call({
                            method: "ntra.event.objective.create_edit_task",
                            args: {
                                goal_name: values.goal_name,
                                description: values.description,
                                employee: frm.doc.employee,
                                objective: frm.doc.name,
                                reason : values.reason
                            },
                            callback: function(r){
                                if(r.message){
                                    frappe.msgprint(__("New Task is created for this objective"))
                                }
                            }
                        })
                        dialog.hide();
                    }
                });
                dialog.show()
            }, 'Process Approval').css({color: 'red'});
        }

        

        let result = (frm.doc.custom_weight_progress * frm.doc.custom_weight) /100
        if(frm.doc.custom_weight_progress_result!= result){
            frm.set_value("custom_weight_progress_result", result)
            frm.save();
        }
	},
    custom_weight_progress(frm) {
        update(frm)
        frm.save();
    },
    validate (frm) {
        update(frm)
    }
});

function update(frm) {
    let result = (frm.doc.custom_weight_progress * frm.doc.custom_weight) /100
    frm.set_value("custom_weight_progress_result", result)
}

