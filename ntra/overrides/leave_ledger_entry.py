import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import DATE_FORMAT, flt, get_link_to_form, getdate, today


class CustomLeaveLedgerEntry(Document):
	def on_cancel(self):
		# allow cancellation of expiry leaves
		if self.is_expired:
			frappe.db.set_value("Leave Allocation", self.transaction_name, "expired", 0)
		# else:
		# 	frappe.throw(_("Only expired allocation can be cancelled"))