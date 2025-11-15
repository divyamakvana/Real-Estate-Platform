from django.db import models
from django.contrib.auth.models import User
from .utils import format_price
from django.utils import timezone
from datetime import timedelta



# Create your models here.
# userprofile


from django.conf import settings

class UserProfile(models.Model):
    USER_ROLES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('agent', 'Agent'),
    )
    STATUS_CHOICES = [
        ('pending', 'Pending'),   # waiting for admin approval
        ('active', 'Active'),     # approved and active
        ('suspended', 'Suspended') # banned/rejected
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=USER_ROLES, default="buyer")
    phone = models.CharField(max_length=15, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    # for email
    email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        default="profile_pics/default-avatar.png",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Already added
    free_posts_remaining = models.PositiveIntegerField(default=2)  # free posts for new owners
    wallet_credits = models.PositiveIntegerField(default=0)        # credits purchased

     # store deletion date if deactivated
    scheduled_deletion = models.DateTimeField(null=True, blank=True)

    def schedule_deletion(self):
        self.user.is_active = False
        self.scheduled_deletion = timezone.now() + timedelta(days=28)
        self.user.save()
        self.save()

    def __str__(self):
        return f"{self.user.username} ({self.role})"



# contact model
class Contact(models.Model):
    mail = models.CharField(max_length=20)
    tel = models.IntegerField()
    msg = models.TextField()


# model for property
class City(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='cities/', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Locality(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="localities")
    name = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ('city', 'name')

    def __str__(self):
        return f"{self.name}, {self.city.name}"

class Feature(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class Property(models.Model):
    # === Choices ===
    FURNISHING_CHOICES = [
    ("furnished", "Furnished"),
    ("semi_furnished", "Semi-Furnished"),
    ("unfurnished", "Unfurnished"),
    ]

    AGE_CHOICES = [
    ("new", "New Construction"),
    ("0-1", "Less than 1 Year"),
    ("1-5", "1-5 Years"),
    ("5-10", "5-10 Years"),
    ("10+", "10+ Years"),
    ]

    FACING_CHOICES = [
    ("north", "North"),
    ("south", "South"),
    ("east", "East"),
    ("west", "West"),
    ]


    DEAL_TYPE_CHOICES = [
    ('sale', 'For Sale'),
    ('rent', 'For Rent'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    LISTED_BY_CHOICES = [
        ('owner', 'Owner'),
        ('agent', 'Agent'),
        ('builder', 'Builder'),
    ]

    PROPERTY_TYPE_CHOICES = [
        ('flat', 'Flat'),
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
    ]

    BHK_CHOICES = [
        ('1bhk', '1BHK'),
        ('2bhk', '2BHK'),
        ('3bhk', '3BHK'),
        ('4bhk+', '4BHK+'),
    ]

    BUSINESS_TYPES = [
        ('office', 'Office'),
        ('shop', 'Shop'),
        ('restaurant', 'Restaurant'),
        ('warehouse', 'Warehouse'),
        ('factory', 'Factory'),
    ]

    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ]

    REQUIRE_CHOICES = [
        ('ready', 'Ready to Move'),
        ('under_construction', 'Under Construction'),
        ('launching_soon', 'Launching Soon'),
    ]

    # === Common Fields ===
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
   
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name="properties")
    apartment_name = models.CharField(max_length=100, blank=True, null=True)

    desc = models.TextField()
    
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rent_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Rent


    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listed_by = models.CharField(max_length=20, choices=LISTED_BY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    deal_type = models.CharField(max_length=10, choices=DEAL_TYPE_CHOICES)
    posted_on = models.DateTimeField(auto_now_add=True)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    area = models.PositiveIntegerField(null=True, blank=True, help_text="Area in square feet")
    require = models.CharField(max_length=30, choices=REQUIRE_CHOICES, default='ready to move')
    updated_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    

    furnishing = models.CharField(
        max_length=20, choices=FURNISHING_CHOICES, default="unfurnished"
    )
    floor_number = models.IntegerField(blank=True, null=True)
    total_floors = models.IntegerField(blank=True, null=True)
    property_age = models.CharField(
        max_length=20, choices=AGE_CHOICES, default="new"
    )
    facing = models.CharField(
        max_length=20, choices=FACING_CHOICES, blank=True, null=True, help_text="e.g. North, East, West"
    )
    parking = models.IntegerField(default=0)

    features = models.ManyToManyField(Feature, blank=True)

    # === Residential-specific ===
    bhk = models.CharField(max_length=10, choices=BHK_CHOICES, null=True, blank=True)
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)

    # === Commercial-specific ===
    business_type = models.CharField(
        max_length=100, choices=BUSINESS_TYPES, null=True, blank=True,
        help_text="e.g. Office, Shop, Warehouse"
    )
    seats = models.IntegerField(blank=True, null=True)      # <-- Seats/workstations
   
    

    # === Land-specific ===
    plot_area = models.FloatField(null=True, blank=True, help_text="Area in square yards/acres")
    road_access = models.BooleanField(default=False)
    area_unit = models.CharField(max_length=20, default="sq.ft", help_text="sq.ft, sq.yd, acre")
    road_width = models.IntegerField(null=True, blank=True, help_text="Width in feet")


    zoning_type = models.CharField(
        max_length=50,
        choices=[("residential", "Residential"), ("commercial", "Commercial"), 
                 ("industrial", "Industrial"), ("agricultural", "Agricultural")],
        null=True, blank=True
    )

    ownership_type = models.CharField(
        max_length=50,
        choices=[("freehold", "Freehold"), ("leasehold", "Leasehold"), 
                 ("poa", "Power of Attorney"), ("govt", "Government Land")],
        null=True, blank=True
    )

    boundary_wall = models.BooleanField(default=False)
    lease_duration = models.CharField(max_length=50, null=True, blank=True, help_text="e.g. 11 months / 3 years")



    
    def display_price(self):
        if self.deal_type == 'sale' and self.price:
            return format_price(self.price)
        elif self.deal_type == 'rent' and self.rent_per_month:
            return f"{format_price(self.rent_per_month)}/Month"
        return "Price not available"

    def display_price_per_sqft(self):
        if self.deal_type == 'sale' and self.area and self.price:
            return self.price / self.area
        return None
    
    

    def save(self, *args, **kwargs):
        # If property is newly created
        if not self.pk:
            if self.owner.is_superuser or (hasattr(self.owner, "userprofile") and self.owner.userprofile.role == "admin"):
                self.status = 'approved'
            else:
                self.status = 'pending'

        # If property is sold/rented -> always approved
        if self.availability in ['sold', 'rented']:
            self.status = 'approved'

        super().save(*args, **kwargs)

    # Helper methods
    def get_city(self):
        return self.locality.city.name if self.locality and self.locality.city else None

    def get_locality(self):
        return self.locality.name if self.locality else None

    def __str__(self):
        return f"{self.desc} - {self.get_locality()} ({self.get_city()})"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.desc}"


class Recentviewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="recent_views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "property"], name="unique_user_property")
        ]
        ordering = ["-viewed_at"]


class Shortlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')
    buyer_type = models.CharField(max_length=20, choices=(("individual", "Individual"), ("dealer", "Dealer")), default='Individual')
    
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Track owner reply
    owner_replied = models.BooleanField(default=False)
    reply_message = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Inquiry by {self.name} for {self.property}'








class LocalityFeedback(models.Model):
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="locality_feedbacks")
    email = models.EmailField()
    
    properties = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)  # NEW
    
    # Category ratings (1–5 scale)
    connectivity = models.IntegerField(default=0)
    safety = models.IntegerField(default=0)
    public_transport = models.IntegerField(default=0)
    water_supply = models.IntegerField(default=0)
    power_supply = models.IntegerField(default=0)
    cleanliness = models.IntegerField(default=0)
    years_lived = models.IntegerField(default=0)

    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # Admin approval
    deleted = models.BooleanField(default=False)   # Soft delete

    @property
    def average_rating(self):
        ratings = [
            self.connectivity, self.safety, self.public_transport,
            self.water_supply, self.power_supply, self.cleanliness
        ]
        valid = [r for r in ratings if r > 0]
        return round(sum(valid) / len(valid), 1) if valid else 0

    def __str__(self):
        return f"{self.locality.name} - {self.average_rating}"


    

 

  


# model for testimonial
class Testimonials(models.Model):
    name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    review = models.TextField()
    rating = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    



# for notification
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
    

class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.created_at + timedelta(minutes=5)

    def mark_used(self):
        self.is_used = True
        self.save()

    @classmethod
    def generate_otp(cls, user):
        code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, code=code)

    @classmethod
    def verify_otp(cls, user, code):
        try:
            otp_instance = cls.objects.filter(user=user, code=code, is_used=False).latest('created_at')
            if otp_instance.is_valid():
                otp_instance.mark_used()
                return True
            return False
        except cls.DoesNotExist:
            return False


from django.db import models

class FAQPage(models.Model):
    """Different pages like EMI, Area, Budget, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class FAQQuestion(models.Model):
    """FAQ questions and answers."""
    page = models.ForeignKey(FAQPage, on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question[:50]

