frappe.ui.form.on('Salary Component', {
    refresh: function (frm) {
        if (!frm.doc.__islocal && frm.doc.amount_based_on_formula) {
            frm.add_custom_button(__('Open Formula Builder'), function () {
                open_formula_builder_dialog(frm);
            });
        }
    }
});

function open_formula_builder_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: __('Formula Builder'),
        fields: [
            {
                label: 'Field',
                fieldname: 'field',
                fieldtype: 'Link',
                options: "Formula",
                reqd: 1
            },
            {
                label: 'Operation',
                fieldname: 'operation',
                fieldtype: 'Select',
                options: ['+', '-', '*', '/'],
                reqd: 1
            },
            {
                label: 'Value Type',
                fieldname: 'value_type',
                fieldtype: 'Select',
                options: ['Number', 'Formula Doctype'],
                default: 'Number',
                reqd: 1
            },
            {
                label: 'Value (Manual)',
                fieldname: 'value_manual',
                fieldtype: 'Data',
                depends_on: 'eval:doc.value_type == "Number"'
            },
            {
                label: 'Value (Formula Doctype)',
                fieldname: 'value_formula',
                fieldtype: 'Link',
                options: 'Formula', // Replace 'Formula' with the actual linked Doctype name
                depends_on: 'eval:doc.value_type == "Formula Doctype"'
            },
            {
                label: 'Add Condition?',
                fieldname: 'add_condition',
                fieldtype: 'Check'
            },
            {
                label: 'Condition Field',
                fieldname: 'condition_field',
                fieldtype: 'Link',
                options: "Formula",
                depends_on: 'eval:doc.add_condition==1'
            },
            {
                label: 'Condition Operator',
                fieldname: 'condition_operator',
                fieldtype: 'Select',
                options: ['>', '<', '>=', '<=', '=='],
                depends_on: 'eval:doc.add_condition==1'
            },
            {
                label: 'Condition Value Type',
                fieldname: 'condition_value_type',
                fieldtype: 'Select',
                options: ['Number', 'Formula Doctype'],
                depends_on: 'eval:doc.add_condition==1'
            },
            {
                label: 'Condition Value (Manual)',
                fieldname: 'condition_value_manual',
                fieldtype: 'Data',
                depends_on: 'eval:doc.add_condition==1 && doc.condition_value_type == "Number"'
            },
            {
                label: 'Condition Value (Formula Doctype)',
                fieldname: 'condition_value_formula',
                fieldtype: 'Link',
                options: 'Formula', // Replace 'Formula' with the actual linked Doctype name
                depends_on: 'eval:doc.add_condition==1 && doc.condition_value_type == "Formula Doctype"'
            }
        ],
        primary_action_label: 'Generate Formula',
        primary_action(values) {
            const formula = generate_formula(values);
            if (formula) {
                frm.set_value('formula', formula);
                frm.scroll_to_field("formula")
                frappe.msgprint(__("Formula Generated! don't forget to save the document."));
                dialog.hide();
            }
        }
    });

    dialog.show();
}

function generate_formula(values) {
    try {
        // Handle main value
        const value = values.value_type === 'Number' ? values.value_manual : `frappe.db.get_value("Formula", "${values.value_formula}", "field_name")`;

        // Handle condition value
        const condition_value = values.condition_value_type === 'Number'
            ? values.condition_value_manual
            : `frappe.db.get_value("Formula", "${values.condition_value_formula}", "field_name")`;

        let formula = `${values.field} ${values.operation} ${value}`;

        // Add condition if specified
        if (values.add_condition) {
            const condition = `${values.condition_field} ${values.condition_operator} ${condition_value}`;
            formula = `${formula} if ${condition} else 0`;
        }

        return formula;
    } catch (error) {
        frappe.msgprint(__('Error generating formula. Please check your inputs.'));
        return null;
    }
}


