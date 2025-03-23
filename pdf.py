import time
from datetime import datetime, timedelta
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://indrajeet:indu0011@cluster0.qstxp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("medicruise")
doctors = db["doctors"] 
appointment = db["appointment"] 
templog = db["logs"] 

def pdfdownload(from_number):


    json_data = list(appointment.find({"amount":{"$gt": -1}}))

    print(json_data)

    
    if json_data:

# Convert JSON data to table format
        table_data = [["S.No", "Appointment No.", "Time Slot", "Name",
                        # "Guardian Name",
                          "Age", "WhatsApp No.","Payment ID","City","Remark"]]  # Table header

        for i, item in enumerate(json_data, start=1):  # Loop through dictionary values with index
            table_data.append([
        str(i),  # Serial number
        item["appoint_number"],
        item["time_slot"],
        item["patient_name"], 
        # item["guardian_name"],
        item["age"], 
        item["whatsapp_number"], 
        item["pay_id"], 
        item["city"],
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
        header = Paragraph(f"<b>Appointment Report</b><br/><i>Printed on: {print_date}</i>", header_style)

# Build PDF with header and table
        pdf.build([header, table])

        WHATSAPP_ACCESS_TOKEN = "EAAJdr829Xj4BO4B15MZAqnCnRp9PprXQP6AOlfw5gtYwVLdrKlSjwXta4o3wkkYalMVOZAARNRIVk7evjoiQg9cY7NfQzFqqXZCv7OQMbxgeQVkDBqnPZA1PcWWGZBN6AXNBrcqGXIINacmAwycthHMsh479FqVjkTWHPgZBrBlfXO93O0DZBOn1aB57vRZB1f0PNAZDZD"
        PDF_FILE_PATH = pdf_filename

        PHONE_NUMBER_ID = "606444145880553"


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

        return 2
    else:
        return 1

