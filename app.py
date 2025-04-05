from flask import Flask, request, jsonify,redirect
from pymongo import MongoClient
import re
from datetime import datetime, timedelta
import time
import json
# import datetime
from appoint_flow import book_appointment, start_automation, appointment_flow, success_appointment,old_user_send,custom_appointment_flow
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from pdf import pdfdownload,pdfdownloadcdate
from date_and_slots import dateandtime

app = Flask(__name__)
CORS(app)



MONGO_URI = "mongodb+srv://care2connect:connect0011@cluster0.gjjanvi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("caredb")
doctors = db["doctors"] 
appointment = db["appointment"] 
templog = db["logs"] 

API_KEY = "1234"

# print(dateandtime(f'2025-03-23'))

# Home Route
@app.route("/")
def home():
    return "all done"

def is_recent(timestamp):
                timestamp = int(timestamp)  # Ensure it's an integer
                current_time = int(time.time())  # Get current timestamp
                return (current_time - timestamp) > 300

def checktext(text):
    match = re.match(r"(appoint_id)([a-f0-9]+)", text)
    if match.group(1)=="appoint_id":
        value = match.group(1)  # "67de8d2b81b4914ab512863d"
        # value = match.group(2)  # "67de8d2b81b4914ab512863d"
        return value
    else:
        return 0

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        VERIFY_TOKEN = "desitestt1"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403
    elif request.method == 'POST':
        data = request.json
        # print("Received data:", data)

        try:
            entry = data.get('entry', [])[0]  # Extract first entry
            changes = entry.get('changes', [])[0]  # Extract first change
            value = changes.get('value', {})

            message_info = value.get('messages', [])[0]  # Extract first message
            contact_info = value.get('contacts', [])[0]  # Extract first contact

            from_number = message_info.get('from')
            body = message_info.get('text', {}).get('body')
            msg_type = message_info.get('type')
            msg_type = message_info.get('type')
            timestamp = message_info.get('timestamp')
            name = contact_info.get('profile', {}).get('name')

            if is_recent(timestamp)==False:

                if msg_type == 'interactive' and "button_reply" in message_info.get('interactive', {}):
                    button_id = message_info["interactive"]["button_reply"]["id"]
                    print(button_id)
                    if button_id == "book_appointment":
                        return appointment_flow(from_number)
                    elif checktext(button_id) == "appoint_id":
                        match = re.match(r"(appoint_id)([a-f0-9]+)", button_id)
                        value = match.group(2)
                        tempdata = {"number":from_number,"id_value":value,"role":"custom_appointment","_id":from_number}
                        try:
                            templog.insert_one(tempdata)
                        except:
                            templog.update_one({'_id': from_number}, {'$set': tempdata})
                        return custom_appointment_flow(from_number)
                    else:
                        return "Invalid message type", 400
                elif msg_type == 'interactive' and "nfm_reply" in message_info.get('interactive', {}):
                    try:
                        return book_appointment(data)
                    except Exception as e:
                        return "Invalid message type", 400
                elif msg_type == 'text' and body.lower() == "hii":
                    print(body.lower())
                    return old_user_send(from_number)
                elif msg_type == 'text' and body.lower() == "hi":
                    print(body.lower())
                    return old_user_send(from_number)
                elif msg_type == 'text' and body.lower() == "pdf":
                    print(body.lower())
                    return pdfdownloadcdate(from_number)
                elif msg_type == 'text' and body.lower().split()[0] == "pdf":
                    print(body.lower())

                    match = re.search(r"\d{2}-\d{2}-\d{4}", body.lower())
                    if match:
                        extracted_date = match.group()  # "20-03-2024"
    
    # Convert to "YYYY-MM-DD" format
                        formatted_date = datetime.strptime(extracted_date, "%d-%m-%Y").strftime("%Y-%m-%d")
    
                        print(formatted_date)

                    return pdfdownload(from_number,formatted_date)
                else:
                    print(body.lower())
                    return "Invalid message type", 400
            else: 
                return "Invalid message type", 400

        except Exception as e:
            print("Error:", str(e))
            return jsonify({"error": "Invalid request"}), 400


def find_user():
    try:
        result = list(doctors.find({"phone": "8767"}, {"_id": 0}))  # Convert cursor to list, exclude '_id'
        if result:
            return result[0]
        else:
            return 404
    except Exception as e:
        return 404


@app.route("/add_user", methods=["POST"])
def add_user_query():
    try:
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        # password = data.get("password")
        # hashed_password = generate_password_hash(password)
        # data["password"] = hashed_password 
        result = doctors.insert_one(data).inserted_id
        return jsonify({"inserted_id": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/update_user/<string:id>/", methods=["POST"])
def update_user_query(id):
    try:
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        try:
            doc_id = ObjectId(id)
        except:
            return jsonify({"error": "Invalid ObjectId"}), 400
        result = doctors.update_one({'_id': doc_id}, {'$set': data})
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404
        elif result.modified_count == 0:
            return jsonify({"message": "No changes made"}), 200
        return jsonify({'success': True, "message": "User updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/update_appointment/<string:id>/", methods=["POST"])
def update_appointment_query(id):
    try:
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        try:
            doc_id = ObjectId(id)
        except:
            return jsonify({"error": "Invalid ObjectId"}), 400
        result = appointment.update_one({'_id': doc_id}, {'$set': data})
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404
        elif result.modified_count == 0:
            return jsonify({"message": "No changes made"}), 200
        return jsonify({'success': True, "message": "User updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_profile/<string:id>/", methods=["POST"])
def get_profile(id):
    try:
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        try:
            doc_id = ObjectId(id)
        except:
            return jsonify({"error": "Invalid ObjectId"}), 400
        document = doctors.find_one({"_id": doc_id})
        if not document:
            return jsonify({"error": "User not found"}), 404
        document["_id"] = str(document["_id"])
        return jsonify(document), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/get_appointment", methods=["POST"])
def get_appointment_list():
    try:
        api_key = request.headers.get("x-api-key")
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        # Fetch all appointments and convert ObjectId to string
        documents = list(appointment.find({}))
        if not documents:
            return jsonify({"error": "No appointments found"}), 404
        # Convert ObjectId to string for JSON response
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        return jsonify(documents), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
@app.route("/login", methods=["POST"])
def login():
    try:
        api_key = request.headers.get("x-api-key")
        
        if api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

        # Get request data
        data = request.json
        username = data.get("username")
        password = data.get("password")

        # Find user in database
        user = doctors.find_one({"email": username})
         
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401

        # Verify password
        if user["password"]!= password:
            return jsonify({"error": "Invalid username or password"}), 401

        try:
            if user["role"]== 'staff':
                return jsonify({"message": "Login successful","role":"staff","staffId":str(user['EmpID']),"doctorId":str(user['doctorId']) ,"user": str(user['_id']), "accessToken":str(user['accessToken']), "phonenumberID":str(user['phonenumberID'])}), 200
        except:

        # ✅ Generate JWT Token
            return jsonify({"message": "Login successful","role":"doctor", "user": str(user['_id']), "accessToken":str(user['accessToken']), "phonenumberID":str(user['phonenumberID'])}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Get Users (GET)
@app.route("/users", methods=["GET"])
def get_users():
    users = list(doctors.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field
    return jsonify(users)

@app.route("/fatch_date_and_time/<string:id>/", methods=["GET"])
def get_datetime(id):
    users = dateandtime(id) # Exclude MongoDB's default _id field
    return jsonify(users)

@app.route("/staff/<string:id>/", methods=["POST"])
def get_staff_list(id):
    try:
        api_key = request.headers.get("x-api-key")
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        # Fetch all appointments and convert ObjectId to string
        documents = list(doctors.find({"role":"staff","doctorId":id}))
        if not documents:
            return jsonify({"error": "No appointments found"}), 404
        # Convert ObjectId to string for JSON response
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        return jsonify(documents), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete User (DELETE)
@app.route("/delete_user", methods=["DELETE"])
def delete_user():
    data = request.json
    if not data or "email" not in data:
        return jsonify({"error": "Email required"}), 400

    result = doctors.delete_one({"email": data["email"]})
    if result.deleted_count:
        return jsonify({"message": "User deleted"}), 200
    else:
        return jsonify({"error": "User not found"}), 404
    
@app.route('/payment_callback/<string:id>/', methods=['GET', 'POST'])
def payment_callback(id):
    if request.method == 'GET':
        # Handle GET callback
        callback_data = request.args.to_dict()
    else:  # POST
        # Handle POST callback
        callback_data = request.json

    # Process the Razorpay response
    print("Callback Data:", callback_data)

    # Verify the payment status and act accordingly
    if callback_data.get('razorpay_payment_link_status') == 'paid':

        doc_id = ObjectId(id)
        retrieved_data = appointment.find_one({"_id": doc_id})

        print(retrieved_data['doctor_phone_id'])

        result = list(appointment.find({"doctor_phone_id": retrieved_data['doctor_phone_id'], "date_of_appointment":retrieved_data['date_of_appointment'],"amount":{"$gt": -1}}, {"_id": 0}))  # Convert cursor to list
        data_length = 1
        if result:
            data_length = len(result)+1

        xdate = retrieved_data['date_of_appointment']
        date_obj = datetime.strptime(xdate, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y%m%d")

        appoint_number = str(formatted_date)+'-'+str(data_length)

        dxxocument = doctors.find_one({'_id':ObjectId('67ee5e1bde4cb48c515073ee')})
        fee = float(dxxocument.get('appointmentfee'))

        appointment.update_one({'_id': doc_id},{'$set':{'status':'success','pay_id':callback_data.get('razorpay_payment_id'),'appoint_number':appoint_number,'amount':fee}})

        name = str(retrieved_data['patient_name'])
        payment_id = str(callback_data.get('razorpay_payment_id'))
        doa = str(retrieved_data['date_of_appointment'])
        tm = str(retrieved_data['time_slot'])
        phone = str(retrieved_data['whatsapp_number'])

        whatsapp_url = success_appointment(payment_id,appoint_number,name,doa,tm,phone)
        return redirect(whatsapp_url)
    else:
        # Payment failed or was not captured
        print("Payment failed or not captured!")
        return jsonify({'status': 'failed', 'message': 'Payment failed or not captured'}), 400



if __name__ == "__main__":
    app.run(port=5000,host="0.0.0.0")


# if __name__ == "__main__":
#     app.run(port=5000,debug=True)