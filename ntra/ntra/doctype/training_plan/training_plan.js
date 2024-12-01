// Copyright (c) 2024, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Training Plan", {
	get_training_requests(frm) {
        get_employee_details(frm)
        get_requests(frm)
        estimated_cost(frm)
        frm.save()
	},
    validate(frm) {
        estimated_cost(frm)
    
    },
    refresh(frm) {
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(__('Course Schedule'), function() {
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
                                    from_date: frm.doc.from,
                                    to_date: frm.doc.to_date,
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


frappe.ui.form.on("Training Plan Table", "estimated_cost_per_course", function(frm, cdt, cdn) {
	estimated_cost(frm, cdt, cdn)
});
frappe.ui.form.on("Training Plan Table", "actual_cost_per_course", function(frm, cdt, cdn) {
	estimated_cost(frm, cdt, cdn)
});


function get_employee_details (frm) {
    frappe.call({
        doc: frm.doc,
        method: 'get_employees',
        freeze: true,
        freeze_message: __("Getting Courses"),
        callback: function(r) {
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
       
}

function get_requests (frm) {
    frappe.call({
        doc: frm.doc,
        method: 'get_training_requests',
        freeze: true,
        freeze_message: __("Getting Requests"),
        callback: function(res) {
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
    frm.refresh_field("total_estimated_cost")
}

