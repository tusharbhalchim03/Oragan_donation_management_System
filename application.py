from flask import Flask, render_template, request,jsonify
import pymongo
from functools import wraps
from flask import flash
from pymongo import MongoClient
from pymongo.errors import WriteConcernError
from bson import ObjectId, json_util
from flask import Flask, render_template, request, redirect, session, url_for
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


application = Flask(__name__)
application.secret_key = 'p26b5LZUEGuPkvekv6ZzkwInufEDyjfT'

client = MongoClient('mongodb+srv://rameshbhopale2021:root@cluster0.bzoxmna.mongodb.net/')
# client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.2')
db = client.mydatabase
collection1 = db.donarData
collection2 = db.patientData
collection3 = db.queryData

# Define a decorator function to check if the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Access denied. Administrative login required.', 'error')
            return render_template("admin.html")  # Redirect to the admin login page
           
        return f(*args, **kwargs)
    return decorated_function


# Redirecting to adminPanel.html i.e homePage - template
@application.route("/")
def home():
    return render_template("home.html")


# donar Registration Store to mongoDb database
@application.route('/insert_donar', methods=['POST'])
def insert_data():
    data = {
        "DonarName": request.form['DonarName'],
        "Age": int(request.form['Age']),
        "Gender": request.form['Gender'],
        "address": request.form['address'],
        "BloodGroup": request.form['BloodGroup'],
        "Email": request.form['Email'],
        "Contactnumber": request.form['Contactnumber'],
        "DonateOrgan": request.form['DonateOrgan'],
        "CausesOfDeath": request.form['CausesOfDeath'],
        "Status": "OUT"
    }

    # Insert data into MongoDB
    insert_result = collection1.insert_one(data)

    if insert_result.inserted_id:
        return render_template("donor.html")
    else:
        return "Registration failed..."

# Redirecting to donor.html template.
@application.route('/donor')
def donor():
    return render_template('donor.html')

# patient Registration Store to mongoDb database
# @application.route('/insert_patient', methods=['POST'])
# def insert_patient_data():
#     data = {
#         "Patientname": request.form['Patientname'],
#         "Age": int(request.form['Age']),
#         "Gender": request.form['Gender'],
#         "address": request.form['address'],
#         "BloodGroup": request.form['BloodGroup'],
#         "Email": request.form['Email'],
#         "Contactnumber": request.form['Contactnumber'],
#         "NeededOrgan": request.form['NeededOrgan'],
#         "Timereqired": request.form['Timereqired'],
#         "Status": "Waiting"
#     }

#     # Insert data into MongoDB
#     insert_result = collection2.insert_one(data)

#     if insert_result.inserted_id:
#         return render_template('patient.html')
     
#     else:
#         return "Registration failed..."


# patient Registration Store to mongoDb database
@application.route('/insert_patient', methods=['POST'])
def insert_patient_data():
    try:
        data = {
            "Patientname": request.form['Patientname'],
            "Age": int(request.form['Age']),
            "Gender": request.form['Gender'],
            "address": request.form['address'],
            "BloodGroup": request.form['BloodGroup'],
            "Email": request.form['Email'],
            "Contactnumber": request.form['Contactnumber'],
            "NeededOrgan": request.form['NeededOrgan'],
            "Timereqired": request.form['Timereqired'],
            "Status": "Waiting"
        }

        # Insert data into MongoDB
        insert_result = collection2.insert_one(data)

        if insert_result.inserted_id:
            return render_template('patient.html')
        else:
            return "Registration failed..."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Redirecting to patient.html template
@application.route('/patient')
def patient():
    return render_template('patient.html')

# Redirecting admin.html template
@application.route('/admin')
def admin():
    return render_template('admin.html')

#  Hardcoded admin credentials
admin_username = 'Admin'
admin_password = 'Admin'

# Redirecting to Admin.html
@application.route('/admin_login', methods=['GET', 'POST'])
def admin_login():   
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['password']

        # Check if the entered credentials match the hardcoded admin credentials
        if username == admin_username and password == admin_password:
            # Set a session variable to indicate admin login
            session['admin_logged_in'] = True
            return render_template('adminPanel.html')
        else:
            return 'Login failed. Please check your credentials.'

    return render_template('adminPanel.html')



# Define a function to check if the user is logged in as an admin
def is_admin_logged_in():
    return session.get('admin_logged_in', False)


# Redirecting from table.html
@application.route("/donar-details")
@admin_required
def get_donor_details():

    donor_data = list(collection1.find())
    # Convert ObjectId to string representation
    for item in donor_data:
        item['_id'] = str(item['_id'])
    return render_template("adminPanel.html", donor_data=donor_data)

@application.route('/delete-donor', methods=['POST'])
def delete_donor():
    if request.method == 'POST':
        donor_id = request.form.get('donor_id')
        # Delete the donor entry based on the donor_id
        collection1.delete_one({'_id': ObjectId(donor_id)})
    return redirect(url_for('get_donor_details'))

# Redirecting from table2.html
@application.route("/patient-details")
@admin_required
def get_patient_details():
    patient_data = list(collection2.find())
    # Convert ObjectId to string representation
    for item in patient_data:
        item['_id'] = str(item['_id'])
    return render_template("patientDetails.html", patient_data=patient_data)

@application.route('/delete-patient', methods=['POST'])

def delete_patient():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        # Delete the donor entry based on the patient_id
        collection2.delete_one({'_id': ObjectId(patient_id)})
    return redirect(url_for('get_patient_details'))


# #Redirecting to organtype.html
@application.route('/search-donor', methods=['GET'])
@admin_required
def organtype():
    return render_template('searchDonor.html')


#Redirecting from organtype.html
@application.route('/search-donor2', methods=['GET'])
@admin_required
def search_donor():
    try:
        organ_to_donate = request.args.get('DonateOrgan')

        donor_data = list(collection1.find({"DonateOrgan" : organ_to_donate}))

        # Convert ObjectId to string representation
        for item in donor_data:
            item['_id'] = str(item['_id'])

        # return jsonify(donor_data), 200
        return render_template("searchDonor.html", donor_data=donor_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#Redirecting to organtypePatient.html
@application.route('/search-patient', methods=['GET'])
def organType2():
    return render_template('searchPatient.html')


#Redirecting from organtypePatient.html
@application.route('/search-patient2', methods=['GET'])
@admin_required
def search_patient():
    try:
        organ_to_donate2 = request.args.get('NeededOrgan')

        patient_data = list(collection2.find({"NeededOrgan" : organ_to_donate2}))

        # Convert ObjectId to string representation
        for item in patient_data:
            item['_id'] = str(item['_id'])

        # return jsonify(donor_data), 200
        return render_template("searchPatient.html", patient_data=patient_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Redirecting to organ-donate-process
@application.route('/organ-donate-process')
@admin_required
def organDonateProcess():
    donor_data = list(collection1.find())
    # Convert ObjectId to string representation
    for item in donor_data:
        item['_id'] = str(item['_id'])
    return render_template("organDonateProcess.html", donor_data=donor_data)

@application.route('/organ-process-form', methods=['POST'])
@admin_required
def organ_donate_process():
    if request.method == 'POST':
        donor_id = request.form.get('donor_id')
        action = request.form.get('action')

        # Fetch the selected donor from the database
        donor = collection1.find_one({'_id': ObjectId(donor_id)})

        if donor:
            # Toggle the donor status
            new_status = "OUT" if action == "IN" else "IN"
            collection1.update_one({'_id': ObjectId(donor_id)}, {'$set': {'Status': new_status}})

            if new_status == "IN":
                matching_patient = collection2.find_one({'NeededOrgan': donor['DonateOrgan'], 'Status': ''})
                if matching_patient:
                    # Update the patient's status to "Donated" and set the organ donor
                    collection2.update_one({'_id': matching_patient['_id']}, {'$set': {'Status': 'Donated'}})

    return redirect(url_for('organDonateProcess'))

    # If the operation is not successful or there's an error, return to the same page
    return redirect(url_for('organDonateProcess.html'))


@application.route('/donated-patient')
@admin_required
def donated_patients():
    patient_data = list(collection2.find({'Status': 'Donated'}))

    for item in patient_data:
        item['_id'] = str(item['_id'])
    return render_template("donatedPatient.html", patient_data=patient_data)

@application.route('/not-donated-patient')
@admin_required
def not_donated_patients():
 
    patient_data = list(collection2.find({'Status': 'Waiting'}))
    # Convert ObjectId to string representation
    for item in patient_data:
        item['_id'] = str(item['_id'])
    return render_template("notDonatedPatient.html", patient_data= patient_data)



# Redirecting the query
@application.route('/submit_query', methods=['POST'])
def submit_query():
    query = {
        "full_name" : request.form['full_name'],
        "phone_number" : request.form['phone_number'],
        "email" : request.form['email'],
        "message" : request.form['message']
    }


    # Insert data into MongoDB
    insert_result = collection3.insert_one(query)

   
    if insert_result.inserted_id:
        return render_template("home.html")
    else:
        return "Registration failed..."

# Redirecting the query
@application.route('/query')
def get_query():
    queries = list(collection3.find())
    # Convert ObjectId to string representation
    for item in queries:
        item['_id'] = str(item['_id'])
    return render_template("query.html", queries = queries)

# Redirecting to logout.html
@application.route('/logout')
def logout():
    session['admin_logged_in']= False
    return render_template('admin.html')



if __name__ == '__main__':
    application.run(debug=True)
