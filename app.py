from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime, timedelta
import csv
import os 
import pytz

app = Flask(__name__, static_folder='static', static_url_path='/static')

CSV_FILE = 'rsvps.csv'
    
# Function to load guest data from CSV
def load_guest_data():
    guests = {}
    with open('names.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            guests[row['code']] = row['name']
    return guests

# Load guest data into a dictionary at the start
guest_data = load_guest_data()

# Route for "Save the Date" page
@app.route('/')
def save_the_date():
    code = request.args.get('code')
    # Check if the code is valid
    if not code or code not in guest_data:
        # Redirect to an "Access Denied" page if code is missing or invalid
        return redirect(url_for('access_denied'))
    
    # Fetch the guest name if the code is valid
    guest_name = guest_data.get(code, "Guest")
    return render_template('save_the_date.html', guest_name=guest_name)

# Route for Invitation page
@app.route('/invitation')
def invitation():
    code = request.args.get('code')
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))

    guest_name = guest_data[code]
    return render_template('invitation.html', guest_name=guest_name, code = code)

# Route for Details page
@app.route('/details')
def details():
    code = request.args.get('code')

    # Check if the code is valid
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))
    
    return render_template('details.html', code = code)

# Route for RSVP page
@app.route('/rsvp')
def rsvp():
    code = request.args.get('code')

    # Check if the code is valid
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))

    # Get full group name string from CSV (e.g., "Alex Smith & Jamie Tran")
    raw_guest_string = guest_data[code]

    # Split into individual names
    guests = [g.strip() for part in raw_guest_string.split('&') for g in part.split(',')]

    return render_template('rsvp.html', guests=guests, group_name=raw_guest_string, code=code)

# Route for Submit RSVP page
@app.route('/submit-rsvp', methods=['POST'])
def submit_rsvp():
    code = request.args.get('code')
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))
    
    data = request.get_json()  # read JSON

    name = data.get('guest_name')
    rsvp = data.get('rsvp_response')
    dietary = data.get('dietary_requirements', '')
    phone = data.get('phone_number')
    country_code = data.get('country_code', '')
    song = data.get('dance_song', '')
    timestamp = datetime.now().isoformat()

    full_phone = f"{country_code}{phone}" if phone else ''

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Timestamp', 'Name', 'RSVP', 'Dietary Requirements', 'Phone Number', 'Dance Song'])
        writer.writerow([timestamp, name, rsvp, dietary, full_phone, song])

    return jsonify({'success': True}), 200

# Route for Favourites page
@app.route('/favourites')
def favourites():
    code = request.args.get('code')
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))
    return render_template('favourites.html', code=code)

# Route for "Access Denied" page
@app.route('/access-denied')
def access_denied():
    return render_template('access_denied.html')  # Render a template for access denied

if __name__ == '__main__':
    app.run(debug=True)

