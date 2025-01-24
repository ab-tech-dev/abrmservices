from django.contrib import admin
from .models import Wallet, WalletTransaction, AuditLog, Transaction, Escrow

# Register your models here.
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(AuditLog)
admin.site.register(Transaction)
admin.site.register(Escrow)
