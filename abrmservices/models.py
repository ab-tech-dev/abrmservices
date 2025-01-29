from django.db import models
from django.conf import settings
from django.utils.timezone import now


class Photo(models.Model):

    image = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Listing(models.Model):
    class SaleType(models.TextChoices):
        FOR_SALE = 'For Sale'
        FOR_RENT = 'For Rent'

    class HomeType(models.TextChoices):
        HOUSE = 'house', 'House'
        APARTMENT = 'apartment', 'Apartment'
        CONDO = 'condo', 'Condo'
        TOWNHOME = 'townhome', 'Townhome'
    realtor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="realtor")
    location = models.CharField(max_length=255)
    title = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    sale_type = models.CharField(max_length=8, choices=SaleType.choices, default=SaleType.FOR_SALE)
    home_type = models.CharField(
        max_length=10,
        choices=HomeType.choices,
        default=HomeType.HOUSE
    )
    main_photo = models.ImageField(upload_to='main_photos/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    additional_photos = models.ManyToManyField(Photo, related_name='additional_photos', blank=True)
    bathroom_photos = models.ManyToManyField(Photo, related_name='bathroom_photos', blank=True)
    toilet_photos = models.ManyToManyField(Photo, related_name='toilet_photos', blank=True)
    is_published = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=now)

    def delete(self, *args, **kwargs):
        self.main_photo.storage.delete(self.main_photo.name)
        if self.video:
            self.video.storage.delete(self.video.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Listing: {self.location} - {self.sale_type}"
    

from django.db import models
