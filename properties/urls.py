from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import render
urlpatterns = [
    path('', views.home, name="home"),

    # admin routes start here
    path('login/' ,views.login_view, name="login_view"),
    path('admin-dashboard/' ,views.admin_dashboard, name="admin_dashboard"),
    path('users/' ,views.manage_users, name="manage_users"),
    path('custom-admin/properties/' ,views.manage_property, name="manage_property"),
    path("custom-admin/properties/<int:property_id>/<str:status>/", views.update_property_status, name="update_property_status"),
    path("custom-admin/properties/<int:property_id>/", views.property_detail, name="property_detail"),
    path("pending_approvals/", views.pending_approvals, name="pending_approvals"),
   # User actions
    path('custom-admin/users/activate/<int:user_id>/', views.activate_user, name='activate_user'),
    path('custom-admin/users/suspend/<int:user_id>/', views.suspend_user, name='suspend_user'),
    path('custom-admin/users/approve-role/<int:user_id>/', views.approve_user_role, name='approve_user_role'),
    path('custom-admin/users/reject-role/<int:user_id>/', views.reject_user_role, name='reject_user_role'),
# properties/urls.py
    path("custom-admin/users/view/<int:user_id>/", views.view_user, name="view_user"),

   # Admin review management
path('custom-admin/feedbacks/', views.manage_reviews, name='manage_reviews'),
path('custom-admin/feedbacks/approve/<int:review_id>/', views.approve_review, name='approve_review'),
path('custom-admin/feedbacks/reject/<int:review_id>/', views.reject_review, name='reject_review'),
path('custom-admin/feedbacks/delete/<int:review_id>/', views.delete_review, name='delete_review'),
# urls.py
path('custom-admin/enquiries/', views.manage_enquiries, name='manage_enquiries'),
path('custom-admin/enquiries/view/<int:enquiry_id>/', views.view_enquiry, name='view_enquiry'),
path('custom-admin/enquiries/delete/<int:enquiry_id>/', views.delete_enquiry, name='delete_enquiry'),
path('custom-admin/enquiries/remind_owner/<int:enquiry_id>/', views.remind_owner, name='remind_owner'),


path('profile/', views.admin_profile, name='admin_profile'),

path('logout/', views.logout_view, name='logout_view'),
path('admins/', views.manage_admins, name='manage_admins'),
path('admins/create/', views.create_admin, name='create_admin'),
path("superuser-dashboard/", views.superuser_dashboard, name="superuser_dashboard"),
    # Password reset
    path(
    'custom-admin/password_reset/',
    auth_views.PasswordResetView.as_view(
        template_name='properties/admin/password_reset_form.html',
        email_template_name='properties/admin/password_reset_email.txt',  # plain text fallback
        html_email_template_name='properties/admin/password_reset_email.html',  # HTML email
        subject_template_name='properties/admin/password_reset_subject.txt',
        success_url='/custom-admin/password_reset/done/'
    ),
    name='admin_password_reset'
),

    path(
        'custom-admin/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='properties/admin/password_reset_done.html'
        ),
        name='admin_password_reset_done'
    ),

    path(
        'custom-admin/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='properties/admin/password_reset_confirm.html',
            success_url='/custom-admin/reset/done/'
        ),
        name='admin_password_reset_confirm'
    ),

    path(
        'custom-admin/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='properties/admin/password_reset_complete.html'
        ),
        name='admin_password_reset_complete'
    ),


      




   
    

    #admin routes start here...
    path('index/', views.index, name="index"),
    


    # client urls start here
     
    path('user_signup/', views.user_signup, name="user_signup"),
    path('user_login/', views.user_login, name="user_login"),
    path('send-login-otp/', views.send_login_otp, name='send_login_otp'),
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    path('user_logout/', views.user_logout, name="user_logout"),
    path('user-profile/', views.user_profile, name="user_profile"),
    # path('/profile/edit_profile/', views.edit_profile, name="edit_profile"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("search_properties/", views.search_properties, name="search_properties"),
    path("properties-search/", views.properties_search, name="properties_search"),

 path('change-password-view/', views.change_password_view, name='change_password_view'),
 path('api/send-password-reset-otp/', views.send_password_reset_otp, name='send_password_reset_otp'),
    path('api/verify-password-reset-otp/', views.verify_password_reset_otp, name='verify_password_reset_otp'),

    


path('/conf_delete_acc/', views.conf_delete_acc, name="conf_delete_acc"),
    path('/delete_acc/', views.delete_acc, name="delete_acc"),
    
    
    path("post_property/", views.post_property, name="post_property"),
    path("check_post_eligibility/", views.check_post_eligibility, name="check_post_eligibility"),
   

    path("view_detail/<int:id>/", views.view_detail, name="view_detail"),
    path('toggle-shortlist/', views.toggle_shortlist, name='toggle_shortlist'),
    path('activity-page/', views.activity_page, name='activity_page'), 
    path("search/", views.city_search, name="city_search"),
    path("city-autocomplete/", views.city_autocomplete, name="city_autocomplete"),
    path("bhk_search/", views.bhk_search, name="bhk_search"),

    path("manage_properties/", views.manage_properties, name="manage_properties"),
    # for submiting
    path("property-submitted/", lambda r: render(r, "properties/client/property_submitted.html"), name="property_submitted"),

     path("update-availability/<int:id>/<str:status>/", views.update_availability, name="update_availability"),
 
    path("delete-property/<int:id>/", views.delete_property, name="delete_property"),
    path("add_review/<int:property_id>/", views.add_review, name="add_review"),
 
    # urls.py
    path('delete_user_review/<int:review_id>/', views.delete_user_review, name='delete_user_review'),

    path("all_reviews/<int:locality_id>/", views.all_reviews, name="all_reviews"),
   
    path("notifications-page/", views.notifications_page, name="notifications_page"),
    path('mark_notification_read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),



# routes for locality and city suggestion in home page
path('ajax/city-suggestions/', views.city_suggestions, name='city_suggestions'),
 path('ajax/location-suggestions/', views.location_suggestions, name='location_suggestions'),



    # ... your existing URLs
    



# enquiry routes



   



    # routes fot deffernt tool
    path('emi_calc/', views.emi_calc, name='emi_calc'),
    path('budget_calc/', views.budget_calc, name='budget_calc'),
    path('loan_eligibility/', views.loan_eligibility, name='loan_eligibility'),
    path('area_calc/', views.area_calc, name='area_calc'),




    


     

    

  










    path('about/', views.about, name="about"),
    path('contact/', views.contact, name="contact"),
    path('terms/', views.terms, name="terms"),
    path('faq/', views.faq, name="faq"),
    path('privacypolicy/', views.privacypolicy, name="privacypolicy"),
    path('testimonials/', views.testimonials, name="testimonials"),




# payment integration routes







  
]