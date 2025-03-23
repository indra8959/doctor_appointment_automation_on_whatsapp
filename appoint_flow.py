from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime, timedelta
import time
import json
from bson.objectid import ObjectId
from razorpay import pay_link

MONGO_URI = "mongodb+srv://indrajeet:indu0011@cluster0.qstxp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("medicruise")
doctors = db["doctors"] 
appointment = db["appointment"] 
templog = db["logs"] 

headers={'Authorization': 'Bearer EAAJdr829Xj4BO4B15MZAqnCnRp9PprXQP6AOlfw5gtYwVLdrKlSjwXta4o3wkkYalMVOZAARNRIVk7evjoiQg9cY7NfQzFqqXZCv7OQMbxgeQVkDBqnPZA1PcWWGZBN6AXNBrcqGXIINacmAwycthHMsh479FqVjkTWHPgZBrBlfXO93O0DZBOn1aB57vRZB1f0PNAZDZD','Content-Type': 'application/json'}
phone_id = '606444145880553'

# def checkoldappointment(phonenumber,fdate,name,doctorid):
#     result = list(appointment.find({"whatsapp_number":phonenumber,"doctor_phone_id":doctorid,"patient_name":name,"amount":{"$gt": 0}}))
# # print(appoint.val())

#     try:

#         date_str = fdate
#         date = datetime.strptime(date_str, "%Y-%m-%d")
#         new_date = date - timedelta(days=2)

#         print(new_date.strftime("%Y-%m-%d"))

#         from_date = datetime.strptime(new_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
#         to_date = datetime.strptime(date_str, "%Y-%m-%d")

#     except:
#         return 0
    
def send_payment_flow(from_number,name,date,slot,amount,link):

    print(from_number,name,date,slot,amount,link)

    external_url = "https://graph.facebook.com/v22.0/606444145880553/messages"  # Example API URL

    incoming_data = { 
        "messaging_product": "whatsapp", 
        "to": from_number, "type": "template", 
        "template": { 
            "name": "razorpay_send_link", 
            "language": { 
                "code": "en" 
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [{
                        "type": "text",
                        "text": name
                    },{
                        "type": "text",
                        "text": date
                    },{
                        "type": "text",
                        "text": slot
                    },{
                        "type": "text",
                        "text": amount
                    }]
                },
                {
                "type": "button",
                "index": "0",
                "sub_type": "url",
                "parameters": [
                    {
                        "type": "text",
                        "text": link
                    }
                ]}
            ]} 
        }

    response = requests.post(external_url, json=incoming_data, headers=headers)
    return "OK", 200

# print(send_payment_flow('918959690512','name','date','slot','amount','link'))

def custom_book_appointment(data):

    entry = data.get('entry', [])[0]  # Extract first entry
    changes = entry.get('changes', [])[0]  # Extract first change
    value = changes.get('value', {})

    message_info = value.get('messages', [])[0] 
    from_number = message_info.get('from')

    document = templog.find_one({'_id':from_number})


    appoint_data = appointment.find_one({"_id": ObjectId(document["id_value"])})

    print(appoint_data)

    response_json_str = data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['nfm_reply']['response_json']
    response_data = json.loads(response_json_str)
    print(response_data)

    

    name = appoint_data.get('patient_name')
    pname = appoint_data.get('guardian_name')
    date = response_data.get('Date_of_appointment_0')
    slot = response_data.get('Time_Slot_1')

    email = 'none'
    symptoms = 'none'
    age = 'none'
    dob = 'none'
    city = 'none'
    address = 'none'

    

    if appoint_data.get('email'):
        email = appoint_data.get('email')
    else:
        email = 'none'

    if response_data.get('Other_Symptoms_5'):
        symptoms = response_data.get('Other_Symptoms_5')
    else:
        symptoms = 'none'

    if appoint_data.get('age'):
        age = appoint_data.get('age')
    else:
        age = 'none'

    if appoint_data.get('date_of_birth'):
        dob = appoint_data.get('date_of_birth')
    else:
        dob = 'none'

    if appoint_data.get('city'):
        city = appoint_data.get('city')
    else:
        city = 'none'

    if appoint_data.get('address'):
        address = appoint_data.get('address')
    else:
        address = 'none'

    from_number = message_info.get('from')
    timestamp = message_info.get('timestamp')

    doctor_id = '12345'

    # result = list(doctors.find({"doctor_phone_id": doctor_id}, {"_id": 0}))  # Convert cursor to list
    # data_length = len(result)

    dataset = {
        'patient_name': name,
        'guardian_name': pname,
        'date_of_appointment': date,
        'time_slot': slot,
        'doctor_phone_id':doctor_id,
        'email' : email,
        'symptoms' : symptoms,
        'age' : age,
        'timestamp' : timestamp,
        'whatsapp_number' : from_number,
        'date_of_birth' : dob,
        'city' : city,
        'address' : address,
        'role':'appointment',
        'status':'created',
        "createdAt": 'x'
            }
    
    date_str = date
    xdate = datetime.strptime(date_str, "%Y-%m-%d")
    new_date = xdate - timedelta(days=3)

    
    from_date = datetime.strptime(new_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
    todate = datetime.strptime(date_str, "%Y-%m-%d")
    todate = todate.replace(hour=23, minute=59, second=59)  # Ensure full-day inclusion

# Query with date filtering (Convert date_of_appointment to datetime in query)
    result = list(appointment.find({
    "whatsapp_number": from_number,
    "patient_name": name,
    "doctor_phone_id": doctor_id,
    "amount":{"$gt": 0},
    "$expr": {
        "$and": [
            {"$gte": [{"$dateFromString": {"dateString": "$date_of_appointment"}}, from_date]},
            {"$lte": [{"$dateFromString": {"dateString": "$date_of_appointment"}}, todate]}
        ]
    }
    }).sort("date_of_appointment", -1).limit(1)) 

    if len(result)>0:
        retrieved_data = result[0]
        result = list(appointment.find({"doctor_phone_id": retrieved_data['doctor_phone_id'], "date_of_appointment":date,"amount":{"$gt": -1}}, {"_id": 0}))  # Convert cursor to list
        data_length = 1
        if result:
            data_length = len(result)+1

        xdate = date
        date_obj = datetime.strptime(xdate, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y%m%d")

        pay_id = str(retrieved_data['pay_id'])
        pay_id = "old_"+pay_id

        appoint_number = str(formatted_date)+'-'+str(data_length)

        appointment.insert_one({**dataset,'status':'success','pay_id':pay_id,'appoint_number':appoint_number,'amount':0})

        name = str(retrieved_data['patient_name'])
        phone = str(retrieved_data['whatsapp_number'])

        return success_appointment(pay_id,appoint_number,name,date,slot,phone)
    else:
        id = str(appointment.insert_one(dataset).inserted_id)
        print(id)
        link = pay_link(name,from_number,'ajeetindrajeet@gmail.com',id,200)
        print(link)
        amount = 200
        return send_payment_flow(from_number,name,date,slot,amount,link)

        


def book_appointment(data):

    entry = data.get('entry', [])[0]  # Extract first entry
    changes = entry.get('changes', [])[0]  # Extract first change
    value = changes.get('value', {})

    message_info = value.get('messages', [])[0] 
    response_json_str = data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['nfm_reply']['response_json']
    response_data = json.loads(response_json_str)
    print(response_data)

    if response_data.get('role')=='personal_flow':
        return custom_book_appointment(data)

    name = response_data.get('Patient_Name_2')
    pname = response_data.get('Guardian_Name')
    date = response_data.get('Date_of_appointment_0')
    slot = response_data.get('Time_Slot_1')

    email = 'none'
    symptoms = 'none'
    age = 'none'
    dob = 'none'
    city = 'none'
    address = 'none'


    if response_data.get('Email_4'):
        email = response_data.get('Email_4')
    else:
        email = 'none'

    if response_data.get('Other_Symptoms_5'):
        symptoms = response_data.get('Other_Symptoms_5')
    else:
        symptoms = 'none'

    if response_data.get('Age_3'):
        age = response_data.get('Age_3')
    else:
        age = 'none'

    if response_data.get('Date_Of_Birth'):
        dob = response_data.get('Date_Of_Birth')
    else:
        dob = 'none'

    if response_data.get('City'):
        city = response_data.get('City')
    else:
        city = 'none'

    if response_data.get('Address'):
        address = response_data.get('Address')
    else:
        address = 'none'

    from_number = message_info.get('from')
    timestamp = message_info.get('timestamp')

    doctor_id = '12345'

    # result = list(doctors.find({"doctor_phone_id": doctor_id}, {"_id": 0}))  # Convert cursor to list
    # data_length = len(result)

    dataset = {
        'patient_name': name,
        'guardian_name': pname,
        'date_of_appointment': date,
        'time_slot': slot,
        'doctor_phone_id':doctor_id,
        'email' : email,
        'symptoms' : symptoms,
        'age' : age,
        'timestamp' : timestamp,
        'whatsapp_number' : from_number,
        'date_of_birth' : dob,
        'city' : city,
        'address' : address,
        'role':'appointment',
        'status':'created',
        "createdAt": 'x'
            }
    
    date_str = date
    xdate = datetime.strptime(date_str, "%Y-%m-%d")
    new_date = xdate - timedelta(days=3)

    
    from_date = datetime.strptime(new_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
    todate = datetime.strptime(date_str, "%Y-%m-%d")
    todate = todate.replace(hour=23, minute=59, second=59)  # Ensure full-day inclusion

# Query with date filtering (Convert date_of_appointment to datetime in query)
    result = list(appointment.find({
    "whatsapp_number": from_number,
    "patient_name": name,
    "doctor_phone_id": doctor_id,
    "amount":{"$gt": 0},
    "$expr": {
        "$and": [
            {"$gte": [{"$dateFromString": {"dateString": "$date_of_appointment"}}, from_date]},
            {"$lte": [{"$dateFromString": {"dateString": "$date_of_appointment"}}, todate]}
        ]
    }
    }).sort("date_of_appointment", -1).limit(1)) 

    if len(result)>0:
        retrieved_data = result[0]
        result = list(appointment.find({"doctor_phone_id": retrieved_data['doctor_phone_id'], "date_of_appointment":date,"amount":{"$gt": -1}}, {"_id": 0}))  # Convert cursor to list
        data_length = 1
        if result:
            data_length = len(result)+1

        xdate = date
        date_obj = datetime.strptime(xdate, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%Y%m%d")

        pay_id = str(retrieved_data['pay_id'])
        pay_id = "old_"+pay_id

        appoint_number = str(formatted_date)+'-'+str(data_length)

        appointment.insert_one({**dataset,'status':'success','pay_id':pay_id,'appoint_number':appoint_number,'amount':0})

        name = str(retrieved_data['patient_name'])
        phone = str(retrieved_data['whatsapp_number'])

        return success_appointment(pay_id,appoint_number,name,date,slot,phone)
    else:
        id = str(appointment.insert_one(dataset).inserted_id)
        print(id)
        link = pay_link(name,from_number,'ajeetindrajeet@gmail.com',id,200)
        print(link)
        amount = 200
        return send_payment_flow(from_number,name,date,slot,amount,link)


def custom_appointment_flow(from_number):

    external_url = "https://graph.facebook.com/v22.0/606444145880553/messages"  # Example API URL

    incoming_data = { 
    "messaging_product": "whatsapp", 
    "to": from_number, 
    "type": "template", 
    "template": { 
        "name": "clone_appointment_flow", 
        "language": { "code": "en" },
        "components": [
            {
                "type": "header"
            },
            {
                "type": "body",
                "parameters": []
            },
            {
                "type": "button",
                "sub_type": "flow",  
                "index": "0"  
            }
        ]
    } 
}

    response = requests.post(external_url, json=incoming_data, headers=headers)
    print(response)
    return "OK", 200


def appointment_flow(from_number):

    external_url = "https://graph.facebook.com/v22.0/606444145880553/messages"  # Example API URL

    incoming_data = { 
    "messaging_product": "whatsapp", 
    "to": from_number, 
    "type": "template", 
    "template": { 
        "name": "flowappoint", 
        "language": { "code": "en" },
        "components": [
            {
                "type": "header"
            },
            {
                "type": "body",
                "parameters": []
            },
            {
                "type": "button",
                "sub_type": "flow",  
                "index": "0"  
            }
        ]
    } 
}

    response = requests.post(external_url, json=incoming_data, headers=headers)
    print(jsonify(response.json()))
    return "OK", 200

def call_external_post_api(from_number):

    last_object = appointment.find_one({"whatsapp_number": from_number}, sort=[("_id", -1)])
    # last_object = False

    print(last_object)

    if last_object:
        name = last_object['patient_name']
        print(name)
        return start_automation(from_number)
    else:
        external_url = "https://graph.facebook.com/v22.0/606444145880553/messages"  # Example API URL

        incoming_data = { 
    "messaging_product": "whatsapp", 
    "to": from_number, 
    "type": "template", 
    "template": { 
        "name": "flowappoint", 
        "language": { "code": "en" },
        "components": [
            {
                "type": "header"
            },
            {
                "type": "body",
                "parameters": []
            },
            {
                "type": "button",
                "sub_type": "flow",  
                "index": "0"  
            }
        ]
    } 
}

        response = requests.post(external_url, json=incoming_data, headers=headers)
        print(jsonify(response.json()))
        return "OK", 200
    

def start_automation(from_number):
    external_url = "https://graph.facebook.com/v22.0/606444145880553/messages"  # Example API URL

    all_buttons = [
    {"id": "book_appointment", "title": "📅 Book Appointment"},
    {"id": "lab_tests", "title": "🧪 Book Lab Test"},
    {"id": "buy_medicine", "title": "💊 Buy Medicine"}
    ]

# Function to send buttons in batches of 3
    def send_whatsapp_buttons(to_number, buttons_list):
        for i in range(0, len(buttons_list), 3):  # Send in groups of 3
            buttons = buttons_list[i:i+3]  # Get 3 buttons at a time

            payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Please select an option:"},
                "action": {
                    "buttons": [{"type": "reply", "reply": btn} for btn in buttons]
                }
            }
        }

            response = requests.post(external_url, headers=headers, json=payload)
       
         

# Send multiple messages with 3 buttons per message
    send_whatsapp_buttons(from_number, all_buttons)

    # response = requests.post(external_url, json=payloadx, headers={'Authorization': 'Bearer EAAJdr829Xj4BOxyhp8MzkQqZCr92HwzYQMyDjZBhWZBqUej9YnYqTBefwyGeIZAUOhSk3y9AspLT69frxyYsWb6ea7jAGP4xm3BCxkAF5SXMqLeY3SpYt5AUUi0CkUIhk8AC6S1H6TIr0RLQHf3Tfo6ZBblcMZCBoc81nqVTidywfSK4FoWZAZCXenHHqRr5wAtE5D2tIGf87f8B7wuXUcWyK77Wca1ZBR3tqxQMOkK6L6BUZD','Content-Type': 'application/json'})
    # print(jsonify(response.json()))
    return "OK", 200



def success_appointment(payment_id,appoint_no,name,doa,time,whatsapp_no):
    url = f"https://graph.facebook.com/v22.0/606444145880553/messages"


    payload = { 
        "messaging_product": "whatsapp", 
        "to": whatsapp_no, "type": "template", 
        "template": { 
            "name": "success_book", 
            "language": { 
                "code": "en" 
            },
            "components": [
                {
                    "type": "header",
                    "parameters":  [{
            "type": "location",
            'location': {
          'latitude': 37.7749, 
          'longitude': -122.4194, 
          'name': "San Francisco",
          'address': "California, USA"
        }
          }]

                },
                 {
        "type": "body",
        "parameters": [ {
                    "type": "text",
                    "text": name
                }, {
                    "type": "text",
                    "text": appoint_no
                }, {
                    "type": "text",
                    "text": doa
                }, {
                    "type": "text",
                    "text": time
                },
          {
                    "type": "text",
                    "text": payment_id
                }
        ]
      }

            ]} 
        }

    response = requests.post(url, json=payload, headers=headers)
    return f"whatsapp://send?phone=+15551790637"




def old_user_send(from_number):
    external_url = "https://graph.facebook.com/v22.0/606444145880553/messages"  # Example API URL

    result = list(appointment.find({"whatsapp_number": from_number}))
# Store only the latest appointment per patient
    unique_patients = {}
    latest_appointments = []

    for record in result:
        patient_name = record.get("patient_name")
        display_name = (patient_name[:15] + "...") if len(patient_name) > 10 else patient_name
        if patient_name and patient_name not in unique_patients:
            unique_patients[patient_name] = True
        
            latest_appointments.append({
            "id": "appoint_id"+str(record["_id"]) if "_id" in record else "",  # Handle missing _id
            "title": display_name
                })

    all_buttons = latest_appointments + [{"id": "book_appointment", "title": "Book Appointment"}]

# Function to send buttons in batches of 3
    def send_whatsapp_buttons(to_number, buttons_list):
        # for i in range(0, len(buttons_list), 3): 
            # buttons = buttons_list[i:i+3] 

            last_three_buttons = buttons_list[-3:]

            payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "Please select an option:"},
                "action": {
                    "buttons": [{"type": "reply", "reply": btn} for btn in last_three_buttons]
                }
            }
        }

            response = requests.post(external_url, headers=headers, json=payload)
       
         

# Send multiple messages with 3 buttons per message
    send_whatsapp_buttons(from_number, all_buttons)

    # response = requests.post(external_url, json=payloadx, headers={'Authorization': 'Bearer EAAJdr829Xj4BOxyhp8MzkQqZCr92HwzYQMyDjZBhWZBqUej9YnYqTBefwyGeIZAUOhSk3y9AspLT69frxyYsWb6ea7jAGP4xm3BCxkAF5SXMqLeY3SpYt5AUUi0CkUIhk8AC6S1H6TIr0RLQHf3Tfo6ZBblcMZCBoc81nqVTidywfSK4FoWZAZCXenHHqRr5wAtE5D2tIGf87f8B7wuXUcWyK77Wca1ZBR3tqxQMOkK6L6BUZD','Content-Type': 'application/json'})
    # print(jsonify(response.json()))
    return "OK", 200


