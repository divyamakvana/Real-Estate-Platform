# properties/notifications.py
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification  

def create_notification(user, message, link=None, send_email=True, email_subject=None, email_body=None):
    """
    Create a DB notification and optionally send an email to the user.
    """
    # Save notification in DB
    Notification.objects.create(user=user, message=message)

    # Optionally send email
    if send_email and user.email:
        subject = email_subject or (message[:60] + "...")
        body = email_body or message
        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception:
            pass
