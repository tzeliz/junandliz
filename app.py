from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from datetime import datetime
import csv
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')

CSV_FILE = 'rsvps.csv'

# Load short names
def load_short_names():
    guests = {}
    with open('names.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            guests[row['code']] = row['name']
    return guests

# Load full names
def load_full_names():
    full_guests = {}
    with open('full_names.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            full_guests[row['code']] = row['name']
    return full_guests

# Load data
guest_data = load_short_names()
guest_full_data = load_full_names()

@app.route('/')
def save_the_date():
    code = request.args.get('code')
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))
    guest_name = guest_data.get(code, "Guest")
    return render_template('save_the_date.html', guest_name=guest_name)

@app.route('/invitation')
def invitation():
    code = request.args.get('code')
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))
    guest_name = guest_data[code]
    return render_template('invitation.html', guest_name=guest_name, code=code)

@app.route('/details')
def details():
    code = request.args.get('code')
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))
    return render_template('details.html', code=code)

@app.route('/rsvp')
def rsvp():
    code = request.args.get('code')
    if not code or code not in guest_full_data:
        return redirect(url_for('access_denied'))

    raw_guest_string = guest_full_data[code]
    guests = [g.strip() for part in raw_guest_string.split('&') for g in part.split(',')]

    # Load names that already RSVP'd
    submitted_guests = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                submitted_guests.add(row['Name'])

    return render_template('rsvp.html', guests=guests, submitted_guests=list(submitted_guests), group_name=raw_guest_string, code=code)

@app.route('/submit-rsvp', methods=['POST'])
def submit_rsvp():
    code = request.args.get('code')
    if not code or code not in guest_full_data:
        return redirect(url_for('access_denied'))

    data = request.get_json()

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

@app.route('/favourites')
def favourites():
    code = request.args.get('code')
    if not code or code not in guest_data:
        return redirect(url_for('access_denied'))
    return render_template('favourites.html', code=code)

@app.route('/access-denied')
def access_denied():
    return render_template('access_denied.html')

if __name__ == '__main__':
    app.run(debug=True)
