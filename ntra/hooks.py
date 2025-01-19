app_name = "ntra"
app_title = "Ntra"
app_publisher = "Mohammed Nasser"
app_description = "NTRA"
app_email = "nasser@nasserx.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "ntra",
# 		"logo": "/assets/ntra/logo.png",
# 		"title": "Ntra",
# 		"route": "/ntra",
# 		"has_permission": "ntra.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ntra/css/ntra.css"
app_include_js = "/assets/ntra/js/socket.js"

# include js, css files in header of web template
# web_include_css = "/assets/ntra/css/ntra.css"
# web_include_js = "/assets/ntra/js/ntra.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ntra/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Job Applicant" : "public/js/job_applicant.js",
            "Employee Onboarding": "public/js/employee_onboarding.js",
            "Employee": "public/js/employee.js",
            "Goal": "public/js/goal.js",
            "Leave Application": "public/js/leave_application.js",
            "Task":"public/js/task.js",
            "Appraisal":"public/js/appraisal.js",
            "Payroll Entry":"public/js/payroll_entry.js",
            "Salary Component":"public/js/salary_component.js",
            "Travel Request": "public/js/travel_request.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
doctype_tree_js = {"Goal" : "public/js/goal_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ntra/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ntra.utils.jinja_methods",
# 	"filters": "ntra.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ntra.install.before_install"
# after_install = "ntra.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ntra.uninstall.before_uninstall"
# after_uninstall = "ntra.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ntra.utils.before_app_install"
# after_app_install = "ntra.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ntra.utils.before_app_uninstall"
# after_app_uninstall = "ntra.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ntra.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Goal": "ntra.overrides.goal.CustomGoal",
    "Leave Application":"ntra.overrides.leave_application.CustomLeaveApplication",
    "Salary Slip":"ntra.overrides.salary_slip.CustomSalarySlip",
    "Overtime Request": "ntra.overrides.overtime_request.CustomOvertimeRequest",
    "Payroll Entry": "ntra.overrides.payroll_entry.CustomPayrollEntry",
    "Salary Structure Assignment": "ntra.overrides.salary_structure_assignment.CustomSalaryStructureAssignment",
    "Leave Ledger Entry": "ntra.overrides.leave_ledger_entry.CustomLeaveLedgerEntry",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Employee Performance Feedback": {
		"validate": "ntra.events.calculate_rating",
	},
    "Employee Transfer":{
        "before_submit": "ntra.event.employee_transfer.before_submit"
    },
    "Appraisal": {
		"validate": "ntra.events.calculate_rating2",
	},
    "Employee": {
		"validate": ["ntra.events.validate_employee",
                     "ntra.events.translate_name_arabic_to_english"],
        "before_insert": "ntra.event.employee.validate",
        # "before_save": "ntra.effective_dates.before_save",
	},
    "Goal": {
		"validate":[ 
            "ntra.events.goal_validation",
            "ntra.event.objective.validate"
        ],
        "on_update": "ntra.events.update_weight",
        "after_insert": "ntra.events.create_task",
	},
    "Leave Application": {
        "validate": ["ntra.events.validate_maternity_leave","ntra.events.leave_without_pay","ntra.event.leave_application.validate_maximum_leaves_time","ntra.events.validate_leave_application"],
        "on_submit": ["ntra.events.validate_attachment","ntra.events.calculate_sick_leave_salary" ],
        # "validate": "ntra.events.leave_without_pay",
        # "on_submit": "ntra.events.calculate_sick_leave_salary",
        # "validate": "ntra.event.leave_application.validate_maximum_leaves_time",
    },
    "Salary Slip": {
        "after_insert": "ntra.events.append_sickleave",
        "before_save": ["ntra.event.salary_slip.get_stamp_tax_amount",
                        "ntra.event.salary_slip.stamp_tax_formula"],
        "validate": ["ntra.event.salary_slip.calculate_leave_without_pay"
                        ],
    },
    "Attendance": {
        "after_insert": "ntra.event.attendance.validate_attendance",
        "on_submit": ["ntra.event.attendance.security_shift", "ntra.event.attendance.calculate_employee_record"],
        "on_cancel": ["ntra.event.attendance.on_cancel_attendance"],
                        
	},
    "Purchase Invoice": {
        "on_submit": "ntra.event.purchase_invoice.update_actual_cost"
    },
    "Task":{
        "on_update": "ntra.event.task.after_save"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"ntra.tasks.all"
	# ],
	"daily": [
		"ntra.api.update_employee_trainings",
        "ntra.events.auto_approve_pending_leaves",
        "ntra.events.update_ad_hocs_for_appraisals",
        "ntra.events.expired_document_type",
        "ntra.events.proccess_contract_renewal"
	],
	# "hourly": [
	# 	"ntra.tasks.hourly"
	# ],
	# "weekly": [
	# 	"ntra.tasks.weekly"
	# ],
	# "monthly": [
	# 	"ntra.tasks.monthly"
	# ],
}

# Testing
# -------

# before_tests = "ntra.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ntra.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ntra.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ntra.utils.before_request"]
# after_request = ["ntra.utils.after_request"]

# Job Events
# ----------
# before_job = ["ntra.utils.before_job"]
# after_job = ["ntra.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ntra.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


fixtures = [
    {"dt": "Custom Field", "filters": [
        [
            "module", "in", [
                "Ntra"
            ]
        ]
    ]},
    {"dt": "Role", "filters": [
        [
            "name", "in", [
                "Objective"
            ]
        ]
    ]}
]

import frappe
import ntra

frappe.api.handle = ntra.handle