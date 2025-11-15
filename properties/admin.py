from django.contrib import admin
from .models import Contact, City, Property, PropertyImage, Testimonials,UserProfile,Shortlist, Inquiry ,Notification,  Feature,LocalityFeedback,Locality, Recentviewed,Article,OTP
from .models import FAQPage, FAQQuestion
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .utils import send_notification_email , send_admin_email  # ✅ import email utility


# Register your models here.
admin.site.register(Contact)

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1  # Number of empty image forms shown by default
    max_num = 10  # Optional: limit number of images


    

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline]
    list_display = [
        'id', 'owner', 'property_type', 'deal_type',
        'listed_by', 'status', 'get_locality', 'get_city', 'get_pincode',
        'price', 'rent_per_month', 'area', 'availability', 'require',
        'furnishing', 'property_age', 'posted_on', 'is_active', 'apartment_name'
    ]
    list_filter = [
        'status', 'property_type', 'listed_by', 'deal_type',
        'availability', 'furnishing', 'property_age',
        'facing', 'locality__city', 'locality', 'is_active','zoning_type', 'ownership_type'
    ]
    search_fields = [
        'title', 'desc',  'get_pincode',
        'owner__username',  'locality__name', 'locality__city__name'
    ]
    ordering = ['-posted_on']
    readonly_fields = ['posted_on', 'updated_on']

    filter_horizontal = ('features',)  # better UI for features (ManyToMany)

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'owner',  'desc', 'property_type',
                'deal_type', 'listed_by', 'status'
            )
        }),
        ('Location Details', {
            'fields': ('locality',)
        }),
        ('Pricing & Area', {
            'fields': ('price', 'rent_per_month', 'area', 'require', 'availability','area_unit','deposit_amount', 'plot_area')
        }),
        ('Property Details', {
            'fields': (
                'furnishing', 'floor_number', 'total_floors',
                'property_age', 'facing', 'parking'
            )
        }),
        ('Residential Details', {
            'fields': ('bhk', 'bedrooms', 'bathrooms','apartment_name')
        }),
        ('Commercial Details', {
            'fields': ('business_type','seats')
        }),
        ('Land Details', {
            'fields': ('road_access', 'road_width', 
                'zoning_type', 'ownership_type', 
                'boundary_wall',  
                'lease_duration')
        }),
        ('Features & Media', {
            'fields': ('features',)
        }),
        ('Timestamps', {
            'fields': ('posted_on', 'updated_on')
        }),
    )
    # Reuse model methods → no duplication needed
    def get_locality(self, obj):
        return obj.get_locality()
    get_locality.admin_order_field = 'locality__name'
    get_locality.short_description = 'Locality'

    def get_city(self, obj):
        return obj.get_city()
    get_city.admin_order_field = 'locality__city__name'
    get_city.short_description = 'City'

    def get_pincode(self, obj):
        return obj.locality.pincode if obj.locality else "-"
    get_pincode.short_description = "Pincode"

    actions = ['approve_properties', 'reject_properties', 'mark_as_available', 'mark_as_sold', 'mark_as_rented']

    # Approve
    @admin.action(description='✅ Approve selected properties')
    def approve_properties(self, request, queryset):
        for prop in queryset:
            prop.status = 'approved'
            prop.save()

            # Notify owner
            send_notification_email(
                prop.owner,
                subject="Your property has been approved 🎉",
                message=f"""
                Hi {prop.owner.username},

                Good news! 🎉 Your property "{prop.property_type}" in {prop.locality}
                has been approved and is now live on RealEstate.com.

                Regards,  
                RealEstate Team
                """
            )
        self.message_user(request, f"{queryset.count()} property(ies) were approved and owners notified.")

    # Reject
    @admin.action(description='❌ Reject selected properties')
    def reject_properties(self, request, queryset):
        for prop in queryset:
            prop.status = 'rejected'
            prop.save()

            # Notify owner
            send_notification_email(
                prop.owner,
                subject="Your property has been rejected ❌",
                message=f"""
                Hi {prop.owner.username},

                Unfortunately, your property "{prop.property_type}" in {prop.locality}
                has been rejected by our team.

                Please review our guidelines and resubmit.

                Regards,  
                RealEstate Team
                """
            )
        self.message_user(request, f"{queryset.count()} property(ies) were rejected and owners notified.")

    # Available
    @admin.action(description='Mark selected properties as Available')
    def mark_as_available(self, request, queryset):
        updated = queryset.update(availability='available')
        self.message_user(request, f"{updated} property(ies) were marked as Available")

    # Sold
    @admin.action(description='Mark selected properties as Sold')
    def mark_as_sold(self, request, queryset):
        updated = queryset.update(availability='sold')
        self.message_user(request, f"{updated} property(ies) were marked as Sold")

    # Rented
    @admin.action(description='Mark selected properties as Rented')
    def mark_as_rented(self, request, queryset):
        updated = queryset.update(availability='rented')
        self.message_user(request, f"{updated} property(ies) were marked as Rented")

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'property_count')
    search_fields = ('name',)

    def property_count(self, obj):
        # Count all properties linked to this city through localities
        return Property.objects.filter(locality__city=obj).count()
    property_count.short_description = 'Properties'


admin.site.register(Testimonials)



@admin.register(Shortlist)
class ShortlistAdmin(admin.ModelAdmin):
    list_display = ("user", "property", "created_at")
    search_fields = ("user__username", "property__title")
    list_filter = ('created_at',)



@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "property","buyer_type", "sender", "created_at", "owner_replied", "reply_message", "replied_at")
    list_filter = ("created_at","buyer_type",)
    search_fields = ("name", "phone", "message",  "sender__username")
    ordering = ("-created_at",)


admin.site.register(UserProfile)

@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city","pincode")
    list_filter = ("city",)
    search_fields = ("name", "city__name", "pincode")
    ordering = ("name",)


@admin.register(LocalityFeedback)
class LocalityFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "locality", 
        "user", 
        "average_rating", 
        "approved", 
        "created_at","years_lived", "email", "properties"
    )
    list_filter = ("approved", "locality__city")
    search_fields = ("locality__name", "locality__city__name", "user__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    actions = ["approve_reviews", "reject_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = "✅ Approve selected reviews"

    def reject_reviews(self, request, queryset):
        queryset.update(approved=False)
    reject_reviews.short_description = "❌ Reject selected reviews"



@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


admin.site.register(Recentviewed)



admin.site.register(Notification)
admin.site.register(Article)
admin.site.register(OTP)




@admin.register(FAQPage)
class FAQPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")

@admin.register(FAQQuestion)
class FAQQuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "page", "updated_at")
    list_filter = ("page",)
    search_fields = ("question", "answer")


