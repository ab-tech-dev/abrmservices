from django.shortcuts import render, redirect
from .models import Listing


from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django import forms
import datetime
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
    SEARCH_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('offices', 'Offices'),
        ('townhome', 'Townhome'),
        ('estate_house', 'A house in an estate'),  # Added option
    ]
    
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
    search = forms.CharField(
        label='Search: *',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Add your decription',
            'required': 'required',
            'class': 'input-field'
        })
    )
    
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'id_location',
            'placeholder': 'Enter a location',
            'class': 'input-field stop'
        })
    )

    category = forms.ChoiceField(
        label='Select Categories',
        choices=SEARCH_CHOICES,
        widget=forms.Select(attrs={'class': 'dropdown-list'})
    )

    min_price = forms.ChoiceField(
        label='Min Price:',
        choices= CATEGORY_CHOICESA,
        widget=forms.Select(attrs={'class': 'dropdown-list'})
    )

    max_price = forms.ChoiceField(
        label='Max Price:',
        choices=CATEGORY_CHOICESB,
        widget=forms.Select(attrs={'class': 'dropdown-list'})
    )




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

    class Meta:
        model = Listing
        fields = [
            'realtor', 'title', 'slug', 'location', 'zipcode',
            'description', 'price', 'bedrooms', 'bathrooms', 'sale_type',
            'home_type', 'main_photo', 'photo_1', 'photo_2', 'photo_3',
            'is_published', 'date_created'
        ]

    realtor = forms.EmailField(
        label='Realtor Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter Realtor Email',
            'required': 'required',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    title = forms.CharField(
        label='Title',
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Title',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    slug = forms.CharField(
        label='Slug',
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Unique Identifier (Slug)',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if ' ' in slug:
            raise forms.ValidationError("Slug cannot contain spaces.")
        return slug.replace(' ', '-').lower()

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

    zipcode = forms.CharField(
        label='Zip Code',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Zip Code',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    def clean_zipcode(self):
        zipcode = self.cleaned_data.get('zipcode')
        if not zipcode.isnumeric() or len(zipcode) < 5:
            raise forms.ValidationError("Zip code must be at least 5 digits long and contain only numbers.")
        return zipcode

    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={
            'rows': 5,
            'cols': 17,
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; width: auto;font-size: 16px;',
            'placeholder': 'Enter Description',
            'class': 'form-control',
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

    bedrooms = forms.IntegerField(
        label='Bedrooms',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Number of Bedrooms',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    def clean_bedrooms(self):
        bedrooms = self.cleaned_data.get('bedrooms')
        if bedrooms < 0:
            raise forms.ValidationError("Number of bedrooms cannot be negative.")
        return bedrooms

    bathrooms = forms.IntegerField(
        label='Bathrooms',
        widget=forms.NumberInput(attrs={
            'placeholder': 'Number of Bathrooms',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
        })
    )

    def clean_bathrooms(self):
        bathrooms = self.cleaned_data.get('bathrooms')
        if bathrooms < 0:
            raise forms.ValidationError("Number of bathrooms cannot be negative.")
        return bathrooms

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

    main_photo = forms.ImageField(
        label='Main Photo',
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'style': 'margin-top: 5px;',
        })
    )

    photo_1 = forms.ImageField(
        label='Photo 1',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'style': 'margin-top: 5px;',
        })
    )

    photo_2 = forms.ImageField(
        label='Photo 2',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'style': 'margin-top: 5px;',
        })
    )

    photo_3 = forms.ImageField(
        label='Photo 3',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'style': 'margin-top: 5px;',
        })
    )

    is_published = forms.BooleanField(
        label='Is Published?',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'style': 'margin-top: 10px;',
        })
    )

    date_created = forms.DateTimeField(
        label='Date Created',
        initial=datetime.datetime.now,
        widget=forms.DateTimeInput(attrs={
            'placeholder': 'YYYY-MM-DD HH:MM:SS',
            'class': 'form-control',
            'style': 'padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px;',
            'value': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }),
    )


from django.shortcuts import render, redirect
from user.forms import RegisterForm, LoginForm
from user.models import UserAccount
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
# from listings.models import Listing
# from listings.forms import SearchForm, ListingForm


def housing(request):
    no_results_message = ''
    listings = Listing.objects.none()

    # Forms
    form = SearchForm(request.POST or None)
    cform = ListingForm(request.POST, request.FILES or None)
    register_form = RegisterForm(request.POST or None)
    login_form = LoginForm(request.POST or None)

    # Logout Process
    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        messages.success(request, 'Logged out successfully')
        return redirect('housing')  # Redirect to the housing page after logout

    # Registration Process
    if register_form.is_valid():
        try:
            name = register_form.cleaned_data['name']
            email = register_form.cleaned_data['email'].lower()
            password = register_form.cleaned_data['password']
            re_password = register_form.cleaned_data['re_password']
            is_realtor = register_form.cleaned_data['is_realtor']

            if password == re_password:
                if not UserAccount.objects.filter(email=email).exists():
                    if is_realtor:
                        user = UserAccount.objects.create_realtor(name=name, email=email)
                    else:
                        user = UserAccount.objects.create_user(name=name, email=email)
                    user.set_password(password)
                    user.save()
                    messages.success(request, 'Account created successfully')
                    return redirect('housing')
                else:
                    messages.error(request, 'Email already exists')
            else:
                messages.error(request, 'Passwords do not match')
        except Exception as e:
            messages.error(request, f'Error in registration: {e}')

    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        messages.success(request, 'Logged out successfully')
        return redirect('housing') 

    # Login Process
    if login_form.is_valid():
        try:
            email = login_form.cleaned_data['email'].lower()
            password = login_form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Login successful')
                return redirect('housing')  # Refresh the page to confirm login status
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('/housing/#login')
        except Exception as e:
            messages.error(request, f'Login error: {e}')

    # Listing Form Process
    if cform.is_valid():
        listing = cform.save(commit=False)
        listing.realtor = request.user.email  # Override realtor with logged-in user's email
        listing.save()

        messages.success(request, 'Listing saved successfully')
        return redirect('housing')  # Redirect to the listing page after saving

    if form.is_valid():  # Only process if the form is valid
        location = form.cleaned_data['location']
        home_type = form.cleaned_data.get('category')  # Get the home type (category from form)
        search_description = form.cleaned_data.get('search')  # Get the search field description
        min_price = form.cleaned_data.get('min_price')  # Get the minimum price from form
        max_price = form.cleaned_data.get('max_price')  # Get the maximum price from form

        # Filtering based on optional fields in the model
        query = Q()

        if location:
            query &= Q(location__icontains=location)
        if home_type:
            query &= Q(home_type=home_type)  # Match home_type in Listing model
        if search_description:
            query |= Q(description__icontains=search_description)  # Match description
        if min_price:
            query &= Q(price__gte=int(min_price))  # price >= min_price
        if max_price:
            query &= Q(price__lte=int(max_price))  # price <= max_price

        # Retrieve additional query parameters from the model's attributes
        sale_type = request.POST.get('sale_type')  # Check for `sale_type` field in GET parameters
        bedrooms = request.POST.get('bedrooms')  # Check for `bedrooms` field in GET parameters

        if sale_type:
            query &= Q(sale_type=sale_type)  # Filter by sale_type if provided
        if bedrooms:
            try:
                query &= Q(bedrooms=int(bedrooms))  # Convert to int and filter by number of bedrooms
            except ValueError:
                pass  # Ignore invalid bedroom inputs for filtering

        # Print the query details to the terminal for debugging

        # Execute query and get the filtered results
        listings = Listing.objects.filter(query).filter(is_published=True)

        # Set no_results_message if no listings found
        if not listings.exists():
            no_results_message = "No results found."

    # Pass no_results_message to the template context
    return render(request, 'index.html', {
        'form': form,
        'login_form': login_form,
        'register_form': register_form,
        'listings': listings,
        'no_results_message': no_results_message,  # Pass the message to the template
        'cform': cform,
        'is_logged_in': request.user.is_authenticated,  # Pass user authentication status
    })

# from user.forms import RegisterForm, LoginForm
# from user.models import UserAccount, UserAccountManager
# from django.contrib.auth import authenticate, login
# from django.contrib import messages

# def housing(request):
    
#     user = request.user
#     no_results_message = ''
#     form = SearchForm(request.POST or None)  # Use GET request to retrieve query parameters
#     listings = Listing.objects.none() 
#     # Start with an empty QuerySet
#     cform = ListingForm(request.POST, request.FILES)


#     register_form = RegisterForm(request.POST)
    
#     if register_form.is_valid():
#         try:
#             # Extract cleaned data from the valid form
#             name = register_form.cleaned_data.get('name')
#             email = register_form.cleaned_data.get('email').lower()
#             password = register_form.cleaned_data.get('password')
#             re_password = register_form.cleaned_data.get('re_password')
#             is_realtor = register_form.cleaned_data.get('is_realtor')

#             # Check if passwords match and meet length requirements
#             if password == re_password and len(password) >= 8:
#                 # Check if the email already exists in the database
#                 if not UserAccount.objects.filter(email=email).exists():
#                     # Determine if the user is a realtor or a regular user
#                     if is_realtor:
#                         user = UserAccount.objects.create_realtor(name=name, email=email)
#                         user.set_password(password)
#                         user.save()
#                         messages.success(request, 'Realtor account created successfully')
#                     else:
#                         user = UserAccount.objects.create_user(name=name, email=email)
#                         user.set_password(password)
#                         user.save()
#                         messages.success(request, 'User account created successfully')

#                     # Redirect to the login page after successful registration
#                     return redirect('housing/#login')

#                 else:
#                     messages.error(request, 'User with this email already exists')

#             elif len(password) < 8:
#                 messages.error(request, 'Password must be at least 8 characters in length')

#             else:
#                 messages.error(request, 'Passwords do not match')

#         except ValueError as e:
#             messages.error(request, f'ValueError: {str(e)}')

#         except Exception as e:
#             messages.error(request, f'Something went wrong when registering an account: {str(e)}')

    
#     else:
#         # Instantiate a blank form if it's not a POST request
#         register_form = RegisterForm()

#     # Render the registration template with the form


#     login_form = LoginForm(request.POST or None)

#     if login_form.is_valid():
#         try:
#             # Extract email and password from the cleaned form data
#             email = login_form.cleaned_data.get('email').lower()
#             password = login_form.cleaned_data.get('password')

#             # Authenticate the user
#             user = authenticate(request, email=email, password=password)

#             if user is not None:
#                 if user.is_active:
#                     # Log the user in if authentication succeeds
#                     login(request, user)
#                     messages.success(request, 'Login successful')
#                     return redirect('dashboard')
#                 else:
#                     # Handle the case where the user is deactivated
#                     messages.error(request, 'User account is deactivated')
#             else:
#                 # Handle invalid credentials
#                 messages.error(request, 'Invalid email or password')

#         except Exception as e:
#             # Catch any unexpected errors
#             messages.error(request, f'Something went wrong: {str(e)}')

#     if cform.is_valid():
#         cform.save()
#         return redirect('listings')  # Redirect to a view that lists all listings or a success page




#     if form.is_valid():  # Only process if the form is valid
#         location = form.cleaned_data['location']
#         home_type = form.cleaned_data.get('category')  # Get the home type (category from form)
#         search_description = form.cleaned_data.get('search')  # Get the search field description
#         min_price = form.cleaned_data.get('min_price')  # Get the minimum price from form
#         max_price = form.cleaned_data.get('max_price')  # Get the maximum price from form

#         # Filtering based on optional fields in the model
#         query = Q()

#         if location:
#             query &= Q(location__icontains=location)
#         if home_type:
#             query &= Q(home_type=home_type)  # Match home_type in Listing model
#         if search_description:
#             query |= Q(description__icontains=search_description)  # Match description
#         if min_price:
#             query |= Q(price__gte=int(min_price))  # price >= min_price
#         if max_price:
#             query |= Q(price__lte=int(max_price))  # price <= max_price

#         # Retrieve additional query parameters from the model's attributes
#         sale_type = request.GET.get('sale_type')  # Check for `sale_type` field in GET parameters
#         bedrooms = request.GET.get('bedrooms')  # Check for `bedrooms` field in GET parameters

#         if sale_type:
#             query &= Q(sale_type=sale_type)  # Filter by sale_type if provided
#         if bedrooms:
#             try:
#                 query &= Q(bedrooms=int(bedrooms))  # Convert to int and filter by number of bedrooms
#             except ValueError:
#                 pass  # Ignore invalid bedroom inputs for filtering

#         # Print the query details to the terminal for debugging

#         # Execute query and get the filtered results
#         listings = Listing.objects.filter(query).filter(is_published=True)  # Only show published listings


#         # Check if there are no results
#         if not listings.exists():
#             no_results_message = "No results found."

#         # return redirect('/housing/#search-result')


#     # Render the template with form and listings
#     return render(request, 'index.html', {
#         'form': form,
#         'login_form': login_form,
#         'register_form': register_form,
#         'listings': listings,
#         'no_results_message': no_results_message,
#         'cform': cform,
#         'user' : user
#     })

    



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


