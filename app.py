from flask import Flask, render_template, request
from datetime import datetime
import csv

app = Flask(__name__)

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

@app.route('/')
def save_the_date():
    code = request.args.get('code')
    guest_name = guest_data.get(code, "Guest")  # Default to 'Guest' if code is not found
    return render_template('index.html', guest_name=guest_name)

if __name__ == '__main__':
    app.run(debug=True)
