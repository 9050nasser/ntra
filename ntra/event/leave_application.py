import frappe
from datetime import datetime, timedelta

def validate_time(doc, method):

    # shift =timedelta(hours=7) 
    # if doc.custom_from_time and doc.custom_to_time:
    #     time_diff = datetime.strptime(doc.custom_to_time, "%H:%M:%S") - datetime.strptime(doc.custom_from_time, "%H:%M:%S")
    #     print(time_diff)
    #     print(time_diff.total_seconds() / shift.total_seconds())
    #     doc.total_leave_days = time_diff.total_seconds() / shift.total_seconds()
    pass