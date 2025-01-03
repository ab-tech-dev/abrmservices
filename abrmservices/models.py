from django.db import models
from django.utils.timezone import now


# Create your models here.
from django.db import models
from django.utils.timezone import now
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

class Listing(models.Model):
    class SaleType(models.TextChoices):
        FOR_SALE = 'For Sale'
        FOR_RENT = 'For Rent'

    class HomeType(models.TextChoices):
        HOUSE = 'house', 'House'
        APARTMENT = 'apartment', 'Apartment'
        CONDO = 'condo', 'Condo'
        TOWNHOME = 'townhome', 'Townhome'

    realtor = models.EmailField(max_length=255)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    location = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=20)  # Adjusted to fit realistic zip codes
    description = models.TextField()
    
    # Adjust price to allow larger values with decimal places
    price = models.DecimalField(max_digits=12, decimal_places=2)

    bedrooms = models.IntegerField()
    
    # Bathrooms can have decimal values (e.g., 1.5 bathrooms)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)

    # Choices for sale and home type with adjusted max_length
    sale_type = models.CharField(max_length=8, choices=SaleType.choices, default=SaleType.FOR_SALE)
    home_type = models.CharField(
        max_length=10,  # Ensure max_length is appropriate for the longest choice ('townhome')
        choices=HomeType.choices,
        default=HomeType.HOUSE  # Set default value if needed
    )
    main_photo = models.ImageField(upload_to='listings/')
    photo_1 = models.ImageField(upload_to='listings/', blank=True, null=True)
    photo_2 = models.ImageField(upload_to='listings/', blank=True, null=True)
    photo_3 = models.ImageField(upload_to='listings/', blank=True, null=True)

    is_published = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=now)

    # Overriding the delete method to ensure photos are deleted from storage
    def delete(self, *args, **kwargs):
        self.main_photo.storage.delete(self.main_photo.name)
        if self.photo_1:
            self.photo_1.storage.delete(self.photo_1.name)
        if self.photo_2:
            self.photo_2.storage.delete(self.photo_2.name)
        if self.photo_3:
            self.photo_3.storage.delete(self.photo_3.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title


# class Message(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"Message from {self.sender.name} to {self.receiver.name} at {self.timestamp}"
# # Create your models here.

# class House(models.Model):
#     STATUS_CHOICES = (
#         ('rent', 'For Rent'),
#         ('sale', 'For Sale'),
#     )
    
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES)
#     price = models.DecimalField(max_digits=8, decimal_places=2)
#     full_package = models.IntegerField(default=0)  # Full package field
#     image = models.ImageField(upload_to='house_images/')
#     location = models.CharField(max_length=100)
#     phone_number = models.CharField(max_length=20)
#     description = models.TextField()
#     bedroom_choices = [(i, str(i)) for i in range(1, 11)]
#     bedroom = models.PositiveSmallIntegerField(choices=bedroom_choices, default=1)
#     house_type_choices = [
#         ('apartment', 'Apartment'),
#         ('bungalow', 'Bungalow'),
#         ('villa', 'Villa'),
#         ('Duplex', 'Duplex')
#         # Add more options as needed
#     ]
#     house_type = models.CharField(max_length=100, choices=house_type_choices, default='Apartment')
#     # Other fields of your House model

