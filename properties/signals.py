from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Property
from .utils import send_notification_email

@receiver(post_save, sender=Property)
def notify_user_on_property_status_change(sender, instance, created, **kwargs):
    """
    Notify property owner when their property is approved or rejected.
    """
    if not created:  # only trigger on updates
        if instance.status == "approved":
            send_notification_email(
                instance.owner,
                subject="Your property has been approved 🎉",
                message=f"""
                Hi {instance.owner.username},

                Good news! 🎉 Your property "{instance.property_type}" in {instance.locality}
                has been approved and is now live on RealEstate.com.

                Buyers can now view and contact you regarding this listing.

                Regards,  
                RealEstate Team
                """
            )

        elif instance.status == "rejected":
            send_notification_email(
                instance.owner,
                subject="Your property has been rejected ❌",
                message=f"""
                Hi {instance.owner.username},

                Unfortunately, your property "{instance.property_type}" in {instance.locality}
                has been rejected by our team.

                Please review our guidelines and resubmit with correct details.

                Regards,  
                RealEstate Team
                """
            )
