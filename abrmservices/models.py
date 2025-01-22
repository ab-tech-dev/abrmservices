from django.db import models
from django.utils.timezone import now
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

# Listing Model
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
    
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1)

    sale_type = models.CharField(max_length=8, choices=SaleType.choices, default=SaleType.FOR_SALE)
    home_type = models.CharField(
        max_length=10,
        choices=HomeType.choices,
        default=HomeType.HOUSE
    )
    main_photo = models.ImageField(upload_to='listings/')
    photo_1 = models.ImageField(upload_to='listings/', blank=True, null=True)
    photo_2 = models.ImageField(upload_to='listings/', blank=True, null=True)
    photo_3 = models.ImageField(upload_to='listings/', blank=True, null=True)

    is_published = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=now)

    # Overriding delete method to ensure photos are deleted from storage
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
