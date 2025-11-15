import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

# -------------------------
# Price formatting
# -------------------------
def format_price(amount):
    if not amount:
        return ""
    amount = float(amount)
    if amount >= 10000000:
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.2f} Lac"
    elif amount >= 1000:
        return f"₹{amount/1000:.0f}K"
    else:
        return f"₹{amount:.0f}"

# -------------------------
# Email utilities
# -------------------------
def send_notification_email(user, subject, message):
    if not user.email:
        return
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def send_admin_email(subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.EMAIL_HOST_USER],
        fail_silently=False,
    )

# -------------------------
# OTP utilities

