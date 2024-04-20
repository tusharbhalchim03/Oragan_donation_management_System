from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import pymongo
from pymongo import MongoClient
from bson import ObjectId, json_util

app = Flask(__name__)
app.secret_key = 'p26b5LZUEGuPkvekv6ZzkwInufEDyjfT'

# Database Setup
client = MongoClient('mongodb://localhost:27017/')
db = client.mydatabase
collection1 = db.donorData  # Fixed typo from 'donarData'
collection2 = db.patientData

# Redirect to home page
@app.route("/")
def home():
    return render_template("home.html")

# Donor registration
@app.route('/insert_donor', methods=['POST'])  # Fixed typo from 'donar'
def insert_donor():
    data = {
        "DonorName": request.form['DonarName'],  # Keep input consistent
        "Age": int(request.form['Age']),
        "Gender": request.form['Gender'],
        "Address": request.form['address'],
        "BloodGroup": request.form['BloodGroup'],
        "Email": request.form['Email'],
        "ContactNumber": request.form['Contactnumber'],
        "DonateOrgan": request.form['DonateOrgan'],
        "CausesOfDeath": request.form['CausesOfDeath'],
        "Status": "OUT"
    }
    insert_result = collection1.insert_one(data)

    if insert_result.inserted_id:
        return render_template("donor.html")
    return "Registration failed..."

@app.route('/donor')
def donor():
    return render_template('donor.html')

# Patient registration
@app.route('/insert_patient', methods=['POST'])
def insert_patient():
    data = {
        "PatientName": request.form['Patientname'],
        "Age": int(request.form['Age']),
        "Gender": request.form['Gender'],
        "Address": request.form['address'],
        "BloodGroup": request.form['BloodGroup'],
        "Email": request.form['Email'],
        "ContactNumber": request.form['Contactnumber'],
        "NeededOrgan": request.form['NeededOrgan'],
        "TimeRequired": request.form['Timereqired'],
        "Status": "Waiting"
    }
    insert_result = collection2.insert_one(data)

    if insert_result.inserted_id:
        return render_template('patient.html')
    return "Registration failed..."

@app.route('/patient')
def patient():
    return render_template('patient.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# Admin login
admin_username = 'Admin'
admin_password = 'Admin'

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['password']
        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            return render_template('adminPanel.html')
        return 'Login failed. Please check your credentials.'
    return render_template('admin.html')

# Fetch and display donor details
@app.route("/donor-details")
def get_donor_details():
    donor_data = list(collection1.find())
    for item in donor_data:
        item['_id'] = str(item['_id'])
    return render_template("adminPanel.html", donor_data=donor_data)

@app.route('/delete-donor', methods=['POST'])
def delete_donor():
    donor_id = request.form.get('donor_id')
    collection1.delete_one({'_id': ObjectId(donor_id)})
    return redirect(url_for('get_donor_details'))

@app.route("/patient-details")
def get_patient_details():
    patient_data = list(collection2.find())
    for item in patient_data:
        item['_id'] = str(item['_id'])
    return render_template("patientDetails.html", patient_data=patient_data)

@app.route('/delete-patient', methods=['POST'])
def delete_patient():
    patient_id = request.form.get('patient_id')
    collection2.delete_one({'_id': ObjectId(patient_id)})
    return redirect(url_for('get_patient_details'))

@app.route('/search-donor')
def search_donor_form():
    return render_template('searchDonor.html')

@app.route('/search-donor-results', methods=['GET'])
def search_donor_results():
    organ = request.args.get('DonateOrgan')
    donor_data = list(collection1.find({"DonateOrgan": organ}))
    for item in donor_data:
        item['_id'] = str(item['_id'])
    return render_template("searchDonor.html", donor_data=donor_data)

@app.route('/search-patient')
def search_patient_form():
    return render_template('searchPatient.html')

@app.route('/search-patient-results', methods=['GET'])
def search_patient_results():
    organ = request.args.get('NeededOrgan')
    patient_data = list(collection2.find({"NeededOrgan": organ}))
    for item in patient_data:
        item['_id'] = str(item['_id'])
    return render_template("searchPatient.html", patient_data=patient_data)

@app.route('/organ-donate-process')
def organ_donate_process_page():
    donor_data = list(collection1.find({'Status': 'OUT'}))
    for item in donor_data:
        item['_id'] = str(item['_id'])
    return render_template("organDonateProcess.html", donor_data=donor_data)

@app.route('/organ-process-form', methods=['POST'])
def organ_donate_process():
    donor_id = request.form.get('donor_id')
    action = request.form.get('action')

    try:
        donor = collection1.find_one({'_id': ObjectId(donor_id)})
        if donor:
            new_status = "IN" if action == "IN" else "OUT"
            collection1.update_one({'_id': ObjectId(donor_id)}, {'$set': {'Status': new_status}})

            if new_status == "IN":
                matching_patient = collection2.find_one({'NeededOrgan': donor['DonateOrgan'], 'Status': 'Waiting'})
                if matching_patient:
                    collection2.update_one({'_id': matching_patient['_id']}, {'$set': {'Status': 'Donated'}})
                    collection1.delete_one({'_id': ObjectId(donor_id)})
                    return redirect(url_for('donated_patients'))
            return redirect(url_for('organ_donate_process_page'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/donated-patient')
def donated_patients():
    patient_data = list(collection2.find({'Status': 'Donated'}))
    for item in patient_data:
        item['_id'] = str(item['_id'])
    return render_template("donatedPatient.html", patient_data=patient_data)

@app.route('/not-donated-patient')
def not_donated_patients():
    patient_data = list(collection2.find({'Status': 'Waiting'}))
    for item in patient_data:
        item['_id'] = str(item['_id'])
    return render_template("notDonatedPatient.html", patient_data=patient_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)