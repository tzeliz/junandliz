from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, Response
from datetime import datetime
import csv
import os
import io
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import sqlite3

app = Flask(__name__, static_folder='static', static_url_path='/static')

DB_PATH = os.path.join('/var/data', 'rsvps.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    rsvp = db.Column(db.String, nullable=False)
    dietary = db.Column(db.String, default='')
    phone_number = db.Column(db.String, default='')
    dance_song = db.Column(db.String, default='')

@app.before_request
def create_tables():
    db.create_all()

# Load short names
def load_short_names():
    guests = {}
    with open('names.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            guests[row['code']] = {
                'name': row['name'],
                'formal_invite': row.get('formal_invite', 'no').lower()  # default to 'no'
            }
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

    guest = guest_data[code]
    guest_name = guest['name']
    formal_invite = guest['formal_invite']

    return render_template('invitation.html',
                           guest_name=guest_name,
                           formal_invite=formal_invite,
                           code=code)

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

    submitted_guests = {rsvp.name for rsvp in RSVP.query.with_entities(RSVP.name).all()}

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

    # Check if this guest has already RSVP'd
    existing = RSVP.query.filter_by(name=name).first()
    if existing:
        return jsonify({'error': 'You’ve already submitted an RSVP. If you need to make a change, please contact us.'}), 400

    new_rsvp = RSVP(
        timestamp=timestamp,
        name=name,
        rsvp=rsvp,
        dietary=dietary,
        phone_number=full_phone,
        dance_song=song
    )
    db.session.add(new_rsvp)
    db.session.commit()

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

@app.route('/export-csv')
def export_csv():
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query the data you want to export
    cursor.execute("SELECT * FROM rsvp")
    rows = cursor.fetchall()

    # Get column names from cursor description
    columns = [desc[0] for desc in cursor.description]

    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)  # write header
    writer.writerows(rows)    # write data rows

    conn.close()

    # Build the response to download the CSV
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=rsvps_export.csv"
    return response

@app.route('/debug-tables')
def debug_tables():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify({"tables": tables})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
