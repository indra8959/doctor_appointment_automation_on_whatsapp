import requests
import json
import re
import time
from threading import Thread

def expire_payment_link(payment_link_id, rzid, rzk):
    """Expires a Razorpay payment link by sending a POST to /cancel."""
    url = f"https://api.razorpay.com/v1/payment_links/{payment_link_id}/cancel"
    auth = (rzid, rzk)
    
    # Wait for 5 minutes (300 seconds)
    time.sleep(300)

    response = requests.post(url, auth=auth)

    if response.status_code == 200:
        print("Payment link expired successfully.")
    else:
        print("Failed to expire payment link:", response.text)


def pay_link(name, number, email, id, rs, rzid, rzk):
    """
    Creates a Razorpay payment link and schedules it to expire after 5 minutes.
    Returns the payment ID or 'x' if failed.
    """
    # Razorpay API URL
    url = "https://api.razorpay.com/v1/payment_links"

    # Payment Data
    data = {
        "amount": int(rs * 100),  # Convert to paise
        "currency": "INR",
        "description": "Payment for service",
        "customer": {
            "name": name,
            # "email": email,
            "contact": number
        },
        "notify": {
            "sms": False,
            "email": False
        },
        "callback_url": f"https://care2connect.in/payment_callback2/{id}/",
        "callback_method": "get"
    }

    # Send Request
    response = requests.post(url, auth=(rzid, rzk), json=data)

    if response.status_code == 200:
        payment_data = response.json()
        short_url = payment_data.get("short_url")
        payment_link_id = payment_data.get("id")

        print("Payment Link Created:", short_url)

        # Start a background thread to auto-expire the link after 5 minutes
        expiry_thread = Thread(target=expire_payment_link, args=(payment_link_id, rzid, rzk))
        expiry_thread.start()

        # Extract and return payment ID from short_url
        match = re.search(r"/rzp/([\w\d]+)", short_url)
        if match:
            return match.group(1)
    else:
        print("Error creating payment link:", response.text)

    return 'x'