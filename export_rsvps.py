from app import db, RSVP
import csv

with open('local_rsvps_export.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Timestamp', 'Name', 'RSVP', 'Dietary', 'Phone Number', 'Dance Song'])

    for r in RSVP.query.all():
        writer.writerow([r.timestamp, r.name, r.rsvp, r.dietary, r.phone_number, r.dance_song])