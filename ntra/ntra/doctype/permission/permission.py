# Copyright (c) 2024, Mohammed Nasser and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	cint,
	cstr,
	format_date,
	get_datetime,
	get_link_to_form,
	getdate,
	nowdate,
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from erpnext.accounts.utils import get_fiscal_year
from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates


class DuplicatePermissionError(frappe.ValidationError):
	pass

class OverAllocationPermissionError(frappe.ValidationError):
	pass


class Permission(Document):

	def on_submit(self):
		self.validate_duplicate_record()
		self.process_permission()

	def validate(self):
		self.validate_count()

	# def on_trash(self):
	# 	self.delete_ledger()

	def before_cancel(self):
		ledgers = frappe.db.get_all("Leave Ledger Entry", filters={"transaction_type": self.doctype, "transaction_name": self.name,"docstatus": ["=", 1], "employee": self.employee}, fields=["*"])
		for ledger in ledgers:
			doc = frappe.get_doc("Leave Ledger Entry", ledger.name)
			doc.delete()
			frappe.msgprint(f"{doc.doctype} {doc.name} Deleted")
		frappe.db.commit()

	def validate_duplicate_record(self):
		duplicate = frappe.db.get_all(
			"Permission", 
			filters={"employee": self.employee, "date": self.date, "status": "Approved", "docstatus": 1, "permission_type": self.permission_type, "name": ["!=", self.name]}, 
			fields=["*"]
		)

		if duplicate:
			duplicate_links = ", ".join(
				[get_link_to_form("Permission", d.name) for d in duplicate]
			)
			frappe.throw(
				_("Permission for employee {0} is already marked for the date {1}: {2}").format(
					frappe.bold(self.employee),
					frappe.bold(format_date(self.date)),
					duplicate_links,
				),
				title=_("Duplicate Permission"),
				exc=DuplicatePermissionError,
			)

	def validate_count(self):
		month = get_start_end_dates("Monthly", self.date)
		start_month, end_month = month.start_date, month.end_date

		permissions = frappe.db.get_all(
			"Permission",
			filters={
				"employee": self.employee,
				"date": ["between", [start_month, end_month]],
				"status": "Approved",
				"docstatus": 1,
				"permission_type": self.permission_type,
			},
			fields=["*"]
		)

		permission_type = frappe.get_doc("Permission Type", self.permission_type)
		max_frequency = permission_type.permission_frequency_per_month

		if len(permissions) >= max_frequency:
			duplicate_links = ", ".join(
				[get_link_to_form("Permission", d.name) for d in permissions]
			)
			frappe.throw(
				_("You already have {0} permissions per month. Permissions for the date {1} are already marked in: {2}.").format(
					frappe.bold(max_frequency),
					frappe.bold(format_date(self.date)),
					duplicate_links,
				),
				title=_("Over Allocation Permission"),
				exc=OverAllocationPermissionError,
			)

	
	def process_permission(self):
		if not self.permission_type or not self.employee:
			frappe.throw(_("Permission Type and Employee are required"))

		permission_type = frappe.get_doc("Permission Type", self.permission_type)
		print(permission_type.name)
		if permission_type.deduct_from_leave_balance:
			is_exist = frappe.db.exists(
				"Leave Application",
				{
					"employee": self.employee,
					"from_date": self.date,
					"to_date": self.date,
					"status": "Approved",
				},
			)
			if not is_exist:
				try:
					# leave_application = frappe.get_doc({
					# 	"doctype": "Leave Application",
					# 	"employee": self.employee,
					# 	"leave_type": permission_type.deduct_from_leave_type,
					# 	"from_date": self.date,
					# 	"to_date": self.date,
					# 	"half_day": 1,
					# 	"description": f"Automatically created for {self.doctype} on {self.date}",
					# 	"posting_date": self.date,
					# 	"status": "Approved",
					# })
					# leave_application.insert(ignore_permissions=True)
					# leave_application.submit()
					# frappe.msgprint(_("Leave Application Created"))
					# return leave_application.name
					company = frappe.db.get_single_value("Global Defaults", "default_company")
					leave_ledger = frappe.get_doc({
						"doctype": "Leave Ledger Entry",
						"employee": self.employee,
						"leave_type": permission_type.deduct_from_leave_type,
						"transaction_type": self.doctype,
						"transaction_name": self.name,
						"leaves": -0.5,
						"from_date": self.date,
						"to_date": self.date,
						"company": company,
						"holiday_list": frappe.get_doc("Company", company).default_holiday_list
					})
					leave_ledger.insert(ignore_permissions=True)
					leave_ledger.submit()

					frappe.msgprint(_("Leave Ledger Created"))
				except Exception as e:
					frappe.throw(_("Error creating Leave Ledger: {0}").format(str(e)))
		else:
			frappe.msgprint(_("Permission does not require leave deduction."))

			