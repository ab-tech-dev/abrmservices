from .models import Notification
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Chat, ChatMessage


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

    # Edit existing listing or create a new one
    if id:
        listing = get_object_or_404(Listing, id=id, realtor=user.email)
        cform = ListingForm(request.POST or None, request.FILES or None, instance=listing)

        if request.method == 'POST' and cform.is_valid():
            # Retain existing photos if no new file is uploaded
            if not cform.cleaned_data.get('main_photo'):
                cform.instance.main_photo = listing.main_photo
            if not cform.cleaned_data.get('photo_1'):
                cform.instance.photo_1 = listing.photo_1
            if not cform.cleaned_data.get('photo_2'):
                cform.instance.photo_2 = listing.photo_2
            if not cform.cleaned_data.get('photo_3'):
                cform.instance.photo_3 = listing.photo_3

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
            new_listing.realtor = user.email
            new_listing.save()
            messages.success(request, 'Listing created successfully')
            return redirect('mydashboard')

    # Fetch listings for realtor or superuser
    if user.is_realtor or user.is_superuser:
        listings = Listing.objects.filter(realtor=user.email)

        # Handle search form submission
        form = SearchForm(request.POST or None)
        if form.is_valid():
            location = form.cleaned_data.get('location')
            home_type = form.cleaned_data.get('category')
            search_description = form.cleaned_data.get('search')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')

            query = Q(realtor=user.email)  # Always filter by the realtor's email

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
    listing = get_object_or_404(Listing, id=id, realtor=request.user.email)
    
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
    listing = get_object_or_404(Listing, id=property_id, realtor=request.user.email)
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

        # Notify the recipient of the new message
        Notification.objects.create(
            user=chat.user1 if chat.user2 == request.user else chat.user2,
            message=f"You have a new message from {request.user.name}."
        )


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
from .models import ChatMessage  # Make sure to import the relevant model

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ChatMessage)
def send_email_notification(sender, instance, created, **kwargs):
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

            # Check if the recipient is offline
            if not recipient.last_active or recipient.last_active < offline_threshold:
                subject = f"New Message from {instance.sender.name}"
                body = f"""
                Hi {recipient.name},

                You have a new message from {instance.sender.name}:

                "{instance.content}"

                Please visit your notification page to respond.

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
            else:
                logger.debug("Recipient %s is active; email not sent.", recipient.email)
        except Exception as e:
            logger.error("Failed to send email notification: %s", str(e), exc_info=True)
            raise e
