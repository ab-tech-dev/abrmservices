from django.db import models
from django.utils.timezone import now


# Create your models here.
class Listing(models.Model):
    class SaleType(models.TextChoices):
        FOR_SALE = 'For Sale'
        FOR_RENT = 'For Rent'
    class HomeType(models.TextChoices):
        HOUSE = 'House'
        CONDO = 'Condo'
        TOWNHOUSE = 'Townhouse'

    realtor =  models.EmailField(max_length=255)
    title =  models.CharField(max_length=255)
    slug =  models.SlugField(unique=True)
    address =  models.CharField(max_length=255)
    city =  models.CharField(max_length=255)
    state =  models.CharField(max_length=255)
    zipcode =  models.CharField(max_length=255)
    description =  models.TextField()
    price =  models.IntegerField()
    bedrooms =  models.IntegerField()
    bathrooms =  models.DecimalField(max_digits=2, decimal_places=1)
    sale_type =  models.CharField(max_length=10, choices=SaleType.choices,default=SaleType.FOR_SALE)
    home_type =  models.CharField(max_length=10, choices=HomeType.choices,default=HomeType.HOUSE)
    main_photo = models.ImageField(upload_to='listings/')
    photo_1 = models.ImageField(upload_to='listings/')
    photo_2 = models.ImageField(upload_to='listings/')
    photo_3 = models.ImageField(upload_to='listings/')
    is_published = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=now)

    def delete(self):
        self.main_photo.storage.delete(self.main_photo.name)
        self.photo_1.storage.delete(self.photo_1.name)
        self.photo_2.storage.delete(self.photo_2.name)
        self.photo_3.storage.delete(self.photo_3.name)


        super().delete()

    def __str__(self):
        return self.title


# Create your models here.

class House(models.Model):
    STATUS_CHOICES = (
        ('rent', 'For Rent'),
        ('sale', 'For Sale'),
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    full_package = models.IntegerField(default=0)  # Full package field
    image = models.ImageField(upload_to='house_images/')
    location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    description = models.TextField()
    bedroom_choices = [(i, str(i)) for i in range(1, 11)]
    bedroom = models.PositiveSmallIntegerField(choices=bedroom_choices, default=1)
    house_type_choices = [
        ('apartment', 'Apartment'),
        ('bungalow', 'Bungalow'),
        ('villa', 'Villa'),
        ('Duplex', 'Duplex')
        # Add more options as needed
    ]
    house_type = models.CharField(max_length=100, choices=house_type_choices, default='Apartment')
    # Other fields of your House model

