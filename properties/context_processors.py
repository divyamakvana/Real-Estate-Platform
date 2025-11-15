from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, read=False).count()
        unread_notifications = Notification.objects.filter(user=request.user, read=False).order_by('-created_at')[:5]
    else:
        unread_notifications = []
        unread_count = 0
    return {
        "unread_notifications": unread_notifications,
        "unread_count": unread_count,
    }
