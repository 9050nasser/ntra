frappe.ui.form.on("Task", {
	refresh(frm) {   
        if(frm.doc.custom_is_edit && frm.doc.status != "Completed"){
            frm.add_custom_button('Edit Objective', () => {
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
                        }
                    ],
                    primary_action_label: 'Submit',
                    primary_action(values) {
                        // Perform an action with the dialog input
                        frappe.call({
                            method: "ntra.event.objective.edit_objective",
                            args: {
                                goal_name: values.goal_name,
                                description: values.description,
                                objective: frm.doc.custom_objective
                            },
                            callback: function(r){
                                if(r.message){
                                    frappe.msgprint(__("Objective is edited Successfully"))
                                    frappe.call({
                                        method: "ntra.event.task.update_complete",
                                        args: {
                                            objective: frm.doc.name
                                        },
                                        callback: function(r){
                                            if(r.message){
                                                frm.refresh()
                                            }
                                        }
                                    })
                                }
                            }
                        })
                        dialog.hide();
                    }
                });
                dialog.show()
            }).css({color: 'red'});
        }
    }
})