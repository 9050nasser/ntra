# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class OvertimeConsolidationTool(Document):
	def on_submit(self):
		frappe.enqueue('ntra.ntra.doctype.overtime_consolidation_tool.overtime_consolidation_tool.make_consolidated_overtimes', doc=self)


def make_consolidated_overtimes(doc):
	attendance_rule = "_"
	for employee in frappe.db.get_list("Employee", [["status", "=", "Active"]], ["name", "custom_attendance_rule as attendance_rule", "holiday_list"], order_by="attendance_rule ASC"):
		if not employee.attendance_rule:
			continue
		if employee.attendance_rule != attendance_rule:
			attendance_rule = employee.attendance_rule
			(
				enable_overtime_based_on_target_hours,
				minimum_hours_calculated_per_month,
				maximum_hours_calculated_per_month,
				maximum_amount_per_currency,
				target_working_hours_per_month
			) = frappe.db.get_value("Attendance Rule", attendance_rule, [
				"enable_overtime_based_on_target_hours",
				"minimum_hours_calculated_per_month",
				"maximum_hours_calculated_per_month",
				"maximum_amount_per_currency",
				"target_working_hours_per_month"
			])
		if enable_overtime_based_on_target_hours:

			overtimes = frappe.db.get_list("Overtime Request", [["docstatus", "=", 0],["date", "between", [doc.from_date, doc.to_date]]], ["name as overtime_request", "overtime_type", "total_overtime_hours as overtime_hours", "calculated_overtime_amount as overtime_amount"])
			d = frappe.get_doc(dict(
				doctype = "Consolidated Overtime",
				employee = employee.name, 
				date = doc.payroll_date,
				overtime_requests = overtimes,
				hour_average_amount = sum(item.overtime_amount for item in overtimes) / sum(item.overtime_hours for item in overtimes),
				overtime_hours = 0,
				
			))

			attendance_records = frappe.db.get_list("Attendance", [["docstatus", "=", 1], ["employee", "=", employee.name], ["attendance_date", "between", [doc.from_date, doc.to_date]], ["status", "!=", "Absent"], ["in_time", "is", "set"], ["out_time", "is", "set"]], ["in_time", "out_time"])
			total_hours = sum((a.out_time - a.in_time).total_seconds()/3600 for a in attendance_records)
			if target_working_hours_per_month:
				if total_hours - target_working_hours_per_month > 0:
					d.overtime_hours = total_hours - target_working_hours_per_month
			else:
				target_hours = get_target_overtime_on_period(employee.name, employee.holiday_list, doc.from_date, doc.to_date)
				d.overtime_hours = total_hours - target_hours
			if d.overtime_hours >= minimum_hours_calculated_per_month:
				if d.overtime_hours > maximum_hours_calculated_per_month:
					d.overtime_hours = maximum_hours_calculated_per_month
				d.amount = d.overtime_hours * d.hour_average_amount
				if d.amount > maximum_amount_per_currency:
					d.amount = maximum_amount_per_currency
				d.insert()
				for overtime in overtimes:
					frappe.get_doc("Overtime Request", overtime.overtime_request).submit()

def get_target_overtime_on_period(employee, holiday_list, from_date, to_date):
	holiday_count = frappe.db.count(
		"Holiday",
		filters={
			"parent": holiday_list,
			"holiday_date": ["between", [from_date, to_date]]
		}
	)
	shift = frappe.db.get_list(
		"Shift Assignment",
		[
			["employee", "=", employee],
			["start_date", "<=", from_date],
			["status", "=", "Active"],
		],
		"shift_type as name",
		or_filters=[["end_date", ">=", to_date], ["end_date", "is", "not set"]],
		order_by="creation DESC"
	)[0]
	shift_working_hours = frappe.db.get_value("Shift Type", shift.name, "custom_daily_working_hour")
	target_hours = (date_diff(to_date, from_date) - holiday_count) * shift_working_hours
	return target_hours
	