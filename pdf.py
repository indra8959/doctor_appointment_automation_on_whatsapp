import time
from datetime import datetime, timedelta
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pymongo import MongoClient
from bson.objectid import ObjectId
from reportlab.platypus import Spacer

MONGO_URI = "mongodb+srv://care2connect:connect0011@cluster0.gjjanvi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("caredb")
doctors = db["doctors"] 
appointment = db["appointment"] 
templog = db["logs"] 

def pdfdownload(from_number,zxdate):
    
    date_obj = datetime.strptime(zxdate, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%d-%m-%Y")
    
    doc_id = ObjectId("67ee5e1bde4cb48c515073ee")
    document = doctors.find_one({"_id": doc_id})
    xslot = document['slots']['slotsvalue']

    formatted_output = [
                {
                     "id": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+ datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                    "slot": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                    "length": item["maxno"]
                }
                for index, item in enumerate(xslot)
                ]

#     print(formatted_output)






    json_data = list(appointment.find({"amount":{"$gt": -1},"date_of_appointment":zxdate}))

#     print(json_data)

    custom_array = []

    for slot in formatted_output:
        slot_data = [appt for appt in json_data if appt["time_slot"] == slot["slot"]]

        while len(slot_data) < int(slot["length"]):
                slot_data.append({
                     'patient_name': ' ',
                     'appoint_number':' ',
                     'time_slot':slot["slot"],
                     'date_of_birth':' ',
                     'whatsapp_number':' ',
                     'pay_id':' ',
                     'city':' ',
                     'vaccine':' '
                     })
        slot_data.reverse()
    
        custom_array.extend(slot_data)

    print(custom_array)
    json_data = custom_array
    if json_data:

# Convert JSON data to table format
        table_data = [["S.No",
                        # "Appointment No.",
                          "Time Slot", "Name",
                        # "Guardian Name",
                          "Date of Birth", "WhatsApp No.",
                        #   "Payment ID",
                          "City","vaccine","Remark"]]  # Table header

        for i, item in enumerate(json_data, start=1):
                
            table_data.append([
        str(i),  # Serial number
        # item["appoint_number"],
        item["time_slot"],
        item["patient_name"], 
        # item["guardian_name"],
        item["date_of_birth"], 
        item["whatsapp_number"], 
        # item["pay_id"], 
        item["city"],
        item["vaccine"],
        "        ",
        ])
# Create a PDF file
        pdf_filename = "output_table.pdf"
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)


# Create table
        table = Table(table_data)

# Add style to the table
        style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),  # Set font size to 12px
    ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        print_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        table.setStyle(style)

        print_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        styles = getSampleStyleSheet()
        header_left = Paragraph(f"<b>date of appointments: {formatted_date}</b>", ParagraphStyle(name="LeftHeader", fontSize=10))
        header_right = Paragraph(f"<i>Printed on: {print_date}</i>", ParagraphStyle(name="RightHeader", fontSize=10, alignment=2))
        header_table = Table([[header_left, header_right]], colWidths=[300, 240])  # Adjust if needed

        pdf.build([header_table, Spacer(1, 10), table])

  
    


        WHATSAPP_ACCESS_TOKEN = "EACHqNPEWKbkBOZBGDB1NEzQyDEsZAUcJwBMdopvDDWrS9JNRsWe1YAHc6C5k4pCQlJvScAX7URYSFE4wvMXlh7x9Uf6fwbccvQqceRxHxJFJLZC7szcNaSZCr9pJWE8g5S8SZCaNxRbMZA6dQNZBVaQzBtZBQJ4TNZAoZBuyZBjyVJDOOSKmSSsdqhFRKLUS6fm28zwKA7GhNsclSZAJtjQWTBWfzw5bOS2Fp53qqujNwm9f"
        PDF_FILE_PATH = pdf_filename

        PHONE_NUMBER_ID = "563776386825270"


# API endpoint for media upload
        upload_url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/media"

# Headers
        headers = {
    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"
    }

# File upload
        files = {
        "file": (PDF_FILE_PATH, open(PDF_FILE_PATH, "rb"), "application/pdf"),
        "type": (None, "application/pdf"),
        "messaging_product": (None, "whatsapp")
        }

        response = requests.post(upload_url, headers=headers, files=files)

        print(response)

# Print response
        print(response.json()['id'])


        RECIPIENT_NUMBER = from_number  # Format: "91xxxxxxxxxx"
        PDF_FILE_ID = response.json()['id']  # Extracted from your provided data

# API endpoint
        url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

# Headers
        headers = {
    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
    "Content-Type": "application/json"
    }

# Message payload
        data = {
    "messaging_product": "whatsapp",
    "to": RECIPIENT_NUMBER,
    "type": "document",
    "document": {
        "id": PDF_FILE_ID,  # Reference to the uploaded PDF file
        "caption": "Here is your PDF file."
    }
    }

# Sending request
        response = requests.post(url, headers=headers, json=data)
# Print response
        print(response.status_code, response.json())

        return "ok",200
    else:
        return "ok",200







def pdfdownloadcdate(from_number):
    
    zxdate = datetime.now().strftime("%Y-%m-%d")
    
    doc_id = ObjectId("67ee5e1bde4cb48c515073ee")
    document = doctors.find_one({"_id": doc_id})
    xslot = document['slots']['slotsvalue']

    formatted_output = [
                {
                     "id": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+ datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                    "slot": datetime.strptime(item["slot"]["stime"], "%H:%M").strftime("%I:%M %p")+" - "+datetime.strptime(item["slot"]["etime"], "%H:%M").strftime("%I:%M %p"),
                    "length": item["maxno"]
                }
                for index, item in enumerate(xslot)
                ]

#     print(formatted_output)






    json_data = list(appointment.find({"amount":{"$gt": -1},"date_of_appointment":zxdate}))

#     print(json_data)

    custom_array = []

    for slot in formatted_output:
        slot_data = [appt for appt in json_data if appt["time_slot"] == slot["slot"]]
    
        while len(slot_data) < int(slot["length"]):
                slot_data.append({
                     'patient_name': ' ',
                     'appoint_number':' ',
                     'time_slot':slot["slot"],
                     'age':' ',
                     'whatsapp_number':' ',
                     'pay_id':' ',
                     'city':' ',
                     'vaccine':' '
                     })
        slot_data.reverse()
    
        custom_array.extend(slot_data)

    print(custom_array)
    json_data = custom_array
    if json_data:

# Convert JSON data to table format
        table_data = [["S.No",
                        # "Appointment No.",
                          "Time Slot", "Name",
                        # "Guardian Name",
                          "Age", "WhatsApp No.","Payment ID","City","vaccine","Remark"]]  # Table header

        for i, item in enumerate(json_data, start=1):
                
            table_data.append([
        str(i),  # Serial number
        item["appoint_number"],
        # item["time_slot"],
        item["patient_name"], 
        # item["guardian_name"],
        item["age"], 
        item["whatsapp_number"], 
        item["pay_id"], 
        item["city"],
        item["vaccine"],
        "        ",
        ])
# Create a PDF file
        pdf_filename = "output_table.pdf"
        pdf = SimpleDocTemplate(pdf_filename, pagesize=letter)


# Create table
        table = Table(table_data)

# Add style to the table
        style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),  # Set font size to 12px
    ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        print_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        table.setStyle(style)

        styles = getSampleStyleSheet()
        header_style = ParagraphStyle(name="HeaderStyle", fontSize=10, leading=14, spaceAfter=10)
        header = Paragraph(f"<b>date of appointments: </b><br/><i>Printed on: {print_date}</i>", header_style)


        pdf.build([header, table])

  
    


        WHATSAPP_ACCESS_TOKEN = "EACHqNPEWKbkBOZBGDB1NEzQyDEsZAUcJwBMdopvDDWrS9JNRsWe1YAHc6C5k4pCQlJvScAX7URYSFE4wvMXlh7x9Uf6fwbccvQqceRxHxJFJLZC7szcNaSZCr9pJWE8g5S8SZCaNxRbMZA6dQNZBVaQzBtZBQJ4TNZAoZBuyZBjyVJDOOSKmSSsdqhFRKLUS6fm28zwKA7GhNsclSZAJtjQWTBWfzw5bOS2Fp53qqujNwm9f"
        PDF_FILE_PATH = pdf_filename

        PHONE_NUMBER_ID = "563776386825270"


# API endpoint for media upload
        upload_url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/media"

# Headers
        headers = {
    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"
    }

# File upload
        files = {
        "file": (PDF_FILE_PATH, open(PDF_FILE_PATH, "rb"), "application/pdf"),
        "type": (None, "application/pdf"),
        "messaging_product": (None, "whatsapp")
        }

        response = requests.post(upload_url, headers=headers, files=files)

        print(response)

# Print response
        print(response.json()['id'])


        RECIPIENT_NUMBER = from_number  # Format: "91xxxxxxxxxx"
        PDF_FILE_ID = response.json()['id']  # Extracted from your provided data

# API endpoint
        url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

# Headers
        headers = {
    "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
    "Content-Type": "application/json"
    }

# Message payload
        data = {
    "messaging_product": "whatsapp",
    "to": RECIPIENT_NUMBER,
    "type": "document",
    "document": {
        "id": PDF_FILE_ID,  # Reference to the uploaded PDF file
        "caption": "Here is your PDF file."
    }
    }

# Sending request
        response = requests.post(url, headers=headers, json=data)
# Print response
        print(response.status_code, response.json())

        return "ok",200
    else:
        return "ok",200


