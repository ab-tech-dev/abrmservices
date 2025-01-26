from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
import hashlib
from abrmservices.models import Listing

User = get_user_model()

class Wallet(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet for {self.user.name} - Balance: {self.balance}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
        ("transfer", "Transfer"),
        ("escrow_release", "Escrow Release"),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100)
    transaction_hash = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_hash:
            raw_data = f"{self.wallet.user.id}{self.amount}{self.transaction_type}{timezone.now()}"
            self.transaction_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} - {self.amount}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.action}"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('funded', 'Funded'),
        ('escrow_initiated', 'Escrow Initiated'),
        ('seller_confirmed', 'Seller Confirmed'),
        ('buyer_confirmed', 'Buyer Confirmed'),
        ('completed', 'Completed'),
    ]

    tracking_id = models.CharField(max_length=255, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_transactions')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_transactions')
    property = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.tracking_id} for {self.property.title}"


class Escrow(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("seller_confirmed", "Seller Confirmed"),
        ("buyer_confirmed", "Buyer Confirmed"),
        ("successful", "Successful"),
        ("cancelled", "Cancelled"),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="escrow_as_buyer")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="escrow_as_seller")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=False, blank=False, default=None)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    buyer_confirmed_at = models.DateTimeField(null=True, blank=True)
    seller_confirmed_at = models.DateTimeField(null=True, blank=True)
    transaction_hash = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.transaction_hash:
            raw_data = f"{self.buyer.id}{self.seller.id}{self.amount}{timezone.now()}"
            self.transaction_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Escrow {self.buyer.name} to {self.seller.name} - {self.amount} ({self.status})"
