from fpdf import FPDF
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests

MONGO_URI = "mongodb+srv://care2connect:connect0011@cluster0.gjjanvi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("caredb")
doctors = db["doctors"] 
appointment = db["appointment"] 
templog = db["logs"] 


def receiptme(from_number):

    document = templog.find_one({'_id':from_number})
    appoint_data = appointment.find_one({"_id": ObjectId(document["current_id"])})

    print(appoint_data)

    name = appoint_data.get('patient_name')
    doa = appoint_data.get('date_of_appointment')
    time = appoint_data.get('time_slot')
    no = str(appoint_data.get('appointment_index'))

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(25, 42, 86)  # RGB for dark blue
            self.rect(0, 0, 210, 55, 'F')    # Full-width rectangle for header

            # Add logo on the top left corner
            self.image("icon.png", 10, 10, 25)  # (file, x, y, width)

            # Move to the right of the logo for text
            self.set_xy(40, 15)  # X=40 to move right of logo, Y=15 for vertical centering
            self.set_font("Arial", "B", 16)
            self.set_text_color(255, 255, 255)  # White text
            self.cell(0, 10, "Care2Connect", ln=True, align="L")
            self.ln(5)

        def add_appointment_details(self):
            # RED BACKGROUND SECTION ABOVE APPOINTMENT DETAILS
            self.set_fill_color(25, 42, 86) 
            self.set_text_color(255, 255, 255)  # White text
            # self.rect(0, 0, 210, 125, 'F') 
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Your appointment is confirmed", ln=True, fill=True)

            self.set_font("Arial", "", 12)
            self.cell(0, 10, "This appointment is guaranteed by Care2Connect", ln=True, fill=True)
            self.ln(10)

            # Appointment intro
            self.set_text_color(0, 0, 0)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, "Hello "+name+" ,", ln=True)
            self.ln(5)
            self.multi_cell(0, 10, "Thanks for booking an appointment on Care2Connect. Here are the details of your appointment:")
            self.ln(5)

            # Appointment details table
            self.set_font("Arial", "B", 12)
            self.cell(50, 10, "Doctor's name:", 1)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, "Dr. Neeraj Bansal", 1, ln=True)

            self.set_font("Arial", "B", 12)
            self.cell(50, 10, "Date:", 1)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, doa, 1, ln=True)

            self.set_font("Arial", "B", 12)
            self.cell(50, 10, "Time:", 1)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, time, 1, ln=True)

            self.set_font("Arial", "B", 12)
            self.cell(50, 10, "Clinic's details:", 1)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, "Dr. Neeraj Bansal Child Care Centre, Bathinda", 1, ln=True)

            self.set_font("Arial", "B", 12)
            self.cell(50, 10, "Phone:", 1)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, from_number, 1, ln=True)

            self.set_font("Arial", "B", 12)
            self.cell(50, 10, "Appointment No:", 1)
            self.set_font("Arial", "", 12)
            self.cell(0, 10, no, 1, ln=True)

            self.ln(10)
            self.set_font("Arial", "", 12)
            self.multi_cell(0, 10, "If you are unable to make it to the appointment, please cancel or reschedule. It will open this valuable slot for others waiting to visit the doctor.")
            self.ln(5)

            self.set_text_color(0, 150, 255)
            self.cell(0, 10, "Manage your appointments better by visiting My Appointments", ln=True)

    # Generate and save the PDF
    pdf = PDF()
    pdf.add_page()
    pdf.add_appointment_details()
    pdf.output("receipt.pdf")

    try:
        WHATSAPP_ACCESS_TOKEN = "EACHqNPEWKbkBOZBGDB1NEzQyDEsZAUcJwBMdopvDDWrS9JNRsWe1YAHc6C5k4pCQlJvScAX7URYSFE4wvMXlh7x9Uf6fwbccvQqceRxHxJFJLZC7szcNaSZCr9pJWE8g5S8SZCaNxRbMZA6dQNZBVaQzBtZBQJ4TNZAoZBuyZBjyVJDOOSKmSSsdqhFRKLUS6fm28zwKA7GhNsclSZAJtjQWTBWfzw5bOS2Fp53qqujNwm9f"
        PDF_FILE_PATH = 'receipt.pdf'

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
        "caption": "Here is your Receipt"
    }
    }

# Sending request
        response = requests.post(url, headers=headers, json=data)
# Print response
        print(response.status_code, response.json())

        return "ok",200
    except Exception as e:
        return e,400
