// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Plan", {
    get_courses(frm) {
        get_employee_details(frm)
        estimated_cost(frm)
    },
    get_training_requests(frm) {
        get_requests(frm)
    },
    validate(frm) {
        estimated_cost(frm)

    },
    on_update(frm) {
        estimated_cost(frm)
    },
    refresh(frm) {
        frm.add_custom_button(__('Update Cost'), function () {
            get_training_actual_cost(frm)
            estimated_cost(frm)
        });

        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Course Schedule'), function () {
                if (frm.doc.table_tqgd.length > frm.doc.training_course_schedule.length) {
                    // Using Promise.all to ensure all schedules are created before refreshing the field and saving
                    let schedulePromises = frm.doc.table_tqgd.map(row => {
                        return new Promise((resolve, reject) => {
                            frappe.call({
                                method: 'frappe.client.insert',
                                freeze: true,
                                freeze_message: __("Creating Schedules"),
                                args: {
                                    doc: {
                                        doctype: 'Training Course Schedule',
                                        training_course: row.training_course,
                                        training_plan: frm.doc.name
                                    }
                                },
                                callback: function (response) {
                                    if (response.message) {
                                        let schedule = frm.add_child('training_course_schedule');
                                        schedule.training_course_schedule = response.message.name;
                                        frappe.msgprint(`Training Schedule for Course ${row.training_course}: <a href="/app/training-course-schedule/${response.message.name}">${response.message.name}</a>`);
                                        resolve();
                                    }
                                },
                                error: function (error) {
                                    frappe.msgprint(__('Failed to create the document.'));
                                    reject(error);
                                }
                            });
                        });
                    });

                    // Wait for all schedule creation promises to resolve
                    Promise.all(schedulePromises)
                        .then(() => {
                            frm.refresh_field("training_course_schedule");
                            return frm.save("Update");
                        })
                        .then(() => {
                            frappe.msgprint(__('All schedules have been created successfully.'));
                        })
                        .catch((error) => {
                            console.error('Error in creating schedules:', error);
                            frappe.msgprint(__('There was an error creating some schedules.'));
                        });
                } else {
                    frappe.throw(__('All schedules have been created already.'));
                }
            }, __("Actions"));

            frm.add_custom_button(__('Request for Quotation'), function () {
                frappe.prompt([
                    {
                        label: 'Supplier',
                        fieldname: 'supplier',
                        fieldtype: 'Link',
                        options: 'Supplier',
                    },
                    {
                        label: 'Date',
                        fieldname: 'date',
                        fieldtype: 'Date',
                        default: 'Today'
                    },
                ], (values) => {
                    if (!frm.doc.table_tqgd || frm.doc.table_tqgd.length === 0) {
                        frappe.msgprint({
                            title: __('Missing Data'),
                            indicator: 'orange',
                            message: __('Please add rows to the Training Courses table before creating an RFQ.')
                        });
                        return;
                    }

                    // Create a new Request for Quotation document
                    let rq = frappe.model.get_new_doc("Request for Quotation");

                    if (!rq) {
                        frappe.msgprint({
                            title: __('Error'),
                            indicator: 'red',
                            message: __('Unable to create a new Request for Quotation.')
                        });
                        return;
                    }

                    // Populate the items table
                    rq.items = [];
                    rq.suppliers = [{ supplier: values.supplier }];
                    rq.custom_training_plan = frm.doc.name;
                    let invalid_rows = []; // Track rows with invalid data

                    frm.doc.table_tqgd.forEach(row => {
                        // Check if each row has valid data for training_course and number_of_courses
                        if (!row.training_course || !row.number_of_courses) {
                            invalid_rows.push(row);
                        } else {
                            // Push valid row data to the items array
                            rq.items.push({
                                item_code: row.training_course,
                                qty: row.number_of_courses,
                                uom: "Nos", // Ensure 'Nos' is a valid UOM in your system
                                stock_uom: "Nos",
                                conversion_factor: 1,
                                schedule_date: frm.doc.from_date
                            });
                            rq.transaction_date = values.date;
                            rq.message_for_supplier = "Please supply the specified items at the best possible rates"
                        }
                    });

                    // If there are invalid rows, show a message
                    if (invalid_rows.length > 0) {
                        frappe.msgprint({
                            title: __('Invalid Data'),
                            indicator: 'red',
                            message: __('The following rows have missing data: ' + invalid_rows.map(row => row.training_course).join(', '))
                        });
                        return;
                    }

                    console.log("Items Array:", rq.items); // Log the populated items array for debugging

                    // Check if the items array is populated
                    if (!rq.items || rq.items.length === 0) {
                        frappe.msgprint({
                            title: __('Error'),
                            indicator: 'red',
                            message: __('No valid items found for the RFQ.')
                        });
                        return;
                    }

                    // Use frappe.client.insert to insert the new RFQ document
                    frappe.call({
                        method: 'frappe.client.insert',
                        args: {
                            doc: rq
                        },
                        callback: function (response) {
                            if (response.message) {
                                let new_rfq_name = response.message.name;
                                // Route to the new document for review
                                frappe.set_route("Form", "Request for Quotation", new_rfq_name);
                            } else {
                                frappe.msgprint({
                                    title: __('Error'),
                                    indicator: 'red',
                                    message: __('Failed to create the Request for Quotation.')
                                });
                            }
                        }
                    });
                });
            }, __("Actions"));











        }
    }

});


frappe.ui.form.on("Training Plan Table", {
    table_tqgd_add(frm, cdn, cdt) {
        estimated_cost(frm, cdt, cdn)
    },
    table_tqgd_remove(frm, cdn, cdt) {
        estimated_cost(frm, cdt, cdn)
    },
});


frappe.ui.form.on("Training Plan Table", "estimated_cost_per_course", function (frm, cdt, cdn) {
    estimated_cost(frm, cdt, cdn)
});
frappe.ui.form.on("Training Plan Table", "actual_cost_per_course", function (frm, cdt, cdn) {
    estimated_cost(frm, cdt, cdn)
});


function get_employee_details(frm) {
    frappe.call({
        doc: frm.doc,
        method: 'get_employees',
        freeze: true,
        freeze_message: __("Getting Courses"),
        callback: function (r) {
            if (!r.exc) {
                console.log(r.message)
                frm.set_value("table_tqgd", [])
                r.message.forEach(row => {
                    let child = frm.add_child("table_tqgd");
                    child.training_course = row.training_course
                    child.number_of_courses = row.count
                })
                frm.refresh_field("table_tqgd")

            }
        }
    });
    frm.save();

}

function get_training_actual_cost(frm) {
    frappe.call({
        doc: frm.doc,
        method: 'get_training_actual_cost',
        freeze: true,
        freeze_message: __("Getting Courses Costing"),
        callback: function (r) {
            console.log(r.message)
            if (!r.exc) {
                if (r.message) {
                    console.log(r.message)
                    let updated = false;
                    r.message.forEach(row => {
                        frm.doc.table_tqgd.forEach(row2 => {
                            if (row.training_course == row2.training_course) {
                                row2.actual_cost_per_course = row.total_actual_cost;
                                row2.estimated_cost_per_course = row.total_estimated_cost
                                updated = true;
                            }
                        });
                    });
                    frm.refresh_field("table_tqgd");
                    frm.save("Update")
                    if (updated) {
                        frappe.msgprint(__("Courses costing updated successfully."));
                    } else {
                        frappe.msgprint(__("No matching courses found to update."));
                    }
                } else {
                    frappe.msgprint(__("No data returned from the server."));
                }
            } else {
                frappe.msgprint(__("An error occurred while fetching data."));
            }
        }
    });
}


function get_requests(frm) {
    frappe.call({
        doc: frm.doc,
        method: 'get_training_requests',
        freeze: true,
        freeze_message: __("Getting Requests"),
        callback: function (res) {
            if (!res.exc) {
                console.log(res.message)
                frm.set_value("table_oyzi", [])
                res.message.forEach(row => {
                    let child = frm.add_child("table_oyzi");
                    child.training_request = row.training_request
                    child.employee = row.employee
                    child.designation = row.designation
                    child.training_course = row.training_course
                })
                frm.refresh_field("table_oyzi")

            }
        }
    });
}

function estimated_cost(frm, cdt, cdn) {
    let totalEstimated = frm.doc.table_tqgd.reduce(function (sum, item) {
        return sum + (item.estimated_cost_per_course || 0);
    }, 0);
    let totalActual = frm.doc.table_tqgd.reduce(function (sum, item) {
        return sum + (item.actual_cost_per_course || 0);
    }, 0);
    frm.set_value("total_estimated_cost", totalEstimated)
    frm.set_value("total_actual_cost", totalActual)
    frm.save("Update")
    frm.refresh_field("total_estimated_cost")
}

