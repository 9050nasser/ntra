// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Course Attendance Tool', {
	setup: (frm) => {
		frm.students_area = $('<div>')
			.appendTo(frm.fields_dict.trainees_html.wrapper);
	},
	refresh: function(frm) {
		frm.disable_save();
	},

	student_group: function(frm) {
		if (frm.doc.date) {
			let args = {
				date: frm.doc.date,
				...(frm.doc.session && { session: frm.doc.session }),
				...(frm.doc.training_course && { training_course: frm.doc.training_course }),
				...(frm.doc.employee && { employee: frm.doc.employee }),
			};
			frm.students_area.find('.student-attendance-checks').html(`<div style='padding: 2rem 0'>Fetching...</div>`);
			var method = "ntra.ntra.doctype.course_attendance_tool.course_attendance_tool.get_student_attendance_records";
			frappe.call({
				method: method,
				args,
				callback: function(r) {
					frm.events.get_students(frm, r.message);
				}
			})
		}
	},

	date: function(frm) {
		if (frm.doc.date > frappe.datetime.get_today())
			frappe.throw(__("Cannot mark attendance for future dates."));
		frm.trigger("student_group");
	},

	training_course: function(frm) {
		frm.trigger("student_group");
	},
	session: function(frm) {
		frm.trigger("student_group");
	},
	employee: function(frm) {
		frm.trigger("student_group");
	},
	get_students: function(frm, students) {
		students = students || [];
		frm.students_editor = new StudentsEditor(frm, frm.students_area, students);
	}
});


class StudentsEditor {
	constructor(frm, wrapper, students) {
		this.wrapper = wrapper;
		this.frm = frm;
		if(students.length > 0) {
			this.make(frm, students);
		} else {
			this.show_empty_state();
		}
	}
	make(frm, students) {
		var me = this;

		$(this.wrapper).empty();
		var student_toolbar = $('<p>\
			<button class="btn btn-default btn-add btn-xs" style="margin-right: 5px;"></button>\
			<button class="btn btn-xs btn-default btn-remove" style="margin-right: 5px;"></button>\
			<button class="btn btn-default btn-primary btn-mark-att btn-xs"></button></p>').appendTo($(this.wrapper));

		student_toolbar.find(".btn-add")
			.html(__('Check all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if (!$(check).prop("disabled")) {
						check.checked = true;
					}
				});
			});

		student_toolbar.find(".btn-remove")
			.html(__('Uncheck all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if (!$(check).prop("disabled")) {
						check.checked = false;
					}
				});
			});

		student_toolbar.find(".btn-mark-att")
			.html(__('Mark Attendance'))
			.removeClass("btn-default")
			.on("click", function() {
				$(me.wrapper.find(".btn-mark-att")).attr("disabled", true);
				var studs = [];
				$(me.wrapper.find('input[type="checkbox"]')).each(function(i, check) {
					var $check = $(check);
					studs.push({
						student: $check.data().student,
						student_name: $check.data().studentName,
						disabled: $check.prop("disabled"),
						checked: $check.is(":checked"),
						name: $check.data().studentAssignment
					});
				});


				var students_present = studs.filter(function(stud) {
					return !stud.disabled && stud.checked;
				});

				var students_absent = studs.filter(function(stud) {
					return !stud.disabled && !stud.checked;
				});

				frappe.confirm(__("Do you want to update attendance? <br> Present: {0} <br> Absent: {1}",
					[students_present.length, students_absent.length]),
					function() {	//ifyes
						if(!frappe.request.ajax_count) {
							frappe.call({
								method: "ntra.ntra.doctype.course_attendance_tool.course_attendance_tool.mark_student_present_or_absent",
								freeze: true,
								freeze_message: __("Marking attendance"),
								args: {
									session_names: studs.map((stud=>{return {name: stud.name, checked: stud.checked}}))
								},
								callback: function(r) {
									$(me.wrapper.find(".btn-mark-att")).attr("disabled", false);
									frm.trigger("student_group");
								}
							});
						}
					},
					function() {	//ifno
						$(me.wrapper.find(".btn-mark-att")).attr("disabled", false);
					}
				);
			});

		// make html grid of students
		let student_html = '';
		for (let student of students) {
			let session = (!frm.doc.session)?`(Session:${student.session})`:"";
			let course = (!frm.doc.training_course)?`(Course: ${student.course})`:"";
			student_html += `<div class="col-sm-5">
					<div class="checkbox">
						<label>
							<input
								type="checkbox"
								data-student="${student.name}"
								data-student-name="${student.employee_name}"
								data-student-assignment="${student.parent}"
								class="students-check"
								${student.status==='Present' ? 'checked' : ''}>
							${student.employee_name} ${course} ${session}
						</label>
					</div>
				</div>`;
		}

		$(`<div class='student-attendance-checks'>${student_html}</div>`).appendTo(me.wrapper);
	}

	show_empty_state() {
		$(this.wrapper).html(
			`<div class="text-center text-muted" style="line-height: 100px;">
				${__("No Students in")} ${this.frm.doc.student_group}
			</div>`
		);
	}
};
