from flask import Flask, render_template, Response
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download-event')
def download_event():
    event_title = "Jun and Liz's Wedding"
    event_start = datetime(2025, 11, 29, 15, 0)  # 3 PM local time
    event_end = datetime(2025, 11, 29, 20, 0)    # 8 PM local time
    event_location = "Penang, Malaysia"
    event_description = "Join us for Jun and Liz's wedding celebration!"

    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Your Company//NONSGML v1.0//EN
BEGIN:VEVENT
UID:{event_start.strftime('%Y%m%dT%H%M%S')}@yourdomain.com
DTSTAMP:{event_start.strftime('%Y%m%dT%H%M%S')}
DTSTART:{event_start.strftime('%Y%m%dT%H%M%S')}
DTEND:{event_end.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{event_title}
LOCATION:{event_location}
DESCRIPTION:{event_description}
END:VEVENT
END:VCALENDAR
"""

    response = Response(ics_content)
    response.headers['Content-Disposition'] = 'attachment; filename=Jun_and_Liz_Wedding.ics'
    response.headers['Content-Type'] = 'text/calendar'
    return response

if __name__ == '__main__':
    app.run(debug=True)
