# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from payments.models import Wallet

User = get_user_model()

@receiver(post_save, sender=User)
def create_wallet_for_new_user(instance, created, **kwargs):
    if created:  # This ensures the wallet is only created when the user is newly created
        Wallet.objects.create(user=instance)
