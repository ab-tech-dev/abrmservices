import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ABRMS.settings')
django.setup()
# from django.contrib.sites.models import Site

# site = Site.objects.get_or_create(id=1)[0]  # Ensure we're updating ID 1
# site.domain = "rested-cheerful-skink.ngrok-free.app"
# site.name = "abrms"
# site.save()

# from django.shortcuts import get_object_or_404
# from user.models import UserAccount  # Ensure you import the correct model

# user = get_object_or_404(UserAccount, email="abrelocationservices@gmail.com")
# user.is_active = True
# user.save()
