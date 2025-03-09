from flask import Flask, render_template, request, redirect, url_for
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

#def save_the_date():
    # Remove the code requirement and always display "Guest"
 #   guest_name = "Guest"
 #  return render_template('save_the_date.html', guest_name=guest_name)

# Route for Invitation page
#@app.route('/invitation')
#def invitation():
 #   code = request.args.get('code')
  #  if not code or code not in guest_data:
   #     return redirect(url_for('access_denied'))

    #guest_name = guest_data[code]
    #return render_template('invitation.html', guest_name=guest_name)
@app.route('/invitation')
def invitation():
    # Remove the code requirement and always display "Guest"
    guest_name = "Guest"
    return render_template('invitation.html', guest_name=guest_name)

# Route for "Access Denied" page
@app.route('/access-denied')
def access_denied():
    return render_template('access_denied.html')  # Render a template for access denied

if __name__ == '__main__':
    app.run(debug=True)

