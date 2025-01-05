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
                                if (frm.doc.gender == row.gender || row.gender == "") {
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
    refresh: function (frm) {
        frm.add_custom_button("View Effective Dates", function () {
            frappe.call({
                method: "ntra.effective_dates.get_version_history",
                args: {
                    employee_name: frm.doc.name
                },
                callback: function (r) {
                    if (r.message) {
                        let versions = r.message;
                        let message = "<table class='table table-bordered'>";
                        message += "<tr><th>Version</th><th>From</th><th>To</th></tr>";
                        versions.forEach(version => {
                            message += `<tr>
                                <td>${version.custom_version_number}</td>
                                <td>${version.custom_from_effective_date}</td>
                                <td>${version.custom_to_effective_date || "Present"}</td>
                            </tr>`;
                        });
                        message += "</table>";
                        frappe.msgprint(message, "Version History");
                    }
                }
            });
        });
        frm.set_query("salutation", function () {
            return {
                filters: [
                    ["gender", "in", [frm.doc.gender, "Any Gender"]]
                ]
            };
        });
        frm.fields_dict['custom_malitary_status'].$input.on('click', function () {

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
                        onchange: function (e) {

                            if (this.value == "Other")
                                d.fields_dict['other'].df.hidden = 0
                            else {
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
                    frm.set_value('custom_malitary_status', values.other || values.malitary_status)
                    d.hide();
                }
            });

            d.show();
        });
    },
    date_of_joining: function (frm) {
        if (frm.doc.custom_retirement_age && frm.doc.date_of_birth) {
            let date_of_joining = frm.doc.date_of_birth;
            // Using moment.js to add years
            let new_date = moment(date_of_joining).add(frm.doc.custom_retirement_age, 'years').format('YYYY-MM-DD');
            frm.set_value('date_of_retirement', new_date);
        }
    },
    custom_retirement_age: function (frm) {
        if (frm.doc.date_of_joining && frm.doc.date_of_birth) {
            let date_of_joining = frm.doc.date_of_birth;
            // Using moment.js to add years
            let new_date = moment(date_of_joining).add(frm.doc.custom_retirement_age, 'years').format('YYYY-MM-DD');
            frm.set_value('date_of_retirement', new_date);
        }
    },
    custom_national_id: function(frm){
        if(frm.doc.custom_national_id.length === 14){
            let id = frm.doc.custom_national_id;
            let year = id.slice(1,3),
            month = id.slice(3,5),
            day = id.slice(5,7),
            state_code = id.slice(7,9),
            gender = (Number(id.slice(12,13))%2 == 0)?"Female":"Male";
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "State",
                    filters: { code: state_code }, // Replace 'CA' with your state code
                    fieldname: "name"
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value({
                            custom_state: r.message.name,
                            custom_place_of_birth_governorate:r.message.name
                        });
                    }
                }
            });
            frm.set_value({
                date_of_birth: `${17+ Number(id.slice(0, 1))}${year}-${month}-${day}`,
                gender,
                custom_state_code: state_code
            })
        }
    }  
});