from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Contact,Property , Testimonials,UserProfile,City,PropertyImage,Shortlist, Inquiry,Feature, LocalityFeedback,Locality,Recentviewed,Notification,Article,OTP
from django.db.models import Q, Count , Avg
from .models import FAQPage
from django.contrib import messages
from django.contrib.auth.models import User 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from .utils import send_notification_email , send_admin_email  # ✅ import email utility
from django.core.paginator import Paginator
from .notifications import create_notification
from django.db.models.functions import TruncMonth
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
# from .ml_utils import predict_property_price


import pandas as pd
import joblib
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.tokens import default_token_generator


from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

import logging
from django.db import transaction
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string
import re
# Create your views here.

logger = logging.getLogger(__name__)
def home(request):
    return render(request, 'home.html')

# admin dashboard start here 
def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

admin_required = user_passes_test(is_admin, login_url='admin_login')

# Only allow superusers
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@user_passes_test(lambda u: u.is_superuser)
def create_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_superuser = request.POST.get("is_superuser") == "on"

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=is_superuser
            )
            messages.success(request, f"Admin '{username}' created successfully!")
            return redirect("superuser_dashboard")

    return render(request, "properties/admin/create_admin.html")

@superuser_required
def manage_admins(request):
    admins = User.objects.filter(is_staff=True)
    return render(request, "properties/admin/manage_admins.html", {"admins": admins})



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser:
                return redirect("superuser_dashboard")
            elif user.is_staff:
                return redirect("admin_dashboard")
            else:
                messages.error(request, "You do not have access.")
                logout(request)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "properties/admin/admin_login.html")

@admin_required
def admin_dashboard(request):
    # ---- KPI Stats ----
    total_user = User.objects.count()
    total_properties = Property.objects.count()
    
    pending_users = UserProfile.objects.filter(status='pending').count()
    pending_properties = Property.objects.filter(status='pending').count()
    pending_approvals = pending_users + pending_properties

    # ---- User Growth (last 6 months) ----
    user_growth = (
        User.objects.annotate(month=TruncMonth("date_joined"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    user_growth_months = [u["month"].strftime("%b %Y") for u in user_growth]
    user_growth_data = [u["count"] for u in user_growth]

    # ---- Enquiries per Month (last 6 months) ----
    enquiry_growth = (
        Inquiry.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    enquiry_months = [e["month"].strftime("%b %Y") for e in enquiry_growth]
    enquiry_counts = [e["count"] for e in enquiry_growth]

    # ---- Recent activity ----
    recent_properties = Property.objects.order_by("-posted_on")[:5]
    recent_enquiries = Inquiry.objects.order_by("-created_at")[:5]

    return render(request, "properties/admin/admin_dashboard.html", {
        # KPI
        "total_user": total_user,
        "total_properties": total_properties,
        "pending_approvals": pending_approvals,
        "pending_users": pending_users,
        "pending_properties": pending_properties,

        # Chart Data (must be JSON for Chart.js)
        "user_growth_months": json.dumps(user_growth_months),
        "user_growth_data": json.dumps(user_growth_data),
        "enquiry_months": json.dumps(enquiry_months),
        "enquiry_counts": json.dumps(enquiry_counts),

        # Recent
        "recent_properties": recent_properties,
        "recent_enquiries": recent_enquiries,
    })
@user_passes_test(lambda u: u.is_superuser)
def superuser_dashboard(request):
    admins = User.objects.filter(is_staff=True)
    return render(request, "properties/admin/superuser_dashboard.html", {
        "admins": admins
    })


@admin_required
def manage_users(request):
    search_query = request.GET.get("q", "")
    
    # Filter users based on search query
    users = UserProfile.objects.select_related("user").all().order_by("-created_at")
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Pagination: 10 users per page
    paginator = Paginator(users, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "properties/admin/manage_users.html", {
        "users": page_obj,       # pass the paginated object
        "search_query": search_query,
    })

def admin_profile(request):
    user = request.user
    password_form = PasswordChangeForm(user=user)

    if request.method == "POST":
        # Check if password change form is submitted
        if request.POST.get("change_password"):
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep admin logged in
                messages.success(request, "Password changed successfully!")
                return redirect("admin_profile")
            # If invalid, errors will be shown in modal
        else:
            # Profile update form submitted
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.email = request.POST.get("email")
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("admin_profile")

    context = {
        "user": user,
        "password_form": password_form
    }
    return render(request, "properties/admin/admin_profile.html", context)

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login_view")



def admin_forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        users = User.objects.filter(email=email, is_staff=True)
        if users.exists():
            for user in users:
                subject = "Admin Password Reset"
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(
                    f"/custom-admin/reset-password/{uid}/{token}/"
                )
                message = render_to_string('properties/admin/admin_forgot_password_email.html', {
                    'user': user,
                    'reset_link': reset_link
                })
                send_mail(
                    subject,
                    message,
                    'no-reply@yourdomain.com',
                    [user.email],
                    fail_silently=False
                )
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect("login_view")
        else:
            messages.error(request, "No admin found with this email.")
            return redirect("admin_forgot_password")

    return render(request, 'properties/admin/admin_forgot_password.html')


@admin_required
def manage_property(request):
    status_filter = request.GET.get("status", "all")
    search_query = request.GET.get("q", "")

    if status_filter == "pending":
        properties = Property.objects.filter(status="pending")
    elif status_filter == "approved":
        properties = Property.objects.filter(status="approved")
    elif status_filter == "rejected":
        properties = Property.objects.filter(status="rejected")
    else:
        properties = Property.objects.all()

    if search_query:
        properties = properties.filter(
            Q(owner__username__icontains=search_query) |
            Q(locality__name__icontains=search_query) |
            Q(property_type__icontains=search_query) |
            Q(listed_by__icontains=search_query)
        )

    paginator = Paginator(properties, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "properties/admin/manage_property.html", {
        "properties": page_obj,
        "status_filter": status_filter,
        "search_query": search_query
    })



@admin_required
def update_property_status(request, property_id, status):
    prop = get_object_or_404(Property, id=property_id)
    if status in ["approved", "rejected", "pending"]:
        prop.status = status
        prop.save()
    return redirect("manage_property")


def property_detail(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    return render(request, "properties/admin/property_detail.html", {'prop':prop})



@admin_required
def pending_approvals(request):
    # --- Users ---
    user_search_query = request.GET.get("user_q", "")
    user_page_number = request.GET.get("user_page")
    pending_users_qs = UserProfile.objects.filter(status="pending")
    if user_search_query:
        pending_users_qs = pending_users_qs.filter(
            Q(user__username__icontains=user_search_query) |
            Q(role__icontains=user_search_query)
        )
    user_paginator = Paginator(pending_users_qs, 10)
    pending_users = user_paginator.get_page(user_page_number)

    # --- Properties ---
    property_search_query = request.GET.get("prop_q", "")
    prop_page_number = request.GET.get("prop_page")
    pending_properties_qs = Property.objects.filter(status="pending")
    if property_search_query:
        pending_properties_qs = pending_properties_qs.filter(
            Q(owner__username__icontains=property_search_query) |
            Q(property_type__icontains=property_search_query) |
            Q(locality__name__icontains=property_search_query)
        )
    prop_paginator = Paginator(pending_properties_qs, 10)
    pending_properties = prop_paginator.get_page(prop_page_number)

    context = {
        "pending_users": pending_users,
        "user_search_query": user_search_query,
        "pending_properties": pending_properties,
        "property_search_query": property_search_query,
    }

    return render(request, "properties/admin/pending_approvals.html", context)

# Approve/Reject Role
@admin_required
def approve_user_role(request, user_id):
    user_profile = get_object_or_404(UserProfile, user__id=user_id)
    user_profile.status = "approved"
    user_profile.save()
    return redirect('view_user', user_id=user_id)
@admin_required
def reject_user_role(request, user_id):
    user_profile = get_object_or_404(UserProfile, user__id=user_id)
    user_profile.status = "rejected"
    user_profile.save()
    return redirect('view_user', user_id=user_id)


# Activate/Suspend User
@admin_required
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return redirect('view_user', user_id=user.id)
@admin_required
def suspend_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return redirect('view_user', user_id=user.id)



# View User Details
@admin_required
def view_user(request, user_id):
    # Fetch the UserProfile for the given User ID
    user_profile = get_object_or_404(UserProfile, user__id=user_id)

    # Fetch properties listed by this user (optional)
    user_properties = Property.objects.filter(owner=user_profile.user)

    # Pagination: 5 properties per page
    paginator = Paginator(user_properties, 5)
    page_number = request.GET.get("page")
    user_properties = paginator.get_page(page_number)

    return render(request, "properties/admin/view_user.html", {
        "user_profile": user_profile,
        "user_properties": user_properties
    })



@admin_required
def manage_reviews(request):
    search_query = request.GET.get("q", "")

    # Base queryset
    all_reviews = LocalityFeedback.objects.filter(deleted=False).select_related("locality", "user","properties").order_by("-created_at")

    # Apply search filter to both
    if search_query:
        all_reviews = all_reviews.filter(
            Q(locality__name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(comment__icontains=search_query)
        )

    # Split into two lists (approved + all)
    approved_reviews_qs = all_reviews.filter(approved=True)

    # Pagination for all reviews
    page_number = request.GET.get("page")
    paginator_all = Paginator(all_reviews, 5)
    reviews = paginator_all.get_page(page_number)

    # Pagination for approved reviews
    approved_page_number = request.GET.get("approved_page")
    paginator_approved = Paginator(approved_reviews_qs, 5)
    approved_reviews = paginator_approved.get_page(approved_page_number)

    return render(request, "properties/admin/manage_locality_feedback.html", {
        "reviews": reviews,
        "approved_reviews": approved_reviews,
        "search_query": search_query,
    })


@admin_required
def approve_review(request, review_id):
    review = get_object_or_404(LocalityFeedback, id=review_id, deleted=False)
    review.approved = True
    review.save()
        # Notify user
    subject = "Your review has been approved ✅"
    message = f"Hi {review.user.username},\n\nYour review for {review.locality.name} has been approved and is now visible to others."
    send_notification_email(review.user, subject, message)

    messages.success(request, "Review approved successfully.")
    # Notify user if needed
    return redirect('manage_reviews')

@admin_required
def reject_review(request, review_id):
    review = get_object_or_404(LocalityFeedback, id=review_id, deleted=False)
    review.approved = False
    review.save()
    # Notify user
    subject = "Your review has been rejected ❌"
    message = f"Hi {review.user.username},\n\nYour review for {review.locality.name} was rejected by admin."
    send_notification_email(review.user, subject, message)

    messages.success(request, "Review rejected successfully.")
    return redirect('manage_locality_feedback')


@admin_required
def delete_review(request, review_id):
    review = get_object_or_404(LocalityFeedback, id=review_id)
    review.deleted = True
    review.save()
    messages.success(request, "Review deleted.")
    return redirect('manage_locality_feedback')




@admin_required
def manage_enquiries(request):
    search_query = request.GET.get("q", "")

    enquiries = Inquiry.objects.select_related("property", "property__owner", "sender").order_by("-created_at")
    
    if search_query:
        enquiries = enquiries.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(property__property_type__icontains=search_query) |
            Q(property__owner__username__icontains=search_query)
        )

    paginator = Paginator(enquiries, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "properties/admin/manage_enquiries.html", {
        "enquiries": page_obj,
        "search_query": search_query
    })



@admin_required
def view_enquiry(request, enquiry_id):
    enquiry = get_object_or_404(Inquiry.objects.select_related("property", "property__owner", "sender"), id=enquiry_id)

    return render(request, "properties/admin/view_enquiry.html", {
        "enquiry": enquiry
    })


@admin_required
def delete_enquiry(request, enquiry_id):
    enquiry = get_object_or_404(Inquiry, id=enquiry_id)
    enquiry.delete()
    messages.success(request, "Enquiry deleted successfully.")
    return redirect("manage_enquiries")


@admin_required
def remind_owner(request, enquiry_id):
    enquiry = get_object_or_404(Inquiry, id=enquiry_id)

    # Compose email message
    subject = f"Reminder: You have a new inquiry for {enquiry.property.property_type}"
    message = (
        f"Hi {enquiry.property.owner.username},\n\n"
        f"A reminder was sent by admin ({request.user.username}) "
        f"for the inquiry from {enquiry.name}.\n\n"
        f"Message: {enquiry.message}\n\n"
        f"Please reply as soon as possible."
    )

    # Send email
    send_notification_email(enquiry.property.owner, subject, message)

    # Log notification in database
    Notification.objects.create(
        user=enquiry.property.owner,
        message=f"Reminder sent by {request.user.username} for inquiry from {enquiry.name}"
    )

    # Show success message in admin
    messages.success(request, f"Reminder sent to {enquiry.property.owner.username}")

    return redirect('view_enquiry', enquiry_id=enquiry.id)














def index(request):
    recent_property = Property.objects.filter(status='approved').order_by('-posted_on')[:10]
    rent_property = Property.objects.filter(status='approved', deal_type='rent' ,availability='available').order_by('-posted_on')[:10]
    sale_properties = Property.objects.filter(status='approved',deal_type='sale' , availability='available').order_by('-posted_on')[:10]
    cities = City.objects.annotate(property_count=Count('localities__properties'))
    latest_reviews = Testimonials.objects.all().order_by('-created_at')[:4]
    latest_article = Article.objects.all().order_by('-date_created').first()
    latest_images = Article.objects.all().order_by('-date_created')[1:4]  # next 2-3 articles with images
   

    count_1bhk = Property.objects.filter(bhk="1bhk").count()
    count_2bhk = Property.objects.filter(bhk="2bhk").count()
    count_3bhk = Property.objects.filter(bhk="3bhk").count()
    count_4bhk = Property.objects.filter(bhk="4bhk+").count()

    if request.user.is_authenticated:
        user_shortlisted = Shortlist.objects.filter(user=request.user).values_list('property_id', flat=True)
    else:
        user_shortlisted = []
    


    context = {'recent_property':recent_property, 'rent_property':rent_property, 'sale_properties': sale_properties,'latest_reviews':latest_reviews, 'user_shortlisted':list(user_shortlisted), 'cities':cities, 'count_1bhk':count_1bhk, 'count_2bhk':count_2bhk, 'count_3bhk':count_3bhk, 'count_4bhk':count_4bhk,'latest_article': latest_article, 'latest_images':latest_images}
    return render(request, 'properties/index.html', context)










# user views start here


def user_signup(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password1")
        cpassword = request.POST.get("password2")

        errors = []

        # Validate passwords
        if password != cpassword:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        # Check if email is already registered
        if User.objects.filter(username=email).exists():
            errors.append("Email is already registered.")

        # Validate phone number
        if not phone.isdigit() or len(phone) != 10:
            errors.append("Phone must be 10 digits.")

        # If errors exist, return with modal open
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "properties/index.html", {"show_register_modal": True})

        # Create the user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name.split(" ")[0] if full_name else "",
            last_name=" ".join(full_name.split(" ")[1:]) if full_name and len(full_name.split()) > 1 else ""
        )

        # Create profile
        UserProfile.objects.create(user=user, phone=phone, role="buyer")

        # Send welcome email
        try:
            send_mail(
                subject="Welcome to Real Estate Portal",
                message=f"Hi {full_name},\n\nThanks for joining us!\n\n- Real Estate Team",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print("Email sending failed:", e)

        # Auto login
        login(request, user)
        messages.success(request, "Signup successful! Welcome email sent.")

        return redirect("index")  # return to homepage or index

    # GET request just redirects to homepage
    return redirect("index")
# login page 
    

def user_login(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        user = None

        # Login via email
        if "@" in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            # Login via phone (assuming UserProfile model has phone)
            try:
                user_obj = User.objects.get(userprofile__phone=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            messages.success(request, "Login successful!")
        else:
            messages.error(request, "Invalid credentials")
            # Optionally, keep login modal open
            return render(request, "properties/index.html", {"show_login_modal": True})

        return redirect("index")  # redirect after login

    # GET request just redirect to home
    return redirect("index")

# logout

def user_logout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully")
    return render(request, 'properties/index.html')


# views.py


# Send OTP# Send OTP


# Send OTP
def send_login_otp(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        identifier = data.get("identifier")
        try:
            if "@" in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(userprofile__phone=identifier)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"})

        otp_instance = OTP.generate_otp(user)
        send_mail(
            "Your Login OTP",
            f"Hello {user.first_name}, Your OTP is {otp_instance.code}. Valid for 5 minutes.",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )
        return JsonResponse({"success": True})

# Verify OTP
def verify_login_otp(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        identifier = data.get("identifier")
        otp_input = data.get("otp")

        try:
            if "@" in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(userprofile__phone=identifier)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"})

        if OTP.verify_otp(user, otp_input):
            login(request, user)
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "Invalid or expired OTP"})



# user profile
def user_profile(request):
    # profile = UserProfile.objects.get(user=request.user)
    return render(request, "properties/client/profile.html", {"user": request.user})
    # return render(request, "properties/client/profile.html", {"profile": profile})


@login_required
def update_profile(request):
    user = request.user
    profile = user.profile  # OneToOne relation

    if request.method == "POST":
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        agree = request.POST.get('agree')  # Checkbox value

        # Update user fields
        user.first_name = name
        user.email = email
        user.save()

        # Update profile fields
        profile.phone = phone
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('update_profile')  # Redirect to the same page



    return render(request, 'properties/client/profile.html',{'user':user, 'profile': profile})


def conf_delete_acc(request):
    return render(request, 'properties/client/confirm_delete.html')


from django.utils import timezone


@login_required
def delete_acc(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")  # email or phone
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("delete_acc")

        user = request.user
        profile = user.profile

        # ✅ Check if identifier matches email or phone
        if not (identifier == user.email or identifier == profile.phone):
            messages.error(request, "Email or phone number does not match.")
            return redirect("delete_acc")

        # ✅ Authenticate user
        auth_user = authenticate(username=user.username, password=password)
        if auth_user is None:
            messages.error(request, "Invalid password.")
            return redirect("delete_acc")

        
        try:
            with transaction.atomic():
                # Delete related objects (profile, properties, reviews, etc.)
                profile.delete()
                user.properties.all().delete()   # if related_name="properties"
                user.locality_feedbacks.all().delete()  # if reviews
                user.inquiries.all().delete()    # if enquiries

                # Finally delete user
                user.delete()

            logout(request)
            messages.success(request, "Your account and all related data have been permanently deleted.")
            return redirect("index")
        except Exception as e:
            messages.error(request, f"Error deleting account: {str(e)}")
            return redirect("delete_acc")
    return render(request, "properties/client/delete_acc.html")

        


def city_autocomplete(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse([], safe=False)
    cities = City.objects.filter(name__icontains=q).values("id", "name")[:10]
    return JsonResponse(list(cities), safe=False)

def city_search(request):
    deal_type = request.GET.get("deal_type")       # "sale" or "rent"
    property_type = request.GET.get("property_type")  # "flat", "house", etc.
    city = request.GET.get("city")                 # City name text

    print("DEBUG INPUTS:", deal_type, property_type, city)

    properties = Property.objects.all()

    if deal_type:
        properties = properties.filter(deal_type=deal_type)

    if property_type:
        properties = properties.filter(property_type=property_type)

    if city:
        properties = properties.filter(city__name__icontains=city)

    print("DEBUG QUERY:", properties.query)
    print("DEBUG RESULTS:", properties.count())

    context = {
        "properties": properties,
        "deal": deal_type,
        "property_type": property_type,
        "city_name": city,
    }
    return render(request, "properties/search_results.html", context)



FREE_POST_LIMIT = 2  # number of free posts per user
@login_required
def post_property(request):
    cities = City.objects.all()
    features = Feature.objects.all()
    property = Property.objects.filter(status="approved").order_by("-posted_on")[:3]
    
    show_plan_message = False
   # ----- GET request: check if user already reached limit -----
    if request.method == "GET":
        profile = UserProfile.objects.filter(user=request.user).first()
        free_posts = profile.free_posts_remaining if profile else FREE_POST_LIMIT
        wallet_credits = profile.wallet_credits if profile else 0

        if free_posts <= 0 and wallet_credits <= 0:
            show_plan_message = True  # open modal

        return render(request, "properties/client/post_property.html", {
            "cities": cities,
            "features": features,
            "property": property,
            "show_plan_message": show_plan_message
        })

    if request.method == "POST":
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if created:
            profile.free_posts_remaining = FREE_POST_LIMIT
            profile.wallet_credits = profile.wallet_credits or 0
            profile.save()

        if profile.role in [None, "", "buyer"]:
            profile.role = "owner"
            profile.status = "pending"
            profile.save()

        # ----- Check free posts / wallet credits -----
        if profile.free_posts_remaining <= 0 and profile.wallet_credits <= 0:
            return render(request, "properties/client/post_property.html", {
                "cities": cities,
                "features": features,
                "property": property,
                "show_plan_message": True
            })

        # Deduct free post or wallet credit
        if profile.free_posts_remaining > 0:
            profile.free_posts_remaining -= 1
        else:
            profile.wallet_credits -= 1
        profile.save()
        
        property_type = request.POST.get("property_type")  # must define before using
        locality = Locality.objects.get(id=request.POST.get("locality"))
        # Only assign price if sale, rent_per_month if rent
        deal_type = request.POST.get("deal_type")
        price = request.POST.get("price") if deal_type == "sale" else None
        rent_per_month = request.POST.get("rent_per_month") if deal_type == "rent" else None
        deposit_amount = request.POST.get("deposit_amount") if deal_type == "rent" else None



        data = {
            "owner": request.user,
            "property_type": property_type,
            "deal_type": deal_type,
            "locality": locality,
            "price": price,
            "rent_per_month": rent_per_month,
            "deposit_amount": deposit_amount,
            "desc": request.POST.get("desc"),
            "listed_by": profile.role,
            "availability": "available",
            "status": "pending",
        }

        # Residential fields
        if property_type in ["flat", "house", "apartment", "villa"]:
            data.update({
                "bhk": request.POST.get("bhk") or None,
                "bedrooms": request.POST.get("bedrooms") or None,
                "bathrooms": request.POST.get("bathrooms") or None,
                "furnishing": request.POST.get("furnishing") or "unfurnished",
                "property_age": request.POST.get("property_age") or "new",
                "facing": request.POST.get("facing") or None,
                "floor_number": request.POST.get("floor_number") or None,
                "total_floors": request.POST.get("total_floors") or None,
                "parking": request.POST.get("parking") or 0,
                "area": request.POST.get("area") or None,
                "apartment_name": request.POST.get("apartment_name") or None,
            })

        # Commercial fields
        elif property_type == "commercial":
            data.update({
                "business_type": request.POST.get("business_type") or None,
                "area": request.POST.get("area") or None,
                "floor_number": request.POST.get("floor_number") or None,
                "total_floors": request.POST.get("total_floors") or None,
                "parking": request.POST.get("parking") or 0,
                "seats" : request.POST.get("seats") or 0
            })

        # Land / Plot fields
        elif property_type == "land":
            data.update({
                "plot_area": request.POST.get("plot_area") or None,
                "area_unit": request.POST.get("area_unit") or None,
                "road_access": bool(request.POST.get("road_access")),
                "road_width": request.POST.get("road_width") or None,
                "zoning_type": request.POST.get("zoning_type") or None,
                "ownership_type": request.POST.get("ownership_type") or None,
                "boundary_wall": bool(request.POST.get("boundary_wall")),
                
                "lease_duration": request.POST.get("lease_duration") or None,
            })

        # Create property
        property_obj = Property.objects.create(**data)
        feature_ids = request.POST.getlist("features")
        if feature_ids:
            property_obj.features.set(feature_ids)

        # ✅ Email user
        send_notification_email(
            request.user,
            subject="Property Submission Received",
            message=f"""
            Hi {request.user.username},

            Thank you for submitting your property "{property_obj.property_type}" on RealEstate.com.
            ✅ Your listing is currently under review.
            ⏳ You’ll get another email once it is approved and goes live.

            Regards,
            RealEstate Team
            """
        )

        # ✅ Email admin
        send_admin_email(
            subject="New Property Submitted for Approval",
            message=f"""
            Admin,

            A new property has been submitted for approval.

            Property ID: {property_obj.id}
            Submitted by: {request.user.username} ({request.user.email})

            Please log in to the admin panel to review and approve/reject this listing.
            """
        )

        return redirect("property_submitted")

    return render(request, "properties/client/post_property.html", {
        "cities": cities,
        "features": features,
        "property": property,
        "show_plan_message": False
       
    })


@login_required
def check_post_eligibility(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    free_posts = profile.free_posts_remaining if profile else FREE_POST_LIMIT
    wallet_credits = profile.wallet_credits if profile else 0

    if free_posts <= 0 and wallet_credits <= 0:
        return JsonResponse({"can_post": False})
    return JsonResponse({"can_post": True})







def view_detail(request, id):
    property = get_object_or_404(Property, id=id)

    # Track recently viewed only if logged in
    if request.user.is_authenticated:
        obj, created = Recentviewed.objects.update_or_create(
            user=request.user,
            property=property,
            defaults={"viewed_at": timezone.now()}
        )

        # Keep only last 10 unique views
        recent_qs = Recentviewed.objects.filter(user=request.user).order_by('-viewed_at')
        if recent_qs.count() > 10:
            ids_to_keep = list(recent_qs.values_list("id", flat=True)[:10])
            Recentviewed.objects.filter(user=request.user).exclude(id__in=ids_to_keep).delete()

    # Check shortlist status
    is_shortlisted = False
    if request.user.is_authenticated:
        is_shortlisted = Shortlist.objects.filter(user=request.user, property=property).exists()

    # Locality reviews
    reviews = LocalityFeedback.objects.filter(
        locality=property.locality, approved=True
    ).select_related('user').order_by('-created_at')
    total_reviews = reviews.count()

    # Feature-wise averages
    features = {
        'Connectivity': round(reviews.aggregate(avg=Avg('connectivity'))['avg'] or 0, 1),
        'Safety': round(reviews.aggregate(avg=Avg('safety'))['avg'] or 0, 1),
        'Public Transport': round(reviews.aggregate(avg=Avg('public_transport'))['avg'] or 0, 1),
        'Water Supply': round(reviews.aggregate(avg=Avg('water_supply'))['avg'] or 0, 1),
        'Power Supply': round(reviews.aggregate(avg=Avg('power_supply'))['avg'] or 0, 1),
        'Cleanliness': round(reviews.aggregate(avg=Avg('cleanliness'))['avg'] or 0, 1),
    }

    avg_rating = round(sum(features.values()) / len(features), 1) if total_reviews > 0 else 0

    # Star breakdown
    star_dict = {i: 0 for i in range(1, 6)}
    for r in reviews:
        star = int(round(r.average_rating))
        if 1 <= star <= 5:
            star_dict[star] += 1

    star_percent = {i: round((star_dict[i] / total_reviews) * 100, 1) if total_reviews > 0 else 0 for i in range(1, 6)}

    # Similar properties
    similar_props = Property.objects.filter(
        Q(locality=property.locality) & Q(property_type=property.property_type)
    ).exclude(id=property.id)[:6]

    # Inquiry form
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        buyer_type = request.POST.get("buyerType", "individual")

        if name and phone and message:
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to send an inquiry.")
                return redirect("login")  # redirect to login page

            inquiry = Inquiry.objects.create(
                property=property,
                name=name,
                sender=request.user,
                buyer_type=buyer_type,
                phone=phone,
                message=message
            )

            # Buyer confirmation
            create_notification(
                user=request.user,
                message=f"Your inquiry for '{property.property_type}' has been sent to the owner.",
                email_subject="Inquiry Sent",
                email_body=f"Your inquiry for '{property.property_type}' was successfully sent."
            )

            # Owner notification
            create_notification(
                user=property.owner,
                message=f"{request.user.get_full_name()} sent an inquiry for your property '{property.property_type}'.",
                email_subject="New Property Inquiry",
                email_body=f"You have a new inquiry for '{property.property_type}'."
            )

            messages.success(request, "Your inquiry has been sent successfully!")
            return redirect("view_detail", id=property.id)

        else:
            messages.error(request, "Please fill in all fields.")
            return redirect('view_detail', id=id)

    context = {
        "property": property,
        "is_shortlisted": is_shortlisted,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "features": features,
        "star_dict": star_dict,
        "star_percent": star_percent,
        "total_reviews": total_reviews,
        "similar_props": similar_props
    }
    return render(request, "properties/client/view_detail.html", context)










from .models import City, Locality, LocalityFeedback

@login_required
def add_review(request, property_id=None):
    property_obj = None
    if property_id:
        property_obj = get_object_or_404(Property, id=property_id)
    if request.method == "POST":
        post_property_id = request.POST.get("property_id")
        if post_property_id:
            try:
                property_obj = Property.objects.get(id=post_property_id)
            except Property.DoesNotExist:
                property_obj = None


        email = request.POST.get("email")
        role = request.POST.get("role")
        city_name = request.POST.get("city_name")
        locality_name = request.POST.get("locality_name")
        

        # ratings
        connectivity = int(request.POST.get("connectivity", 0))
        safety = int(request.POST.get("safety", 0))
        public_transport = int(request.POST.get("public_transport", 0))
        water_supply = int(request.POST.get("water_supply", 0))
        power_supply = int(request.POST.get("power_supply", 0))
        cleanliness = int(request.POST.get("cleanliness", 0))

        years_lived = int(request.POST.get("years_lived", 0))
        comment = request.POST.get("comment")

        # city and locality
        city, _ = City.objects.get_or_create(name=city_name)
        locality, _ = Locality.objects.get_or_create(name=locality_name, city=city)

        # save review
        LocalityFeedback.objects.create(
            locality=locality,
            user=request.user,
            properties=property_obj,  # ✅ attach property
            connectivity=connectivity,
            safety=safety,
            public_transport=public_transport,
            water_supply=water_supply,
            power_supply=power_supply,
            cleanliness=cleanliness,
            years_lived=years_lived,
            comment=comment,
            approved=False
        )
        # Notify user
        messages.success(request, "✅ Your review has been submitted successfully and is awaiting admin approval!")

        # Notify admin
        subject = f"New review submitted for {locality.name}"
        message = f"{request.user.username} submitted a review for {locality.name}.\n\nComment: {comment}"
        send_admin_email(subject, message)
        return redirect("index")

    fields = [
        ("connectivity", "Connectivity"),
        ("safety", "Safety"),
        ("public_transport", "Public Transport"),
        ("water_supply", "Water Supply"),
        ("power_supply", "Power Supply"),
        ("cleanliness", "Cleanliness"),
    ]
    return render(request, "properties/client/add_review.html", {"fields": fields, "property": property_obj})



from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import LocalityFeedback, Property

def all_reviews(request, locality_id):
    # Get all reviews for this locality, newest first
    all_review_list = LocalityFeedback.objects.filter(locality_id=locality_id).order_by('-created_at')
    

    # Pagination: 5 reviews per page
    paginator = Paginator(all_review_list, 5)  # Adjust number per page
    page_number = request.GET.get('page')
    all_review = paginator.get_page(page_number)  # Page object

    # Get property from first review (safely)
    property_obj = all_review[0].properties if all_review.object_list else None

    context = {
        'all_review': all_review,
        'property': property_obj,
    }
    return render(request, "properties/client/all_reviews.html", context)



# Aut

# managing property page view
def manage_properties(request):
    property = Property.objects.filter(owner=request.user).order_by('-posted_on')
    return render(request, 'properties/client/manage_properties.html', {'properties':property})


def update_availability(request, id, status):
    if request.method == "POST":
        prop = get_object_or_404(Property, id=id, owner=request.user)
        if status in ["available", "rented", "sold"]:
            prop.availability = status
            prop.save(update_fields=["availability"])
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Invalid status"}, status=400)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def delete_property(request, id):
    if request.method == "POST":
        prop = get_object_or_404(Property, id=id, owner=request.user)
        prop.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@require_POST
@login_required
def toggle_shortlist(request):
    if request.method == 'POST':
        property_id = request.POST.get('property_id')
        try:
            prop = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Property not found'}, status=404)

        obj, created = Shortlist.objects.get_or_create(user=request.user, property=prop)
        if not created:  # already exists → remove it
            obj.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})
    return JsonResponse({'status': 'error'}, status=400)





def activity_page(request):
    tab = request.GET.get('activeTab', 'SHORTLISTED')  # default shortlist
    shortlisted = Shortlist.objects.filter(user=request.user).select_related('property')
    inquiries = Inquiry.objects.filter(sender=request.user).select_related('property', 'property__owner')
    # Owner side: inquiries received on properties listed by this user
    inquiries_received = Inquiry.objects.filter(property__owner=request.user).select_related('property', 'sender')

    recent_views = Recentviewed.objects.filter(user=request.user).select_related("property")[:6] if request.user.is_authenticated else []


    # extract only property objects
    shortlisted_properties = [s.property for s in shortlisted]

     # ✅ Handle reply submission
    if request.method == "POST" and tab == "MANAGE INQUIRY":
        inquiry_id = request.POST.get("inquiry_id")
        reply_message = request.POST.get("reply_message")

        if inquiry_id and reply_message:
            inquiry = get_object_or_404(Inquiry, id=inquiry_id, property__owner=request.user)
            inquiry.reply_message = reply_message
            inquiry.owner_replied = True
            inquiry.replied_at = timezone.now()
            inquiry.save()

            # 1️⃣ Notify buyer in-app
            buyer = inquiry.sender
            if buyer:  # only if sender is a registered user
                create_notification(
                user=buyer,
                message=f"The owner of '{inquiry.property.property_type}' replied to your inquiry.",
                email_subject="Property Owner Replied",
                email_body=f"The owner of '{inquiry.property.property_type}' has replied:\n\n{reply_message}"
                )

            messages.success(request, "Reply sent successfully!")
            return redirect(f"{request.path}?activeTab=MANAGE INQUIRY")

    context = {
        "active_tab": tab,
        "shortlisted_properties": shortlisted_properties,
        "inquiries" : inquiries,
        "inquiries_received": inquiries_received,
           "recent_views": recent_views,
    }
    return render(request, "properties/client/activity_page.html", context)



# modal for explore via city



# defferent tool view
def emi_calc(request):
    return render(request, 'properties/tools/emi_calc.html')


def budget_calc(request):
    return render(request, 'properties/tools/budget_calc.html')

def loan_eligibility(request):
    return render(request, 'properties/tools/loan_eligibility.html')

def area_calc(request):
    return render(request, 'properties/tools/area_calc.html')

# local views for testimonials, FAQ, privacypolicy, terms and conditions
def terms(request):
    return render(request, 'properties/terms.html')

def faq(request):
    return render(request, 'properties/FAQ.html' )

def privacypolicy(request):
    return render(request, 'properties/privacy.html')

def testimonials(request):
    reviews = Testimonials.objects.all().order_by('-created_at')
    return render(request, 'properties/testimonials.html', {'reviews':reviews})


# about page
def about(request):
    return render(request, "properties/about.html")


#contact route
def contact(request):
    if request.method == 'POST':
       mail = request.POST.get('mail')
       tel = request.POST.get('tel')
       msg = request.POST.get('msg')
       contact = Contact(mail=mail, tel=tel, msg=msg)
       contact.save()
       messages.success(request, "your Message send Successfully")
       return redirect('contact')
    return render(request, 'properties/contact.html')







def search_properties(request):
    bhk_choices = Property.BHK_CHOICES
    property_types = ["flat", "house", "apartment", "villa", "land"]

    deal_type = request.GET.get('deal_type', '')
    location = request.GET.get('location', '')
    property_type = request.GET.get('property_type', '')
    bhk = request.GET.get('bhk')
    require = request.GET.get('require')
    commercial_purpose = request.GET.get('commercial_purpose')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    qs = Property.objects.filter(is_active=True, status="approved")

    if deal_type:
        qs = qs.filter(deal_type=deal_type)

    # --- Updated location filter ---
    if location:
        if "," in location:
            loc_name, city_name = map(str.strip, location.split(",", 1))
            qs = qs.filter(
                Q(locality__name__icontains=loc_name) &
                Q(locality__city__name__icontains=city_name)
            )
        else:
            qs = qs.filter(
                Q(locality__name__icontains=location) |
                Q(locality__city__name__icontains=location)
            )

    if property_type:
        qs = qs.filter(property_type=property_type)

    if bhk and deal_type in ['sale', 'rent']:
        qs = qs.filter(bhk=bhk)

    if require and deal_type in ['sale', 'rent']:
        qs = qs.filter(require=require)

    if commercial_purpose and deal_type == 'commercial':
        qs = qs.filter(deal_type=commercial_purpose)

    if min_price:
        qs = qs.filter(price__gte=min_price)

    if max_price:
        qs = qs.filter(price__lte=max_price)

    # Shortlist dictionary for logged-in users
    shortlist_dict = {}
    if request.user.is_authenticated:
        user_shortlisted = Shortlist.objects.filter(
            user=request.user, property__in=qs
        ).values_list('property_id', flat=True)
        shortlist_dict = {prop_id: True for prop_id in user_shortlisted}

    # Pagination
    paginator = Paginator(qs, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Results summary
    total_results = qs.count()
    deal_text = ""
    if deal_type == "sale":
        deal_text = "for Sale"
    elif deal_type == "rent":
        deal_text = "for Rent"
    elif deal_type == "commercial":
        deal_text = "Commercial Properties"

    results_summary = f"{total_results} results | Property {deal_text}"
    if location:
        results_summary += f" in {location}"

    context = {
        "properties": page_obj,
        "page_obj": page_obj,
        "total_results": total_results,
        "results_summary": results_summary,
        'deal_type_selected': deal_type,
        'location_query': location,
        'property_type_selected': property_type,
        'bhk_selected': bhk,
        'require_selected': require,
        'commercial_purpose_selected': commercial_purpose,
        'min_price': min_price,
        'max_price': max_price,
        "bhk_choices": bhk_choices,
        'shortlist_dict': shortlist_dict,
        "property_types": property_types,
    }

    # AJAX request handling
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "properties/partials/ajax_search_properties.html", context, request=request
        )
        return HttpResponse(html)

    return render(request, "properties/search_results.html", context)


def bhk_search(request):
    # --- 1. Define required template constants (NOW MATCHING YOUR MODEL) ---
    bhk_choices = [
        ('1bhk', '1BHK'),
        ('2bhk', '2BHK'),
        ('3bhk', '3BHK'),
        ('4bhk+', '4BHK+'),
    ] 
    property_types = ["flat", "house", "apartment", "villa", "land"]

    # --- 2. Retrieve ALL Filter Parameters from GET ---
    
    deal_type = request.GET.get('deal_type', '')
    location = request.GET.get('location', '')
    property_type = request.GET.get('property_type', '')
    bhk_selected_value = request.GET.get('bhk', '') 
    require = request.GET.get('require', '')
    commercial_purpose = request.GET.get('commercial_purpose', '')
    
    # Price fields must be passed back to pre-fill the slider values
    min_price = request.GET.get('min_price', '0')
    max_price = request.GET.get('max_price', '2000000')

    # --- 3. Apply the actual database filter (bhk only, as requested) ---
    if bhk_selected_value:
        # Initialize queryset based on all properties
        properties = Property.objects.all()
        
        if bhk_selected_value == '4 Bhk+':
            # FIX: Handle '4bhk+' by excluding all lower BHK types.
            # This relies on your database containing specific string values like '4bhk', '5bhk', etc., 
            # OR simply the other defined lower types '1bhk', '2bhk', '3bhk'.
            properties = properties.exclude(
                Q(bhk__iexact='1bhk') | 
                Q(bhk__iexact='2bhk') |
                Q(bhk__iexact='3bhk')
            )
            
        else:
            # FIX: Use __iexact for case-insensitive exact match using the model's value.
            # This filters for '1bhk', '2bhk', or '3bhk' exactly.
            properties = properties.filter(bhk__iexact=bhk_selected_value)

    else:
        properties = Property.objects.all()

    # --- 4. Prepare Context for Template State Restoration ---
    context = {
        # The main list of properties to display
        'properties': properties, 
        
        # State restoration variables for the sidebar
        'deal_type_selected': deal_type,
        'location_query': location,
        'property_type_selected': property_type,
        'bhk_selected': bhk_selected_value, # This tells the template which BHK button to check
        'require_selected': require,
        'commercial_purpose_selected': commercial_purpose,
        'min_price': min_price,             # This pre-fills the minPriceSlider
        'max_price': max_price,             # This pre-fills the maxPriceSlider

        # Constants needed for the template loops
        'bhk_choices': bhk_choices, 
        'property_types': property_types, 
        
        # NOTE: You'll likely need to add pagination variables here too, e.g.:
        # 'page_obj': paginator.get_page(page_number),
        # 'total_results': paginator.count,
    }

    return render(request, "properties/search_results.html", context)







def update_property_status(request, property_id, status):
    prop = get_object_or_404(Property, id=property_id)
    if status in ['approved', 'rejected']:
        prop.status = status
        prop.save()

        # Send email notification
        if status == 'approved':
            subject = "Your property has been approved 🎉"
            message = f"Hi {prop.owner.username},\n\nYour property '{prop.property_type}' is now live."
        else:
            subject = "Your property has been rejected ❌"
            message = f"Hi {prop.owner.username},\n\nYour property '{prop.property_type}' was rejected."

        send_notification_email(prop.owner, subject, message)

    return redirect('manage_property')


def notifications_page(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to home or login

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'notifications': notifications  # Always a queryset
    }
    return render(request, 'properties/client/notifications.html', context)

def mark_notification_read(request, notif_id):
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.read = True
    notification.save()
    # Redirect back to previous page or notifications page
    return redirect(request.META.get('HTTP_REFERER', 'notifications_page'))





# OTP storage (or you can use a model)
# views.py
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import random, time

OTP_STORE = {}  # simple in-memory store for demonstration

from django.core.mail import send_mail

def send_password_reset_otp(request):
    if request.method == "POST":
        import json, random, time
        data = json.loads(request.body)
        email = data.get("identifier")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "Email not found"})

        # Generate OTP
        otp = str(random.randint(100000, 999999))
        OTP_STORE[email] = {"otp": otp, "expires_at": time.time() + 600}  # 10 min expiry

        # Send email
        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP to reset password is: {otp}. It is valid for 10 minutes.",
            from_email=None,  # uses DEFAULT_FROM_EMAIL from settings.py
            recipient_list=[email],
        )

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"})



def verify_password_reset_otp(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        email = data.get("identifier")
        otp_input = data.get("otp")
        new_password = data.get("new_password")

        record = OTP_STORE.get(email)
        if not record or time.time() > record["expires_at"]:
            return JsonResponse({"success": False, "error": "OTP expired or not found"})

        if record["otp"] != otp_input:
            return JsonResponse({"success": False, "error": "Invalid OTP"})

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.save()
            del OTP_STORE[email]
            return JsonResponse({"success": True})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})







def article_list(request):
    articles = Article.objects.all().order_by('-date_created')
    return render(request, 'properties/blog/articles_list.html', {'articles': articles})

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'properties/blog/article_detail.html', {'article': article})



@login_required
def change_password_view(request):
    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        user = request.user
        errors = []

        if not check_password(current, user.password):
            errors.append("Current password is incorrect.")
        if len(new) < 6:
            errors.append("New password must be at least 6 characters.")
        if new != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            user.set_password(new)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect('change_password_view')

    return render(request, 'properties/client/change_password.html')













def properties_search(request):
    
    # Assuming Property.BHK_CHOICES is defined in your Property model
    try:
        # If your model is available, use this:
        # from .models import Property # Ensure this import is done higher up
        bhk_choices = Property.BHK_CHOICES
    except NameError:
        # Placeholder for BHK choices if model is not accessible here
        bhk_choices = [('1BHK', '1 BHK'), ('2BHK', '2 BHK'), ('3BHK', '3 BHK'), ('4BHK', '4 BHK')] 
        
    property_types = ["flat", "house", "apartment", "villa", "land", "commercial"]

    # 1. Get ALL filters from GET request 
    deal_type = request.GET.get('deal_type', '').strip()
    location = request.GET.get('location', '').strip()
    property_type = request.GET.get('property_type', '').strip().lower()
    bhk = request.GET.get('bhk', '').strip()
    require = request.GET.get('require', '').strip()            # Status (Ready to move, etc.)
    commercial_purpose = request.GET.get('commercial_purpose', '').strip().lower() 
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    qs = Property.objects.filter(is_active=True, status="approved")

    # --- Apply Filters ---
    
    if deal_type:
        # If user clicks commercial tab, deal_type might be 'commercial'. 
        # But the Property model deal_type field might only store 'sale' or 'rent'.
        # We will filter on deal_type as received, assuming 'commercial' properties 
        # are correctly tagged in the database or filtered by property_type later.
        qs = qs.filter(deal_type=deal_type)

    if location:
        qs = qs.filter(
            Q(locality__name__icontains=location) | 
            Q(locality__city__name__icontains=location)
        )

    if property_type:
        qs = qs.filter(property_type__iexact=property_type)

    if bhk and deal_type in ['sale', 'rent']:
        qs = qs.filter(bhk__iexact=bhk)

    # Filter for Status (e.g., Ready to Move, Under Construction)
    if require and deal_type in ['sale', 'rent']:
        qs = qs.filter(require__iexact=require) 

    if commercial_purpose and deal_type == 'commercial':
        # Assuming 'commercial_purpose' maps to a field like 'business_type' on Property
        qs = qs.filter(business_type__iexact=commercial_purpose) 

    # Price filters (Handling for slider values)
    if min_price:
        try:
            qs = qs.filter(price__gte=int(min_price))
        except (ValueError, TypeError):
            pass

    if max_price:
        try:
            qs = qs.filter(price__lte=int(max_price))
        except (ValueError, TypeError):
            pass

    # --- Shortlist dict ---
    shortlist_dict = {}
    if request.user.is_authenticated:
        # Placeholder for real Shortlist logic
        # user_shortlisted = Shortlist.objects.filter(user=request.user, property__in=qs).values_list('property_id', flat=True)
        # shortlist_dict = {prop_id: True for prop_id in user_shortlisted}
        pass 

    # --- Pagination ---
    paginator = Paginator(qs, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    
    # Results summary
    location_display = location if location else "all locations"
    deal_display = deal_type.capitalize() if deal_type else "Properties"
    results_summary = f"{qs.count()} results | {deal_display} in {location_display}"

    # --- Context Mapping (CRITICAL: Uses flat names the sidebar template expects) ---
    context = {
        # Results & Pagination
        "properties": page_obj,          # The current page of properties
        "page_obj": page_obj,            # The paginator page object
        "total_results": paginator.count, 
        "results_summary": results_summary,
        # Filter Options (For sidebar population)
        "bhk_choices": bhk_choices,
        "property_types": property_types,
        
        # Selected/Current Filter Values (Used by template to pre-select radio buttons and set input values)
        'location_query': location,               # Used for Location text input
        'deal_type_selected': deal_type,          # Used to show/hide BHK/Status filters
        'property_type_selected': property_type,
        'bhk_selected': bhk,
        'require_selected': require,              # Used to check 'Status' radio buttons
        'commercial_purpose_selected': commercial_purpose,
        'min_price': min_price,                   # Used to set price slider start
        'max_price': max_price,                   # Used to set price slider end
        
        'shortlist_dict': shortlist_dict,
    }

    # --- AJAX Response ---
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "properties/partials/ajax_search_properties.html", context, request=request
        )
        return HttpResponse(html)

    return render(request, "properties/search_results.html", context)
















def delete_user_review(request, review_id):
    review = get_object_or_404(LocalityFeedback, id=review_id)
    
    if request.user != review.user:
        messages.error(request, "You can only delete your own reviews.")
        return redirect(request.META.get('HTTP_REFERER', 'index'))
    
    review.delete()
    messages.success(request, "✅ Your review has been deleted successfully.")
    return redirect(request.META.get('HTTP_REFERER', 'index'))




    # city and locality suggestion view for home page

def city_suggestions(request):
    query = request.GET.get('q', '').lower()
    results = list(City.objects.filter(name__icontains=query).values_list('name', flat=True))
    return JsonResponse({'results': results})


# views for location and city suggestion for both in service modal
# views.py
from django.http import JsonResponse
from .models import City, Locality

def location_suggestions(request):
    query = request.GET.get('q', '').strip()

    # Cities matching query
    city_results = list(City.objects.filter(name__icontains=query).values_list('name', flat=True))

    # Localities matching query (Locality, City)
    locality_results = list(
        Locality.objects.filter(name__icontains=query)
        .select_related('city')
        .values_list('name', 'city__name')
    )
    locality_results = [f"{loc}, {city}" for loc, city in locality_results]

    results = city_results + locality_results
    return JsonResponse({'results': results})
