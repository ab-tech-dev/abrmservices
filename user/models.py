from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email adress')
        
        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(
            email = email,
            name = name
        )

        user.set_password(password)
        user.save(using=self._db)

        return user 
    
    def create_realtor(self, email, name, password=None):
        user = self.create_user(email, name, password)

        user.is_realtor = True
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, name, password):
        user =  self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user
from django.utils.timezone import now

# class UserAccount(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(max_length=255, unique=True)
#     name = models.CharField(max_length=255)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_realtor = models.BooleanField(default=False)
#     last_active = models.DateTimeField(null=True, blank=True)  # Track last activity

#     objects = UserAccountManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['name']

#     def update_last_active(self):
#         """Update the last active time for the user."""
#         self.last_active = now()
#         self.save(update_fields=["last_active"])

#     def __str__(self):
#         return self.email

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField (default=False)

    is_realtor = models.BooleanField(default=False)
    last_active = models.DateTimeField(null=True, blank=True)  # Track last activity


    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def update_last_active(self):
        """Update the last active time for the user."""
        self.last_active = now()
        self.save(update_fields=["last_active"])

    def __str__(self):
        return self.email

from django.db import models
from django.conf import settings  # Ensures compatibility with your custom user model

class Chat(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.user1.name} (Superuser) and {self.user2.name}"

    def save(self, *args, **kwargs):
        """Override the save method to enforce user1 as superuser and user2 as logged-in user"""
        if not self.user1.is_superuser:
            raise ValueError('User1 must be a superuser')
        if self.user2 == self.user1:
            raise ValueError('User2 cannot be the same as User1')
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_chat(cls, superuser, logged_in_user):
        """Ensure a separate chat is created for each superuser and logged-in user pair"""
        # Check if chat already exists for this superuser and logged-in user pair
        chat = cls.objects.filter(user1=superuser, user2=logged_in_user) \
                          .or_filter(user1=logged_in_user, user2=superuser).first()

        # If no existing chat, create a new one
        if not chat:
            chat = cls(user1=superuser, user2=logged_in_user)
            chat.save()

        return chat

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_chat_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # New field to track read status

    def __str__(self):
        return f"Message from {self.sender.name} at {self.timestamp.strftime('%H:%M')}"



from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message[:20]}"
