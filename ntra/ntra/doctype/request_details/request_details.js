// Copyright (c) 2025, Mohammed Nasser and contributors
// For license information, please see license.txt

frappe.ui.form.on("Request Details", {
    refresh: function(frm) {
        frm.set_query("meeting_rooms", function() {
            return {
                filters: {
                    "room_status": "Active"
                }
            };
        });
    },
    meeting_rooms: function(frm) {
        if(frm.doc.meeting_rooms){
            frappe.call({
                method: "get_meeting_room_details",
                doc: frm.doc,
                callback: function(r) {
                    // console.log(r.message);
                    frm.doc.table_csol = [];
                    if (r.message) {
                        r.message.forEach(function(amenities_details) {
                            if (amenities_details.amenities){
                                var child_table = frm.add_child( "table_csol");
                                frappe.model.set_value(child_table.doctype, child_table.name, "amenities", amenities_details.amenities);
                            }

                        });
                        // frm.set_value("total_time", r.message.total_time);
                        // frm.set_value("room_capacity", r.message.room_capacity);
                    }
                    frm.refresh_field("table_csol");
                }
            })
        }
    },
	start_date(frm) {
         if (frm.doc.meeting_rooms && frm.doc.start_date)
            {
                frappe.call({
                method: "get_appointment_slots",
                doc: frm.doc,
                callback: function(r) {
                    console.log(r.message);
                    if (r.message) {
                        let slots = [];
                        r.message.forEach(function(slot) {
                            if (slot.availability)
                                slots.push(slot.time.split("+")[0]);
                        })
                        frm.set_df_property("available_slot", "options", slots);
                    }
                }
            })
        }
        else{
            frm.set_df_property("available_slot", "options", []);

            frm.set_value("start_date", "");
        }
        
	},
    available_slot(frm) {
        if (frm.doc.available_slot) {
            // Parse available_slot as a Date object
            let availableSlot = new Date(frm.doc.available_slot);
        
            // Calculate 'from_time' as the timestamp of the available slot
            const fromTime = availableSlot.getTime();
        
            // Create a new Date object for 'to_time'
            let toTime = new Date(availableSlot);
            toTime.setMinutes(toTime.getMinutes() + frm.doc.total_time); // Add the total time in minutes
        
            // Format 'from_time' and 'to_time' as "HH:mm:ss" for display
            const formatTime = (date) => date.toTimeString().split(' ')[0];
        
            frm.set_value("from_time", formatTime(availableSlot)); // Format and set 'from_time'
            frm.set_value("to_time", formatTime(toTime));          // Format and set 'to_time'
        }
        
        
   },
});
