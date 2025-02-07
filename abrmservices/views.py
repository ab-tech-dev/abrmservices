from django.shortcuts import render, redirect
from .models import Listing
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django import forms
import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
# from .models import House
# Create your views here.
# from dotenv import load_dotenv

# load_dotenv()


from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector

from django import forms
from django.db.models import Q
from .models import Listing
from django import forms

# Define the available search fields and their corresponding choices
SEARCH_FIELDS_CHOICES = [
    ('address', 'Address'),
    ('bathrooms', 'Bathrooms'),
    ('bedrooms', 'Bedrooms'),
    ('city', 'City'),
    ('description', 'Description'),
    ('home_type', 'Home Type'),
    ('sale_type', 'Sale Type'),
    ('state', 'State'),

]



from django.db.models import Q
from .models import Listing



from django import forms

class SearchForm(forms.Form):

    
    CATEGORY_CHOICESA = [
        ('50000', '50000'),
        ('100000', '100000'),
        ('200000', '200000'),
        ('300000', '300000'),
        ('400000', '400000'),
        ('500000', '500000'),
        ('600000', '600000'),
    ]

    CATEGORY_CHOICESB = [
        ('500000', '500000'),
        ('1000000', '1000000'),
        ('5000000', '5000000'),
        ('10000000', '10000000'),
        ('50000000', '50000000'),
        ('100000000', '100000000'),
        ('1000000000', '1000000000'),
        ('10000000000', '10000000000'),
        ('100000000000', '100000000000'),
    ]
    
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'id_location',
            'placeholder': 'Enter a location',
            'class': 'input-field stop'
        })
    )


    min_price = forms.ChoiceField(
        label='Min Price:',
        choices=CATEGORY_CHOICESA,
        widget=forms.Select(attrs={'class': 'dropdown-list'})
    )

    max_price = forms.ChoiceField(
        label='Max Price:',
        choices=CATEGORY_CHOICESB,
        widget=forms.Select(attrs={'class': 'dropdown-list'})
    )

    # Additional fields can be added as needed
    sale_type = forms.ChoiceField(choices=[('For Sale', 'For Sale'), ('For Rent', 'For Rent')], required=False)



from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Layout
from .models import Listing, Photo

class ListingForm(forms.ModelForm):
    SALE_TYPE_CHOICES = [
        ('For Sale', 'For Sale'),
        ('For Rent', 'For Rent'),
    ]
    
    HOME_TYPE_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condo'),
        ('townhome', 'Townhome'),
    ]
    
    # Fields to handle multiple uploads
    main_photo = forms.ImageField(label='Main Photo')
    additional_photos = forms.ImageField(widget=forms.ClearableFileInput(attrs={}), required=False)
    video = forms.FileField(required=False)
    bathroom_photos = forms.ImageField(widget=forms.ClearableFileInput(attrs={}), required=False)
    toilet_photos = forms.ImageField(widget=forms.ClearableFileInput(attrs={}), required=False)



    class Meta:
        model = Listing
        fields = [
            'title', 'location', 'bedrooms', 'bathrooms', 'sale_type', 
            'home_type', 'main_photo', 'video', 'price', 'additional_photos', 
            'bathroom_photos', 'toilet_photos'
        ]

    # Basic fields with crispy_forms styling
    title = forms.CharField(
        label='Title',
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter property description',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    location = forms.CharField(
        label='Location',
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Location',
            'class': 'form-control stop',
            'id': 'id_location',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    bedrooms = forms.IntegerField(
        label='Bedrooms',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Number of Bedrooms',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    bathrooms = forms.IntegerField(
        label='Bathrooms',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Number of Bathrooms',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    sale_type = forms.ChoiceField(
        label='Sale Type',
        choices=SALE_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    home_type = forms.ChoiceField(
        label='Home Type',
        choices=HOME_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    # Photo and Video fields with 'multiple' support
    main_photo = forms.ImageField(
        label='Main Photo',
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'style': 'margin-top: 5px;',
        })
    )

    video = forms.FileField(
        label='Video File (Optional)',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'style': 'margin-top: 5px;',
        })
    )

    price = forms.DecimalField(
        label='Price',
        max_digits=13,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter Price',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    # Custom form helper with crispy_forms layout
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('title'),
            Field('location'),
            Field('bedrooms'),
            Field('bathrooms'),
            Field('sale_type'),
            Field('home_type'),
            Field('main_photo'),
            Field('video'),
            Field('price'),
            Field('additional_photos', data_multiple_files="true"),  # Allow multiple files for additional_photos
            Field('bathroom_photos', data_multiple_files="true"),  # Multiple bathroom photos
            Field('toilet_photos', data_multiple_files="true"),  # Multiple toilet photos
            Submit('submit', 'Submit')
        )

from django.shortcuts import render, redirect
from user.forms import RegisterForm, LoginForm
from user.models import UserAccount, Chat, ChatMessage, Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

def housing(request):
    # Initial setup
    properties = Listing.objects.all()
    no_results_message = ''
    listings = Listing.objects.none()
    user = request.user if request.user.is_authenticated else None

    # Notifications and unread messages
    if user:
        unread_notifications = Notification.objects.filter(user=user, is_read=False)
        unread_notifications_count = unread_notifications.count()

        chats = Chat.objects.filter(Q(user1=user) | Q(user2=user))
        unread_messages = ChatMessage.objects.filter(
            ~Q(sender=user),
            chat__in=chats,
            read=False
        )
        unread_senders = unread_messages.values('sender').distinct()
        unread_users_count = unread_senders.count()
    else:
        unread_notifications_count = 0
        unread_users_count = 0
        chats = []

    # Forms
    form = SearchForm(request.POST or None)
    cform = ListingForm(request.POST or None, request.FILES or None)
    register_form = RegisterForm(request.POST or None)
    login_form = LoginForm(request.POST or None)

    # Process Listing Form (cform)
    if cform.is_valid() and 'create_listing' in request.POST:
        cform.instance.realtor = User(id=request.user.id)

        # Handle the file uploads (if needed)
        cform.main_photo = request.FILES.get('main_photo')
        cform.video = request.FILES.get('video')

        listing = cform.save(commit=False)
        listing.realtor = request.user
        listing.save()

        # Handle the file uploads for ManyToMany fields
        bathroom_photos = request.FILES.getlist('bathroom_photos')
        for photo in bathroom_photos:
            photo_instance = Photo.objects.create(image=photo)
            listing.bathroom_photos.add(photo_instance)

        toilet_photos = request.FILES.getlist('toilet_photos')
        for photo in toilet_photos:
            photo_instance = Photo.objects.create(image=photo)
            listing.toilet_photos.add(photo_instance)

        additional_photos = request.FILES.getlist('additional_photos')
        for photo in additional_photos:
            photo_instance = Photo.objects.create(image=photo)
            listing.additional_photos.add(photo_instance)

        listing.save()

        messages.success(request, "Listing created successfully!")
        Notification.objects.create(
            user=user,
            message=f"Your listing '{listing.title}' has been successfully created."
        )
        return redirect('housing')
    

    # Process Search Form (form)
    # Process Search Form (form)
    if form.is_valid() and 'search' in request.POST:
        location = form.cleaned_data.get('location')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')

        query = Q()  # Start with an empty query object

        # Apply location filter if it's provided
        if location:
            query &= Q(location__icontains=location)  # Use '&' to combine conditions

        # Apply min_price filter if it's provided and valid
        if min_price not in [None, '']:  # Check for None or empty string
            try:
                min_price = float(min_price)
                query &= Q(price__gte=min_price)  # Use '&' to combine conditions
            except (ValueError, TypeError):
                # Handle invalid min_price (e.g., non-numeric input)
                no_results_message = "Invalid minimum price."

        # Apply max_price filter if it's provided and valid
        if max_price not in [None, '']:  # Check for None or empty string
            try:
                max_price = float(max_price)
                query &= Q(price__lte=max_price)  # Use '&' to combine conditions
            except (ValueError, TypeError):
                # Handle invalid max_price (e.g., non-numeric input)
                no_results_message = "Invalid maximum price."

        # Ensure min_price is not greater than max_price
        if min_price and max_price and min_price > max_price:
            no_results_message = "Minimum price cannot be greater than maximum price."

        # Apply sale_type filter if it's provided
        sale_type = request.POST.get('sale_type')  # Directly from POST as it might not be in cleaned_data
        if sale_type:
            query &= Q(sale_type=sale_type)  # Apply sale_type condition

        # Execute the query only if no errors were encountered
        if not no_results_message:
            listings = Listing.objects.filter(query)

            # Check if any results were found
            if not listings.exists():
                no_results_message = "No results found."
                form = SearchForm()  # It's better to instantiate the form empty for re-rendering in the template



    # Pass data to template
    return render(request, 'index.html', {
        'form': form,
        'login_form': login_form,
        'register_form': register_form,
        'listings': listings,
        'no_results_message': no_results_message,
        'cform': cform,
        'is_logged_in': request.user.is_authenticated,
        'unread_users_count': unread_users_count,
        'properties': properties,
        'unread_notifications_count': unread_notifications_count,
        'user': user,
    })


def main(request):
    return render(request, 'main.html')

def about(request):
    return render(request, 'about.html')


def termsandconditions(request):
    return render(request, 'termsandconditions.html')


def submitmyform(request):
    content = {
        "Status": "Successfully Delivered",
        "Message": "Your request has been successfully delivered, and you will get a response as soon as possible"
    }
    return JsonResponse(content)

def contact(request):
    if request.method == "POST":
        first_name = request.POST.get('Cfirst_name', '')
        last_name = request.POST.get('Clast_name', '')
        email = request.POST.get('Cemail', '')
        phone = request.POST.get('Cphone', '')
        text_area = request.POST.get('Ctext_area', '')

        send_mail(
            'CONTACT MESSAGE',
            f'From: {first_name} {last_name}\nEmail: {email}\nPhone: {phone}\nMessage: {text_area}',
            {email},
            ['abrelocationservices@gmail.com'],
            fail_silently=False
        )

    return render(request, 'contact.html')

from django.core.mail import EmailMessage

from django.core.mail import EmailMessage

def movingServices(request):
    if request.method == "POST":
        adressfrom = request.POST.get('adressfrom', '')
        adressto = request.POST.get('adressto', '')
        apartment_from = request.POST.get('apartment_from', '')
        apartment_to = request.POST.get('apartment_to', '')
        bedroom_from = request.POST.get('bedroom_from', '')
        bedroom_to = request.POST.get('bedroom_to', '')
        floor_from = request.POST.get('floor_from', '')
        floor_to = request.POST.get('floor_to', '')
        Mfirst_name = request.POST.get('Mfirst_name', '')
        Mlast_name = request.POST.get('Mlast_name', '')
        Memail = request.POST.get('Memail', '')
        Mphone = request.POST.get('Mphone', '')
        Mtext_area = request.POST.get('Mtextarea', '')
        Mdate = request.POST.get('Mdate', False)
        Mtime = request.POST.get('Mtime', False)

        # Collect checkbox values with the same name
        move_checkbox = request.POST.getlist('move_service')
        string_mcheckbox = ", ".join(move_checkbox) if move_checkbox else "No services selected"

        # Collect uploaded files
        uploaded_files = request.FILES.getlist('file') 

        # Compose the email content
        subject = 'MOVING REQUEST'
        body = (
            f'From: {Mfirst_name} {Mlast_name}\n'
            f'Email: {Memail}\n'
            f'Phone: {Mphone}\n\n'
            f'Moving from {adressfrom} to {adressto}\n\n'
            f'From a {apartment_from} to a {apartment_to}\n'
            f'From a {bedroom_from} bedroom to a {bedroom_to} bedroom\n'
            f'From the {floor_from} to the {floor_to}\n\n'
            f'Service(s) required: {string_mcheckbox}\n'
            f'Message: {Mtext_area}\n\n'
            f'I want these services on {Mdate} by {Mtime}\n\n'
        )

        # Create the EmailMessage object
        email = EmailMessage(
            subject,
            body,
            Memail,  # From email
            ['abrelocationservices@gmail.com'],  # To email
            reply_to=[Memail],  # Reply-To email
            headers={"Message-ID": "moving-request"},  # Custom headers
        )

        # Attach the uploaded files
        for uploaded_file in uploaded_files:
            email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)

        # Send the email
        email.send(fail_silently=False)

    return render(request, 'moving-services.html')




def cleaningServices(request):
    if request.method == "POST":
        try:
            # Collect form data
            CLfirst_name = request.POST.get('CLfirst_name', '')
            CLlast_name = request.POST.get('CLlast_name', '')
            CLemail = request.POST.get('CLemail', '')
            CLphone = request.POST.get('CLphone', '')
            CLtext_area = request.POST.get('CLtextarea', '')
            CLselect = request.POST.get('CLselect', False)
            CLdate = request.POST.get('CLdate', False)
            CLtime = request.POST.get('CLtime', False)

            # Collect checkbox values with the same name
            clean_checkbox = request.POST.getlist('clean_service')
            string_checkbox = ", ".join(clean_checkbox) if clean_checkbox else "No services selected"

            # Collect uploaded files
            uploaded_files = request.FILES.getlist('file') 

            # Compose the email content
            subject = 'CLEANING REQUEST'
            body = (
                f'From: {CLfirst_name} {CLlast_name}\n'
                f'Email: {CLemail}\n'
                f'Phone: {CLphone}\n\n'
                f'Number of Rooms: {CLselect}\n\n'
                f'Service(s) required: {string_checkbox}\n'
                f'Message: {CLtext_area}\n\n'
                f'I want these services on {CLdate} by {CLtime}\n\n'
            )

            # Create the EmailMessage object
            email = EmailMessage(
                subject,
                body,
                CLemail,  # From email
                ['abrelocationservices@gmail.com'],  # To email
                reply_to=[CLemail],  # Reply-To email
                headers={"Message-ID": "cleaning-request"},  # Custom headers
            )

            # Attach the uploaded files
            for uploaded_file in uploaded_files:
                email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)

            # Send the email
            email.send(fail_silently=False)

        except Exception as e:
            # Capture the error message
            error_message = str(e)
            return JsonResponse({'error': f'Failed to send email. Error: {error_message}'}, status=500)

    return render(request, 'cleaning.html')



def getaquote(request):
    if request.method == "POST":
         # Collect form data
        CLfirst_name = request.POST.get('CLfirst_name', '')
        CLlast_name = request.POST.get('CLlast_name', '')
        CLemail = request.POST.get('CLemail', '')
        CLphone = request.POST.get('CLphone', '')
        CLtext_area = request.POST.get('CLtextarea', '')
        CLselect = request.POST.get('CLselect', False)
        CLdate = request.POST.get('CLdate', False)
        CLtime = request.POST.get('CLtime', False)

        # Collect checkbox values with the same name
        clean_checkbox = request.POST.getlist('clean_service')
        string_checkbox = ", ".join(clean_checkbox) if clean_checkbox else "No services selected"

        # Collect uploaded files
        uploaded_files = request.FILES.getlist('file') 

        # Compose the email content
        subject = 'CLEANING REQUEST'
        body = (
            f'From: {CLfirst_name} {CLlast_name}\n'
            f'Email: {CLemail}\n'
            f'Phone: {CLphone}\n\n'
            f'Number of Rooms: {CLselect}\n\n'
            f'Service(s) required: {string_checkbox}\n'
            f'Message: {CLtext_area}\n\n'
            f'I want these services on {CLdate} by {CLtime}\n\n'
        )

        # Create the EmailMessage object
        email = EmailMessage(
            subject,
            body,
            CLemail,  # From email
            ['abrelocationservices@gmail.com'],  # To email
            reply_to=[CLemail],  # Reply-To email
            headers={"Message-ID": "cleaning-request"},  # Custom headers
        )

        # Attach the uploaded files
        for uploaded_file in uploaded_files:
            email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)

        # Send the email
        email.send(fail_silently=False)

        # Handle moving request
        adressfrom = request.POST.get('adressfrom', '')
        adressto = request.POST.get('adressto', '')
        apartment_from = request.POST.get('apartment_from', '')
        apartment_to = request.POST.get('apartment_to', '')
        bedroom_from = request.POST.get('bedroom_from', '')
        bedroom_to = request.POST.get('bedroom_to', '')
        floor_from = request.POST.get('floor_from', '')
        floor_to = request.POST.get('floor_to', '')
        Mfirst_name = request.POST.get('Mfirst_name', '')
        Mlast_name = request.POST.get('Mlast_name', '')
        Memail = request.POST.get('Memail', '')
        Mphone = request.POST.get('Mphone', '')
        Mtext_area = request.POST.get('Mtextarea', '')
        Mdate = request.POST.get('Mdate', False)
        Mtime = request.POST.get('Mtime', False)

        # Collect checkbox values with the same name
        move_checkbox = request.POST.getlist('move_service')
        string_mcheckbox = ", ".join(move_checkbox) if move_checkbox else "No services selected"

        # Collect uploaded files
        uploaded_files = request.FILES.getlist('file') 

        # Compose the email content
        subject = 'MOVING REQUEST'
        body = (
            f'From: {Mfirst_name} {Mlast_name}\n'
            f'Email: {Memail}\n'
            f'Phone: {Mphone}\n\n'
            f'Moving from {adressfrom} to {adressto}\n\n'
            f'From a {apartment_from} to a {apartment_to}\n'
            f'From a {bedroom_from} bedroom to a {bedroom_to} bedroom\n'
            f'From the {floor_from} to the {floor_to}\n\n'
            f'Service(s) required: {string_mcheckbox}\n'
            f'Message: {Mtext_area}\n\n'
            f'I want these services on {Mdate} by {Mtime}\n\n'
        )

        # Create the EmailMessage object
        email = EmailMessage(
            subject,
            body,
            Memail,  # From email
            ['abrelocationservices@gmail.com'],  # To email
            reply_to=[Memail],  # Reply-To email
            headers={"Message-ID": "moving-request"},  # Custom headers
        )

        # Attach the uploaded files
        for uploaded_file in uploaded_files:
            email.attach(uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)

        # Send the email
        email.send(fail_silently=False)

    return render(request, 'get-a-quote.html')


