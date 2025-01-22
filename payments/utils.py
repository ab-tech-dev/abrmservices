# utils.py
from cryptography.fernet import Fernet
import hmac
import hashlib
from ABRMS import settings

# Encryption Setup
SECRET_KEY = bytes(settings.SECRET_KEY_P, 'utf-8')
cipher = Fernet(SECRET_KEY)

# Encryption Helpers
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    return cipher.decrypt(encrypted_data.encode()).decode()

# Verify Webhook Signature
def verify_webhook_signature(payload, signature):
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(), payload, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)


print