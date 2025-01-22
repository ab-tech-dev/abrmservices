from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.timezone import now
from django.conf import settings

# Custom User Manager
class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(
            email=email,
            name=name
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
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

# Custom User Model
class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
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


class Chat(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.user1.name} and {self.user2.name}"

    def save(self, *args, **kwargs):
        """Override the save method to ensure user1 and user2 are distinct."""
        if self.user1 == self.user2:
            raise ValueError('User1 and User2 cannot be the same')
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_chat(cls, user1, user2):
        """Ensure a chat is created for any pair of users."""
        # Ensure the order of users does not affect chat creation
        if user1.id > user2.id:
            user1, user2 = user2, user1
        
        chat = cls.objects.filter(user1=user1, user2=user2).first()

        if not chat:
            chat = cls(user1=user1, user2=user2)
            chat.save()

        return chat

# ChatMessage Model (unchanged)
class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_chat_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # Track read status

    def __str__(self):
        return f"Message from {self.sender.name} at {self.timestamp.strftime('%H:%M')}"

# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message[:20]}"
