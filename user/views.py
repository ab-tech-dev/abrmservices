
from django.contrib.auth import get_user_model
User = get_user_model()
from django.shortcuts import render



def listings(request):
    return render(request, 'index.html')


# Import statements...

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from abrmservices.models import Listing
from abrmservices.views import ListingForm, SearchForm  # Make sure to import your form class
from django.contrib import messages
from django.contrib.messages import get_messages
from django.db.models import Q
 

try:
    @login_required
    def mydashboard(request, id=None):
        messages_list = get_messages(request)  # Retrieve messages for the request
        user = request.user

        # Edit existing listing if property_id is provided, else create a new listing
        if id:
            listing = get_object_or_404(Listing, id=id, realtor=user.email)
            cform = ListingForm(request.POST, request.FILES, instance=listing)
            # Retain existing photos if no new file is uploaded
            if not cform.cleaned_data.get('main_photo'):
                cform.instance.main_photo = listing.main_photo
            if not cform.cleaned_data.get('photo_1'):
                cform.instance.photo_1 = listing.photo_1
            if not cform.cleaned_data.get('photo_2'):
                cform.instance.photo_2 = listing.photo_2
            if not cform.cleaned_data.get('photo_3'):
                cform.instance.photo_3 = listing.photo_3
            if cform.is_valid():
                cform.save()

        else:
            cform = ListingForm(request.POST or None, request.FILES or None)
            cform.fields['realtor'].initial = user.email
            if cform.is_valid():
                cform.save()

        if user.is_realtor or user.is_superuser:
            # Retrieve listings only for the logged-in realtor
            listings = Listing.objects.filter(realtor=user.email)
            slistings = Listing.objects.none()  # Initialize `slistings` as an empty queryset
            no_results_message = ''  # Initialize `no_results_message` to prevent UnboundLocalError

            form = SearchForm(request.POST or None)

            # Listing Form Process
            if cform.is_valid():
                listing = cform.save(commit=False)
                listing.realtor = user.email  # Set the realtor to the logged-in user's email
                listing.save()
                
                if id:
                    messages.success(request, 'Listing updated successfully')
                else:
                    messages.success(request, 'Listing created successfully')
                return redirect('mydashboard')
            else:
                if cform.errors:
                    messages.error(request, 'Invalid form value: {}'.format(cform.errors))

            # Process the search form
            if form.is_valid():
                location = form.cleaned_data['location']
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

                # Get filtered listings
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
                'id': id,  # Pass id for conditional form handling in template
            })

except Exception:
    HttpResponseForbidden("You do not have permission to access this page.")



@login_required
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

@login_required
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


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from abrmservices.models import Listing
from django.db import models





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Chat, ChatMessage
from django.contrib.auth import get_user_model

@login_required
def chat_list(request):
    user = request.user  # The logged-in user
    user1 = get_user_model().objects.get(is_superuser=True)  # The superuser

    # Fetch chats based on the logged-in user type
    if user.is_superuser:
        # Superuser sees all chats with users
        chats = Chat.objects.filter(Q(user1=user1) | Q(user2=user1))
    else:
        # Normal user sees chats with the superuser
        chats = Chat.objects.filter(
            (Q(user1=user1) & Q(user2=user)) | (Q(user1=user) & Q(user2=user1))
        )

    chat_list = []

    for chat in chats:
        last_message = ChatMessage.objects.filter(chat=chat).order_by('-timestamp').first()
        chat_list.append({
            'other_user': chat.user1.name if chat.user2 == user else chat.user2.name,
            'last_message': last_message.content if last_message else 'No messages yet',
            'timestamp': last_message.timestamp if last_message else None,
            'chat_id': chat.id
        })

    # Sort the chat list by timestamp (most recent first)
    chat_list.sort(key=lambda x: x['timestamp'] or 0, reverse=True)

    is_superuser = user.is_superuser
    return render(request, 'chat_list.html', {'chat_list': chat_list, 'is_superuser': is_superuser})




@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Ensure the logged-in user is part of this chat
    if request.user not in [chat.user1, chat.user2]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Fetch all messages for this chat
    messages = ChatMessage.objects.filter(chat=chat).order_by('timestamp')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX
        messages_data = [
            {
                'sender': message.sender.name,  # Use sender's username
                'content': message.content,
                'timestamp': message.timestamp.strftime('%H:%M')  # Format timestamp
            }
            for message in messages
        ]
        return JsonResponse({'messages': messages_data})

    # Default behavior: Render the HTML template
    return render(request, 'chat_detail.html', {
        'chat': chat,
        'messages': messages
    })


from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

@login_required
@csrf_exempt
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=chat_id)

        # Ensure the logged-in user is part of this chat
        if request.user not in [chat.user1, chat.user2]:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({'error': 'Message content cannot be empty'}, status=400)

        # Create the message
        message = ChatMessage.objects.create(
            chat=chat,
            sender=request.user,
            content=content,
            timestamp=now()
        )

        return JsonResponse({
            'sender': request.user.name,
            'message': message.content,
            'timestamp': message.timestamp.strftime('%H:%M')
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def initiate_chat_with_superuser(request):
    user = request.user  # This is the logged-in user (user2)
    user1 = get_user_model().objects.get(is_superuser=True)  # Get the superuser (user1)

    # Check if a chat already exists between the logged-in user and the superuser
    existing_chat = Chat.objects.filter(
        (models.Q(user1=user1) & models.Q(user2=user)) | (models.Q(user1=user) & models.Q(user2=user1))
    ).first()

    if existing_chat:
        # If a chat already exists, redirect to that chat
        # Send a welcome message or predefined message to start the conversation
        welcome_message = "Hello, how can I assist you today?"
        ChatMessage.objects.create(
            chat=existing_chat,
            sender=user,
            content=welcome_message,
            timestamp=now()
        )
        return redirect('chat_detail', chat_id=existing_chat.id)

    # If no chat exists, create a new chat
    new_chat = Chat.objects.create(user1=user1, user2=user)

    # Send an initial message after creating the new chat
    initial_message = "Hello, how can I assist you today?"
    ChatMessage.objects.create(
        chat=new_chat,
        sender=user,
        content=initial_message,
        timestamp=now()
    )

    # Redirect to the newly created chat
    return redirect('chat_detail', chat_id=new_chat.id)

