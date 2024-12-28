import frappe
from frappe import _
from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
from hrms.hr.utils import (
    get_holiday_dates_for_employee
)
from frappe.utils import (
    getdate,
    add_days,
    get_link_to_form,
    date_diff
)
from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import daterange
from hrms.hr.doctype.leave_ledger_entry.leave_ledger_entry import create_leave_ledger_entry
from hrms.hr.doctype.leave_application.leave_application import get_allocation_expiry_for_cf_leaves, get_number_of_leave_days
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

class CustomLeaveApplication(LeaveApplication):
    def create_ledger_entry_for_intermediate_allocation_expiry(self, expiry_date, submit, lwp):
        """Splits leave application into two ledger entries to consider expiry of allocation"""
        raise_exception = False if frappe.flags.in_patch else True

        leaves = get_number_of_leave_days(
            self.employee, self.leave_type, self.from_date, expiry_date, self.half_day, self.half_day_date
        )

        if leaves:
            args = dict(
                from_date=self.from_date,
                to_date=expiry_date,
                leaves=leaves * -1,
                is_lwp=lwp,
                holiday_list=get_holiday_list_for_employee(self.employee, raise_exception=raise_exception)
                or "",
            )
            create_leave_ledger_entry(self, args, submit)

        if getdate(expiry_date) != getdate(self.to_date):
            start_date = add_days(expiry_date, 1)
            leaves = get_number_of_leave_days(
                self.employee, self.leave_type, start_date, self.to_date, self.half_day, self.half_day_date
            )

            if leaves:
                args.update(dict(from_date=start_date, to_date=self.to_date, leaves=leaves * -1))
                create_leave_ledger_entry(self, args, submit)
    def create_separate_ledger_entries(self, alloc_on_from_date, alloc_on_to_date, submit, lwp):
        """Creates separate ledger entries for application period falling into separate allocations"""
        # for creating separate ledger entries existing allocation periods should be consecutive
        if (
            submit
            and alloc_on_from_date
            and alloc_on_to_date
            and add_days(alloc_on_from_date.to_date, 1) != alloc_on_to_date.from_date
        ):
            frappe.throw(
                _(
                    "Leave Application period cannot be across two non-consecutive leave allocations {0} and {1}."
                ).format(
                    get_link_to_form("Leave Allocation", alloc_on_from_date.name),
                    get_link_to_form("Leave Allocation", alloc_on_to_date),
                )
            )

        raise_exception = False if frappe.flags.in_patch else True

        if alloc_on_from_date:
            first_alloc_end = alloc_on_from_date.to_date
            second_alloc_start = add_days(alloc_on_from_date.to_date, 1)
        else:
            first_alloc_end = add_days(alloc_on_to_date.from_date, -1)
            second_alloc_start = alloc_on_to_date.from_date

        leaves_in_first_alloc = get_number_of_leave_days(
            self.employee,
            self.leave_type,
            self.from_date,
            first_alloc_end,
            self.half_day,
            self.half_day_date,
        )
        leaves_in_second_alloc = get_number_of_leave_days(
            self.employee,
            self.leave_type,
            second_alloc_start,
            self.to_date,
            self.half_day,
            self.half_day_date,
        )

        args = dict(
            is_lwp=lwp,
            holiday_list=get_holiday_list_for_employee(self.employee, raise_exception=raise_exception) or "",
        )

        if leaves_in_first_alloc:
            args.update(
                dict(from_date=self.from_date, to_date=first_alloc_end, leaves=leaves_in_first_alloc * -1)
            )
            create_leave_ledger_entry(self, args, submit)

        if leaves_in_second_alloc:
            args.update(
                dict(from_date=second_alloc_start, to_date=self.to_date, leaves=leaves_in_second_alloc * -1)
            )
            create_leave_ledger_entry(self, args, submit)
    
    
    
    def create_leave_ledger_entry(self, submit=True):
        if self.status != "Approved" and submit:
            return

        leave_type = frappe.get_cached_doc("Leave Type", self.leave_type)
        if not leave_type.custom_is_death_leave:
            expiry_date = get_allocation_expiry_for_cf_leaves(
                self.employee, self.leave_type, self.to_date, self.from_date
            )
            lwp = leave_type.is_lwp
            if expiry_date:
                self.create_ledger_entry_for_intermediate_allocation_expiry(expiry_date, submit, lwp)
            else:
                alloc_on_from_date, alloc_on_to_date = self.get_allocation_based_on_application_dates()
                if self.is_separate_ledger_entry_required(alloc_on_from_date, alloc_on_to_date):
                    # required only if negative balance is allowed for leave type
                    # else will be stopped in validation itself
                    self.create_separate_ledger_entries(alloc_on_from_date, alloc_on_to_date, submit, lwp)
                else:
                    raise_exception = False if frappe.flags.in_patch else True
                    args = dict(
                        leaves=self.total_leave_days * -1,
                        from_date=self.from_date,
                        to_date=self.to_date,
                        is_lwp=lwp,
                        holiday_list=get_holiday_list_for_employee(self.employee, raise_exception=raise_exception)
                        or "",
                    )
                    create_leave_ledger_entry(self, args, submit)
        else:
            from_date = self.from_date
            to_date = self.to_date
            difference_in_days = date_diff(self.to_date, self.from_date) + 1
            unpaid_day=0
            total_leave_days = self.total_leave_days
            if difference_in_days > leave_type.custom_leave_period_paid:
                unpaid_day = difference_in_days - leave_type.custom_leave_period_paid
                self.total_leave_days = leave_type.custom_leave_period_paid
                self.to_date = add_days(self.to_date, -1 * (unpaid_day))
                # 
                # frappe.msgprint(f"{self.from_date} {self.to_date}")
                expiry_date = get_allocation_expiry_for_cf_leaves(
                self.employee, self.leave_type, self.to_date, self.from_date
                    )
                lwp = 0
                if expiry_date:
                    self.create_ledger_entry_for_intermediate_allocation_expiry(expiry_date, submit, lwp)
                else:
                    alloc_on_from_date, alloc_on_to_date = self.get_allocation_based_on_application_dates()
                    if self.is_separate_ledger_entry_required(alloc_on_from_date, alloc_on_to_date):
                        # required only if negative balance is allowed for leave type
                        # else will be stopped in validation itself
                        self.create_separate_ledger_entries(alloc_on_from_date, alloc_on_to_date, submit, lwp)
                    else:
                        raise_exception = False if frappe.flags.in_patch else True
                        args = dict(
                            leaves=self.total_leave_days * -1,
                            from_date=self.from_date,
                            to_date=self.to_date,
                            is_lwp=lwp,
                            holiday_list=get_holiday_list_for_employee(self.employee, raise_exception=raise_exception)
                            or "",
                        )
                        create_leave_ledger_entry(self, args, submit)




            if unpaid_day:
                self.total_leave_days = unpaid_day
                self.to_date = to_date
                self.from_date = add_days(self.from_date, leave_type.custom_leave_period_paid)
                # frappe.throw(f"{self.from_date} {self.to_date}")
                expiry_date = get_allocation_expiry_for_cf_leaves(
                self.employee, self.leave_type, self.to_date, self.from_date
                    )
                lwp = 1
                # frappe.msgprint(f"{self.from_date} {self.to_date}")
                if expiry_date:
                    self.create_ledger_entry_for_intermediate_allocation_expiry(expiry_date, submit, lwp)
                else:
                    alloc_on_from_date, alloc_on_to_date = self.get_allocation_based_on_application_dates()
                    if self.is_separate_ledger_entry_required(alloc_on_from_date, alloc_on_to_date):
                        # required only if negative balance is allowed for leave type
                        # else will be stopped in validation itself
                        self.create_separate_ledger_entries(alloc_on_from_date, alloc_on_to_date, submit, lwp)
                    else:
                        raise_exception = False if frappe.flags.in_patch else True
                        args = dict(
                            leaves=self.total_leave_days * -1,
                            from_date=self.from_date,
                            to_date=self.to_date,
                            is_lwp=lwp,
                            holiday_list=get_holiday_list_for_employee(self.employee, raise_exception=raise_exception)
                            or "",
                        )
                        create_leave_ledger_entry(self, args, submit)



            self.total_leave_days = total_leave_days
            self.from_date = from_date
            self.to_date = to_date
            pass
    def create_or_update_attendance(self, attendance_name, date, unpaid=0):
        status = (
            "Half Day" if self.half_day_date and getdate(date) == getdate(self.half_day_date) else "On Leave"
        )

        if attendance_name:
            # update existing attendance, change absent to on leave
            doc = frappe.get_doc("Attendance", attendance_name)
            doc.db_set({"status": status, "leave_type": self.leave_type, "leave_application": self.name, "custom_unpaid":unpaid})
        else:
            # make new attendance and submit it
            doc = frappe.new_doc("Attendance")
            doc.employee = self.employee
            doc.employee_name = self.employee_name
            doc.attendance_date = date
            doc.company = self.company
            doc.leave_type = self.leave_type
            doc.leave_application = self.name
            doc.status = status
            doc.custom_unpaid = unpaid
            doc.flags.ignore_validate = True
            doc.insert(ignore_permissions=True)
            doc.submit()
    def update_attendance(self):
        if self.status != "Approved":
            return

        holiday_dates = []
        if not frappe.db.get_value("Leave Type", self.leave_type, "include_holiday"):
            holiday_dates = get_holiday_dates_for_employee(self.employee, self.from_date, self.to_date)
        leave_type = frappe.get_cached_doc("Leave Type", self.leave_type)
        if not leave_type.custom_is_death_leave:
            for dt in daterange(getdate(self.from_date), getdate(self.to_date)):
                date = dt.strftime("%Y-%m-%d")
                attendance_name = frappe.db.exists(
                    "Attendance", dict(employee=self.employee, attendance_date=date, docstatus=("!=", 2))
                )

                # don't mark attendance for holidays
                # if leave type does not include holidays within leaves as leaves
                if date in holiday_dates:
                    if attendance_name:
                        # cancel and delete existing attendance for holidays
                        attendance = frappe.get_doc("Attendance", attendance_name)
                        attendance.flags.ignore_permissions = True
                        if attendance.docstatus == 1:
                            attendance.cancel()
                        frappe.delete_doc("Attendance", attendance_name, force=1)
                    continue

                self.create_or_update_attendance(attendance_name, date)
        else:
            from_date = self.from_date
            to_date = self.to_date
            difference_in_days = date_diff(self.to_date, self.from_date) + 1
            unpaid_day=0
            total_leave_days = self.total_leave_days
            if difference_in_days > leave_type.custom_leave_period_paid:
                unpaid_day = difference_in_days - leave_type.custom_leave_period_paid
                self.total_leave_days = leave_type.custom_leave_period_paid
                self.to_date = add_days(self.to_date, -1 * unpaid_day)
                frappe.msgprint(f"{self.from_date} {self.to_date}")
                for dt in daterange(getdate(self.from_date), getdate(self.to_date)):
                    date = dt.strftime("%Y-%m-%d")
                    attendance_name = frappe.db.exists(
                        "Attendance", dict(employee=self.employee, attendance_date=date, docstatus=("!=", 2))
                    )

                    # don't mark attendance for holidays
                    # if leave type does not include holidays within leaves as leaves
                    if date in holiday_dates:
                        if attendance_name:
                            # cancel and delete existing attendance for holidays
                            attendance = frappe.get_doc("Attendance", attendance_name)
                            attendance.flags.ignore_permissions = True
                            if attendance.docstatus == 1:
                                attendance.cancel()
                            frappe.delete_doc("Attendance", attendance_name, force=1)
                        continue

                    self.create_or_update_attendance(attendance_name, date)
            if unpaid_day:
                self.total_leave_days = unpaid_day
                self.to_date = to_date
                self.from_date = add_days(self.from_date, leave_type.custom_leave_period_paid)
                frappe.msgprint(f"{self.from_date} {self.to_date}")
                for dt in daterange(getdate(self.from_date), getdate(self.to_date)):
                    date = dt.strftime("%Y-%m-%d")
                    attendance_name = frappe.db.exists(
                        "Attendance", dict(employee=self.employee, attendance_date=date, docstatus=("!=", 2))
                    )

                    # don't mark attendance for holidays
                    # if leave type does not include holidays within leaves as leaves
                    if date in holiday_dates:
                        if attendance_name:
                            # cancel and delete existing attendance for holidays
                            attendance = frappe.get_doc("Attendance", attendance_name)
                            attendance.flags.ignore_permissions = True
                            if attendance.docstatus == 1:
                                attendance.cancel()
                            frappe.delete_doc("Attendance", attendance_name, force=1)
                        continue

                    self.create_or_update_attendance(attendance_name, date, unpaid = 1)

            self.from_date = from_date
            self.to_date = to_date         
    pass