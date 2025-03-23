

import time
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from pymongo import MongoClient
from collections import Counter

MONGO_URI = "mongodb+srv://indrajeet:indu0011@cluster0.qstxp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("medicruise")
doctors = db["doctors"] 
appointment = db["appointment"] 
templog = db["logs"] 


def dateandtime(id):
        if id == 'date':
            doc_id = ObjectId("67dd57c9f7318c29e5d54853")
            document = doctors.find_one({"_id": doc_id})
            datas = document

            def get_next_7_days():
                today = datetime.today()
                dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(8)]
                return dates

            disabled_dates = get_next_7_days()

            data = datas['date']['disabledate']
            data_names = {item["name"] for item in data}
            formatted_output = [
                {"id": date, "title": date, "enabled": False} if date in data_names else {"id": date, "title": date}
                for date in disabled_dates
                ]
    
            current_time = datetime.now().time()

            cutoff_time = datetime.strptime("08:00AM", "%I:%M%p").time()

            print(cutoff_time)

            is_before_8am = current_time < cutoff_time

            if not is_before_8am and data:
                formatted_output.pop(0)
            

            return formatted_output

        else:


            doc_id = ObjectId("67dd57c9f7318c29e5d54853")
            document = doctors.find_one({"_id": doc_id})
            datas = document


            appoint = list(appointment.find({"doctor_phone_id": "12345", "date_of_appointment":id,"amount":{"$gt": -1}}, {"_id": 0}))
            
            if appoint:

                time_slots = [entry['time_slot'] for entry in appoint]

                time_counts = Counter(time_slots)

# Convert to required format
                result = [{"time": time, "number": count} for time, count in time_counts.items()]

                xslot = datas['slots']['slotsvalue']

                formatted_output = [
                {
                    "id": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+ datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                    "title": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                    "maxno": item["maxno"]
                }
                for index, item in enumerate(xslot)
                ]

                arry1 = result
                arry2 = formatted_output

# Convert arry1 into a dictionary for quick lookup
                time_counts = {item['time']: item['number'] for item in arry1}

# Process and apply conditions
                result = [
                {
                "id": item['id'],
                "title": item['title'],
                "enabled": False if time_counts.get(item['title'], 0) >= int(item['maxno']) else True
                }
                for item in arry2
                ]

# Remove "enabled": True for cleaner output
                for obj in result:
                    if obj["enabled"]:
                        del obj["enabled"]

                return result
            else:
                xslot = datas['slots']['slotsvalue']

                formatted_output = [
                {
                     "id": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+ datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                    "title": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                }
                for index, item in enumerate(xslot)
                ]

            
                return formatted_output







