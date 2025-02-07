from .models import Notification
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render
from .models import UserAccount

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Chat, ChatMessage
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow

from ABRMS import settings
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from django.shortcuts import redirect, render
from django.contrib.auth import login
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow insecure transport for development

import re
import logging
import geoip2.database
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_protect
from django_ratelimit.decorators import ratelimit
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import UserAccount, FailedLoginAttempt

logger = logging.getLogger(__name__)

# Security settings
MAX_LOGIN_ATTEMPTS = 5  # Lock account after 5 failed attempts
LOCKOUT_DURATION = 15  # Lockout duration in minutes

def get_client_ip(request):
    """Securely retrieve the user's IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
from google_auth_oauthlib.flow import Flow
from django.contrib.auth import get_user_model
User = get_user_model()

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

def google_auth_init(request, action):
    """
    Initialize Google OAuth2 flow for sign-in or sign-up.
    """
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_OAUTH2_REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='select_account'
    )

    request.session['google_oauth2_state'] = state
    request.session['google_oauth2_action'] = action  # Track if it's sign-in or sign-up

    return redirect(authorization_url)


def google_auth_callback(request):
    """
    Handle Google OAuth2 callback for sign-in or sign-up.
    """
    state = request.session.get('google_oauth2_state')
    action = request.session.get('google_oauth2_action')  # 'signin' or 'signup'

    if request.GET.get('state') != state:
        messages.error(request, "Invalid state parameter. Please try again.")
        return redirect('housing')

    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_OAUTH2_REDIRECT_URI],
                }
            },
            scopes=SCOPES,
            state=state,
        )
        flow.redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI

        # Fetch access token
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        # Validate ID token
        idinfo = id_token.verify_oauth2_token(
            credentials.id_token,
            Request(),
            settings.GOOGLE_OAUTH2_CLIENT_ID,
        )

        # Extract user details
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')

        # Handle sign-in or sign-up differently
        if action == "signup":
            # Ensure user doesn't already exist before signing up
            if UserAccount.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists. Please sign in.")
                return redirect('housing')

            # Create new user
            user = UserAccount.objects.create(
                email=email,
                name=f"{first_name} {last_name}",
                google_authenticated=True,
                is_active=True  # Mark as active since Google verified email
            )
            user.set_unusable_password()  # No password required for Google login
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('housing')

        elif action == "signin":
            # Check if user exists
            user = UserAccount.objects.filter(email=email).first()
            # ✅ Brute Force Protection
            ip_address = get_client_ip(request)
            failed_attempts = FailedLoginAttempt.objects.filter(email=email, ip_address=ip_address)

            if failed_attempts.count() >= MAX_LOGIN_ATTEMPTS:
                last_attempt = failed_attempts.last()
                if (now() - last_attempt.timestamp).seconds < (LOCKOUT_DURATION * 60):
                    messages.error(request, 'Too many failed attempts. Try again later.')
                    return redirect('/housing/#login')
                else:
                    failed_attempts.delete()  # Reset failed attempts after lockout duration

            if not user:
                messages.error(request, "No account found. Please sign up first.")
                return redirect('housing')
            # ✅ Log Login Details with IP Geolocation
            
            user.last_login_ip = ip_address
            user.last_login_agent = request.META.get('HTTP_USER_AGENT', '')
            geoip_db_path = os.path.join(settings.BASE_DIR, 'static', 'GeoLite2-City.mmdb')

            try:
                with geoip2.database.Reader(geoip_db_path) as reader:
                    geo_data = reader.city(ip_address)
                    user.last_login_location = f"{geo_data.city.name}, {geo_data.country.name}"
            except Exception as e:
                logger.error(f"Error fetching geo data for IP {ip_address}: {str(e)}")
                user.last_login_location = "Unknown"
            user.save()
            # Log the user in
            login(request, user)
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('housing')

        else:
            messages.error(request, "Invalid authentication action. Please try again.")
            return redirect('housing')

    except Exception as e:
        print(e)
        messages.error(request, f"Google authentication failed: {str(e)}")
        return redirect('housing')



@csrf_protect
@ratelimit(key='ip', rate='5/m', method='POST', block=True)  # Prevents spam
def register(request):
    """Secure user registration with email verification and strong password validation."""
    if request.method == 'POST':
        name = request.POST.get('name').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        is_realtor = request.POST.get('is_realtor') == 'on'

        # ✅ Validate Email Format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format.')
            return redirect('housing')

        # ✅ Enforce Strong Password Policy
        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[A-Za-z]', password):
            messages.error(request, 'Password must be at least 8 characters and include both letters and numbers.')
            return redirect('housing')

        if password != re_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('housing')

        # ✅ Prevent Duplicate Email
        if UserAccount.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('housing')

        # ✅ Create User with Email Verification
        user = (
            UserAccount.objects.create_realtor(email=email, name=name, password=password)
            if is_realtor
            else UserAccount.objects.create_user(email=email, name=name, password=password)
        )

        user.is_active = False  # Prevent login until email is verified
        send_verification_email(user,request)
        user.save()
        messages.success(request, 'Account created! Please verify your email before logging in.')
        return redirect('housing')

    return redirect('housing')


@csrf_protect
@ratelimit(key='ip', rate='5/m', method='POST', block=True)  # Prevents brute-force attacks
def user_login(request):
    """Secure user login with brute-force protection and IP logging."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')

        # ✅ Check If User Exists
        user = UserAccount.objects.filter(email=email).first()
        if not user:
            messages.error(request, 'Invalid credentials.')
            return redirect('/housing/#login')

        # ✅ Prevent Login If Email Not Verified
        if not user.is_active:
            messages.error(request, 'Please verify your email before logging in.')
            return redirect('/housing/#login')

        # ✅ Brute Force Protection
        ip_address = get_client_ip(request)
        failed_attempts = FailedLoginAttempt.objects.filter(email=email, ip_address=ip_address)

        if failed_attempts.count() >= MAX_LOGIN_ATTEMPTS:
            last_attempt = failed_attempts.last()
            if (now() - last_attempt.timestamp).seconds < (LOCKOUT_DURATION * 60):
                messages.error(request, 'Too many failed attempts. Try again later.')
                return redirect('/housing/#login')
            else:
                failed_attempts.delete()  # Reset failed attempts after lockout duration

        # ✅ Authenticate User
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)

            # ✅ Secure Session Settings
            request.session.set_expiry(3600)  # 1-hour session expiration

            # ✅ Log Login Details with IP Geolocation
            user.last_login_ip = ip_address
            user.last_login_agent = request.META.get('HTTP_USER_AGENT', '')
            geoip_db_path = os.path.join(settings.BASE_DIR, 'static', 'GeoLite2-City.mmdb')

            try:
                with geoip2.database.Reader(geoip_db_path) as reader:
                    geo_data = reader.city(ip_address)
                    user.last_login_location = f"{geo_data.city.name}, {geo_data.country.name}"
            except Exception as e:
                logger.error(f"Error fetching geo data for IP {ip_address}: {str(e)}")
                user.last_login_location = "Unknown"

            user.save()

            # ✅ Clear Failed Login Attempts
            failed_attempts.delete()

            messages.success(request, 'Login successful!')
            return redirect('housing')
        else:
            # ✅ Log Failed Login Attempt
            FailedLoginAttempt.objects.create(email=email, ip_address=ip_address, timestamp=now())
            messages.error(request, 'Invalid credentials.')
            return redirect('/housing/#login')

    return redirect('housing')

def send_verification_email(user, request):
    try:
        """Send an email verification link to the user."""
        
        domain = request.get_host()  # Dynamically fetch domain
        protocol = "https" if request.is_secure() else "http"

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{protocol}://{domain}/verify-email/{uid}/{token}/"

        send_mail(
            'Verify Your Email',
            f'Click the link to verify your email: {verification_link}',
            'abrelocationservices@gmail.com',
            [user.email],
            fail_silently=False,
        )
    except Exception as e :
        logger.error(f"Error sending verification email: {str(e)}")
        messages.error(request, 'User not created.')
        redirect('housing')



from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode



def verify_email(request, uidb64, token):
    """Handles email verification when the user clicks the link."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserAccount.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate account
        user.save()
        messages.success(request, "Email verified successfully! You can now log in.")
        return redirect('/housing/#login')
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect('/housing/')


def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('housing')


# Custom login_required decorator with message support
def login_required_with_message(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in first')
            return redirect(f"/housing/#login")
        return func(request, *args, **kwargs)
    return wrapper


from django.http import HttpResponseForbidden
from abrmservices.models import Listing
from abrmservices.views import ListingForm, SearchForm  # Make sure to import your form class
from django.contrib import messages
from django.contrib.messages import get_messages
 
@login_required_with_message
def mydashboard(request, id=None):
    messages_list = get_messages(request)  # Retrieve messages for the request
    user = request.user

    # Initialize variables
    listings = Listing.objects.none()  # Default to no listings
    slistings = Listing.objects.none()
    no_results_message = ''
    form = SearchForm()  # Initialize form to avoid UnboundLocalError

    # Edit existing listing or create a new one
    if id:
        listing = get_object_or_404(Listing, id=id, realtor=user)
        cform = ListingForm(request.POST or None, request.FILES or None, instance=listing)

        if request.method == 'POST' and cform.is_valid():
            cform.save()
            Notification.objects.create(
                user=user,
                message=f"Your listing '{listing.title}' has been successfully updated."
            )
            messages.success(request, 'Listing updated successfully')
            return redirect('mydashboard')

    else:
        cform = ListingForm(request.POST or None, request.FILES or None)
        if request.method == 'POST' and cform.is_valid():
            new_listing = cform.save(commit=False)
            new_listing.realtor = user
            new_listing.save()
            messages.success(request, 'Listing created successfully')
            return redirect('mydashboard')

    # Fetch listings for realtor or superuser
    if user.is_realtor or user.is_superuser:
        listings = Listing.objects.filter(realtor=user)

        # Handle search form submission
        form = SearchForm(request.POST or None)  # Reinitialize form if user is realtor
        if form.is_valid():
            location = form.cleaned_data.get('location')
            home_type = form.cleaned_data.get('category')
            search_description = form.cleaned_data.get('search')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')

            query = Q(realtor=user)  # Always filter by the realtor's email

            if location:
                query &= Q(location__icontains=location)
            if home_type:
                query &= Q(home_type=home_type)
            if search_description:
                query |= Q(description__icontains=search_description)
            if min_price:
                query &= Q(price__gte=int(min_price))
            if max_price:
                query &= Q(price__lte=int(max_price))

            sale_type = request.POST.get('sale_type')
            bedrooms = request.POST.get('bedrooms')

            if sale_type:
                query &= Q(sale_type=sale_type)
            if bedrooms:
                try:
                    query &= Q(bedrooms=int(bedrooms))
                except ValueError:
                    messages.error(request, 'Invalid Bedroom value')

            # Filter listings based on search criteria
            slistings = listings.filter(query)
            if not slistings.exists():
                no_results_message = "No results found."

    return render(request, 'dashboard.html', {
        'listings': listings,
        'form': form,
        'cform': cform,
        'slistings': slistings,
        'messages': messages_list,
        'no_results_message': no_results_message,
        'id': id,
    })


@login_required_with_message
def delete_listing(request, id):
    listing = get_object_or_404(Listing, id=id, realtor=request.user)
    
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted successfully.')
    else:
        messages.error(request, 'Invalid request. Listing not deleted.')

    return redirect('mydashboard')  # Redirect to dashboard after deletion

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@login_required_with_message
def get_listing_data(request, property_id):
    listing = get_object_or_404(Listing, id=property_id, realtor=request.user)
    data = {
        'realtor': listing.realtor,
        'title': listing.title,
        'slug': listing.slug,
        'location': listing.location,
        'zipcode': listing.zipcode,
        'description': listing.description,
        'price': str(listing.price),  # Ensure decimal is stringified
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'sale_type': listing.sale_type,
        'home_type': listing.home_type,
        'main_photo': listing.main_photo.url if listing.main_photo else '',
        'photo_1': listing.photo_1.url if listing.photo_1 else '',
        'photo_2': listing.photo_2.url if listing.photo_2 else '',
        'photo_3': listing.photo_3.url if listing.photo_3 else '',
        'is_published': listing.is_published,
        'date_created': listing.date_created.strftime('%Y-%m-%d %H:%M:%S') if listing.date_created else '',
    }
    return JsonResponse(data)


@login_required_with_message
def chat_list(request):
    user = request.user
    UserAccount = get_user_model()

    # Fetch chats involving the logged-in user
    chats = Chat.objects.filter(Q(user1=user) | Q(user2=user))

    chat_list_data = []
    for chat in chats:
        # Get the last message
        last_message = ChatMessage.objects.filter(chat=chat).order_by('-timestamp').first()

        # Count total unread messages for the logged-in user from other users
        unread_count = ChatMessage.objects.filter(
            ~Q(sender=user),
            chat=chat,
            read=False  # Exclude messages sent by the logged-in user
        ).count()

        # Determine the other user in the chat
        other_user = chat.user1 if chat.user2 == user else chat.user2

        chat_list_data.append({
            'other_user': other_user.name,
            'last_message': last_message.content if last_message else 'No messages yet',
            'timestamp': last_message.timestamp if last_message else None,
            'chat_id': chat.id,
            'unread_count': unread_count
        })

    # Sort chats by the timestamp of the last message
    chat_list_data.sort(key=lambda x: x['timestamp'] or 0, reverse=True)

    return render(request, 'chat_list.html', {'chat_list': chat_list_data})


@login_required_with_message
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Ensure the user is authorized to view this chat
    if request.user not in [chat.user1, chat.user2]:
        messages.error(request, "You are not authorized to view this chat.")
        return redirect('/housing/#login')

    # Fetch chat messages ordered by timestamp
    messages_data = ChatMessage.objects.filter(chat=chat).order_by('timestamp')

    # Mark all unread messages as read for the current user
    messages_data.filter(~Q(sender=request.user), read=False).update(read=True)

    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX request
        response_data = [
            {
                'id': message.id,
                'sender': message.sender.name,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%H:%M'),
            }
            for message in messages_data
        ]
        return JsonResponse({'messages': response_data})

    # Render the chat detail page for non-AJAX requests
    return render(request, 'chat_detail.html', {'chat': chat, 'messages': messages_data})


@login_required_with_message
@csrf_exempt
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)

        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Message content cannot be empty'}, status=400)

        message = ChatMessage.objects.create(
            chat=chat,
            sender=request.user,
            content=content,
            timestamp=now()
        )

        # # Notify the recipient of the new message
        # Notification.objects.create(
        #     user=chat.user1 if chat.user2 == request.user else chat.user2,
        #     message=f"You have a new message from {request.user.name}."
        # )


        return JsonResponse({
            'sender': request.user.name,
            'message': message.content,
            'timestamp': message.timestamp.strftime('%H:%M'),
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required_with_message
def initiate_chat(request, email):
    user = request.user
    User = get_user_model()
    other_user = User.objects.filter(email=email).first()

    existing_chat = Chat.objects.filter(
        Q(user1=other_user, user2=user) | Q(user1=user, user2=other_user)
    ).first()

    if existing_chat:
        return redirect('chat_detail', chat_id=existing_chat.id)

    new_chat = Chat.objects.create(user1=other_user, user2=user)
    ChatMessage.objects.create(
        chat=new_chat,
        sender=other_user,
        content=f"Thank you for contacting {other_user.name}, How can we serve you please?",
        timestamp=now()
    )

    return redirect('chat_detail', chat_id=new_chat.id)



@login_required_with_message
def notifications_page(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required_with_message
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

@login_required_with_message
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return JsonResponse({'success': True})



def mark_all_as_read(request):
    if request.method == "POST":
        # Logic to mark all notifications as read
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from django.core.mail import EmailMessage
from django.utils.timezone import now
from datetime import timedelta
from .models import ChatMessage, Notification  # Make sure to import the relevant model

logger = logging.getLogger(__name__)
import logging
from datetime import timedelta
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.urls import reverse  # For generating URLs
from .models import ChatMessage, Notification

logger = logging.getLogger(__name__)

from django.core.mail import EmailMessage
from django.utils.timezone import now
from django.urls import reverse
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import ChatMessage

@receiver(post_save, sender=ChatMessage)
def send_email_notification(instance, created, **kwargs):
    """
    Sends an email notification when a new ChatMessage is created,
    provided the recipient has been inactive for the last 5 minutes.
    """
    if created:
        try:
            logger.debug("Creating email notification for message ID: %s", instance.id)
            chat = instance.chat
            recipient = chat.user2 if instance.sender == chat.user1 else chat.user1
            offline_threshold = now() - timedelta(minutes=1)

            # Generate a link to view the chat
            chat_url = reverse('chat_detail', args=[chat.id])  # Ensure this view exists

            # Fetch domain from settings or use a default
            domain = getattr(settings, 'SITE_DOMAIN', 'rested-cheerful-skink.ngrok-free.app')
            protocol = "https"  # Assuming HTTPS is used in production

            link = f"{protocol}://{domain}{chat_url}"
            subject = f"New Message from {instance.sender.name}"
            body = f"""
            Hi {recipient.name},

            You have a new message from {instance.sender.name}:

            "{instance.content}"

            Click the link below to view and respond:
            {link}

            Best Regards,
            Your Team
            """

            # Prepare and send the email
            email = EmailMessage(
                subject=subject.strip(),
                body=body.strip(),
                from_email='abrelocationsevices@gmail.com',  # Correct sender email
                to=[recipient.email],
                reply_to=['abrelocationsevices@gmail.com'],  # Correct reply-to email
            )
            email.send(fail_silently=False)
            logger.info("Email sent successfully to %s", recipient.email)
        except Exception as e:
            logger.error("Failed to send email notification: %s", str(e), exc_info=True)
            redirect('housing')


@receiver(post_save, sender=Notification)
def send_email_for_notification(instance, created, **kwargs):
    """
    Sends an email notification when a new Notification is created,
    provided the recipient has been inactive for the last 5 minutes.
    """
    if created:
        try:
            logger.debug("Creating email notification for notification ID: %s", instance.id)
            recipient = instance.user
            offline_threshold = now() - timedelta(minutes=0)

            # Check if the recipient is offline
            if not recipient.last_active or recipient.last_active < offline_threshold:
                # Generate a link to view the notification
                notification_url = reverse('notifications_page')  # Replace with your notification view name
                # Fetch domain from settings or use a default
                domain = getattr(settings, 'SITE_DOMAIN', 'rested-cheerful-skink.ngrok-free.app')
                protocol = "https"  # Assuming HTTPS is used in production

                link = f"{protocol}://{domain}/{notification_url}"

                subject = "New Notification Alert"
                body = f"""
                Hi {recipient.name},

                You have a new notification:

                "{instance.message}"

                Click the link below to view the notification:
                {link}

                Best Regards,
                Your Team
                """

                # Prepare and send the email
                email = EmailMessage(
                    subject=subject.strip(),
                    body=body.strip(),
                    from_email='abrelocationsevices@gmail.com',  # Correct sender email
                    to=[recipient.email],
                    reply_to=['abrelocationsevices@gmail.com'],  # Correct reply-to email
                )
                email.send(fail_silently=False)
                logger.info("Notification email sent successfully to %s", recipient.email)
            else:
                logger.debug("Recipient %s is active; notification email not sent.", recipient.email)
        except Exception as e:
            logger.error("Failed to send notification email: %s", str(e), exc_info=True)
            redirect('housing')
