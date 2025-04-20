import requests
import json
import re
def pay_link(name,number,email,id,rs,rzid,rzk):

# Razorpay API Credentials
    RAZORPAY_KEY_ID = rzid
    RAZORPAY_KEY_SECRET = rzk

# API URL
    url = "https://api.razorpay.com/v1/payment_links"

# Payment Data
    data = {
    "amount": rs*100,  # Amount in paise (₹20)
    "currency": "INR",
    "description": "Payment for service",
    "customer": {
        "name": name,
        # "email": 'test@gmail.vom',
        "contact": number
    },
    "notify": {
        "sms": False,
        "email": False
    },
    "callback_url": "https://care2connect.in/payment_callback2/"+id+"/",
    "callback_method": "get"
}

# Send Request
    response = requests.post(url, auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET), json=data)

# Print Response
    payment_data = json.loads(response.text)
    short_url = payment_data.get("short_url")
    print(short_url)
    match = re.search(r"/rzp/([\w\d]+)", short_url)
    if match:
        payment_id = match.group(1)
        return payment_id
    else:
        return 'x'