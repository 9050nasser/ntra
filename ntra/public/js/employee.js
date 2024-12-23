frappe.ui.form.on("Employee", {

    gender: function (frm) {
        if (frm.is_new()) { // Ensure this only runs for new documents
            // Check if the child table is empty
            if (!frm.doc.items || frm.doc.items.length === 0) {
                frappe.call({
                    method: 'ntra.events.get_employee_identification_type',
                    callback: function (response) {
                        if (response.message) {
                            frm.doc.custom_employee_identification = []
                            response.message.identefication.forEach(row => {
                                if(frm.doc.gender == row.gender ||row.gender  == "" )
                                {
                                    const child = frm.add_child('custom_employee_identification');
                                frappe.model.set_value(child.doctype, child.name, 'document', row.document_type);
                            }
                            });
                            frm.refresh_field('custom_employee_identification');
                        }
                    }
                });
            }
        }
    },
    refresh: function(frm) {
        frm.set_query("salutation", function() {
            return {
                filters: [
                    ["gender", "in", [frm.doc.gender, "Any Gender"]]
                ]
            };
        });
        frm.fields_dict['custom_malitary_status'].$input.on('click', function() {

            // Alternatively, open a custom dialog
            let d = new frappe.ui.Dialog({
                title: 'Enter details',
                fields: [
                    {
                        label: 'Malitary Status',
                        fieldname: 'malitary_status',
                        fieldtype: 'Select',
                        options: [
                            "Exempt",
                            "Completed",
                            "Not Requested",
                            "Not Applicable",
                            "Over 30 Years Old",
                            "Defferd",
                            "T-Exempt",
                            "Other"
                        ],
                        onchange: function(e) {
                            
                            if (this.value == "Other")
                                d.fields_dict['other'].df.hidden = 0
                            else
                               { 
                                d.fields_dict['other'].df.hidden = 1
                                d.fields_dict['other'].value = null
                            }
                            d.fields_dict['other'].refresh()

                        }
                    },
                    {
                        
                        fieldname: 'column_break',
                        fieldtype: 'Column Break',
                    },
                    {
                        label: 'Other',

                        fieldname: 'other',
                        fieldtype: 'Data',
                        hidden: 1
                    },
    
                ],
                size: 'small', // small, large, extra-large 
                primary_action_label: 'Set',
                primary_action(values) {
                    frm.set_value('custom_malitary_status',values.other || values.malitary_status )
                    d.hide();
                }
            });

            d.show();
        });
    },
    date_of_joining: function(frm){
        if(frm.doc.custom_retirement_age && frm.doc.date_of_birth)
        {
            let date_of_joining = frm.doc.date_of_birth;
            // Using moment.js to add years
            let new_date = moment(date_of_joining).add(frm.doc.custom_retirement_age, 'years').format('YYYY-MM-DD');
            frm.set_value('date_of_retirement', new_date);
        }
    },
    custom_retirement_age: function(frm){
        if(frm.doc.date_of_joining  && frm.doc.date_of_birth)
        {
            let date_of_joining = frm.doc.date_of_birth;
            // Using moment.js to add years
            let new_date = moment(date_of_joining).add(frm.doc.custom_retirement_age, 'years').format('YYYY-MM-DD');
            frm.set_value('date_of_retirement', new_date);
        }
    }
});