from django.shortcuts import render
from rest_framework.views import APIView
from .models import Listing
from rest_framework import status, permissions
from rest_framework.response import Response
from .serializers import ListingSerializer
from django.http import Http404
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import os
from .models import House
# Create your views here.
from mailersend import emails
import base64
# from dotenv import load_dotenv

# load_dotenv()

mailer = emails.NewEmail(os.getenv('mlsn.bd8b1921e3f0be6f76ca361c651bdb6ca6d7da63555fde0b84a244ffdef16a00'))

class ManageListingView(APIView):
    def get(self, request, format=None):
        try:
            user = request.user
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have necessary permissions for creating this listing data'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            slug = request.query_params.get('slug')

            if not slug:
                listing = Listing.objects.order_by('-date_created').filter(
                    realtor =  
                    user.email
                )

                listing = ListingSerializer(listing, many=True)

                return Response(
                    {
                        'listings' : listing.data
                    },
                    status=status.HTTP_200_OK
                )
            
            if not Listing.objects.filter(
                realtor = user.email,
                slug=slug
            ).exists():
                return Response(
                    {'error' : 'Listing not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            listing = Listing.objects.get(realtor=user.email, slug=slug)
            listing = ListingSerializer(listing)

            return Response(
                {'listing' : listing.data},
                status=status.HTTP_200_OK
            )

        except:
            return Response(
                {'error' : 'Something went wrong when retrieving Listing or Listing detail'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def retrieve_values(self, data):
        title = data.get('title')
        slug = data.get('slug')

        if not title:
            return Response(
                {'error': 'Title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Other fields validation...

        # Convert price, bedrooms, and bathrooms to the correct types
        try:
            price = int(data.get('price'))
            bedrooms = int(data.get('bedrooms'))
            bathrooms = float(data.get('bathrooms'))
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate bathrooms range
        if bathrooms <= 0 or bathrooms >= 10:
            bathrooms = 1.0

        bathrooms = round(bathrooms, 1)

        # Convert sale_type and home_type
        sale_type = 'For Rent' if data.get('sale_type') == 'FOR_RENT' else 'For Sale'
        home_type = 'Condo' if data.get('home_type') == 'CONDO' else 'House'

        # Other fields conversion and validation...
        address = data.get('address')
        city = data.get('city')
        state = data.get('state')
        zipcode = data.get('zipcode')
        description = data.get('description')
        main_photo = data.get('main_photo')
        photo_1 = data.get('photo_1')
        photo_2 = data.get('photo_2')
        photo_3 = data.get('photo_3')
        is_published = data.get('is_published', False)

        data = {
                'title' : title, 
                'slug' : slug, 
                'address' : address, 
                'city' : city, 
                'state' : state, 
                'zipcode' : zipcode, 
                'description' : description, 
                'price' : price,
                'bedrooms' : bedrooms, 
                'bathrooms' : bathrooms, 
                'sale_type' : sale_type, 
                'home_type' : home_type, 
                'main_photo' : main_photo,
                'photo_1' : photo_1,
                'photo_2' : photo_2,
                'photo_3' : photo_3,
                'is_published' : is_published
        }


        return data

    def post(self, request):
        try:
            user = request.user
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have necessary permissions for creating this listing data'},
                    status=status.HTTP_403_FORBIDDEN
                )

            data = request.data
            data = self.retrieve_values(data)


            title = data.get('title')
            slug = data.get('slug')

            # Check if a listing with the same "slug" already exists
            if Listing.objects.filter(slug=slug).exists():
                return Response(
                    {'error': 'Listing with this slug already exists'},
                    status=status.HTTP_400_BAD_REQUEST  # You can choose the appropriate status code
                )

            # Continue with creating the listing
            address = data.get('address')
            city = data.get('city')
            state = data.get('state')
            zipcode = data.get('zipcode')
            description = data.get('description')

            price = data.get('price')
            try:
                price = float(price)
            except ValueError as e:
                return Response(
                    {'error': f"Field 'price' expected a number but got {price}. Error: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            bedrooms = data.get('bedrooms')
            bathrooms = data.get('bathrooms')
            sale_type = data.get('sale_type')
            home_type = data.get('home_type')
            main_photo = data.get('main_photo')
            photo_1 = data.get('photo_1')
            photo_2 = data.get('photo_2')
            photo_3 = data.get('photo_3')
            is_published = data.get('is_published', False)

            # Create the Listing object
            listing = Listing.objects.create(
                realtor=user.email,
                title=title,
                slug=slug,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                description=description,
                price=price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                sale_type=sale_type,
                home_type=home_type,
                main_photo=main_photo,
                photo_1=photo_1,
                photo_2=photo_2,
                photo_3=photo_3,
                is_published=is_published
            )

            return Response(
                {'success': 'Listing created successfully', 'listing_id': listing.id},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': f'Something went wrong when creating this listing data: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        
    def put(self, request):
        try:
            user = request.user
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have necessary permissions for getting this listing data'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data

            data = self.retrieve_values(data)

            title = data.get('title')  # Remove the extra comma
            slug = data.get('slug')
            address = data.get('address')
            city = data.get('city')
            state = data.get('state')
            zipcode = data.get('zipcode')
            description = data.get('description')
            price = data.get('price')
            bedrooms = data.get('bedrooms')
            bathrooms = data.get('bathrooms')
            sale_type = data.get('sale_type')
            home_type = data.get('home_type')
            main_photo = data.get('main_photo')
            photo_1 = data.get('photo_1')
            photo_2 = data.get('photo_2')
            photo_3 = data.get('photo_3')
            is_published = data.get('is_published', False)

            if not Listing.objects.filter(realtor=user.email, slug=slug).exists():
                raise Http404(f'Listing with slug "{slug}" does not exist for user "{user.email}"')
                
            Listing.objects.filter(realtor=user.email, slug=slug).update(
                realtor=user.email,
                title=title,
                slug=slug,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                description=description,
                price=price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                sale_type=sale_type,
                home_type=home_type,
                main_photo=main_photo,
                photo_1=photo_1,
                photo_2=photo_2,
                photo_3=photo_3,
                is_published=is_published
            )
            
            return Response(
                {'success' : 'Listing updated successfully'},
                status=status.HTTP_200_OK
            )

        except Http404 as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Something went wrong updating listing: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request):
        try:
            user = request.user
            if not user.is_realtor:
                return Response(
                    {'error': 'User does not have necessary permissions for getting this listing data'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            data = request.data

            slug = data['slug']

            is_published = data['is_published']
            if is_published == 'True':
                is_published = True
            else:
                is_published = False

            if not Listing.objects.filter(realtor=user.email, slug=slug).exists():
                raise Http404(f'Listing with slug "{slug}" does not exist for user "{user.email}"')

            Listing.objects.filter(realtor=user.email, slug=slug).update(
                is_published=is_published
            )

            return Response(
                {'success' : 'Listing publish status updated successfully'},
                status=status.HTTP_200_OK
            )


        except Http404 as e:
            return Response(
                {'error': f'Something went wrong updating listing: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def delete(self, request):
        try:
            user = request.user
            data = request.data
            slug = data['slug']
            if not user.is_realtor:
                    return Response(
                        {'error': 'User does not have necessary permissions for deleting this listing data'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            if not Listing.objects.filter(realtor=user.email, slug=slug).exists():
                    return Response(
                        {'error' : 'Listing you are trying to delete does not exist'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            Listing.objects.filter(realtor=user.email, slug=slug).delete()
            if not Listing.objects.filter(realtor=user.email, sulug=slug).exists():
                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'error' : 'Failed to delete listing'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(
                    {'error': 'Something went wrong when deleting this listing data'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class ListingDetailView(APIView):
    def get(self, request, format=None):
        try:
            slug = request.query_params.get('slug')

            if not slug:
                return Response(
                    {'error' : 'Must provide slug'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not Listing.objects.filter(slug=slug, is_published=True).exists():
                return Response(
                    {'error' : 'Published listing with this slug does not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            listing = Listing.objects.get(slug=slug, is_published=True)
            listing = ListingSerializer(listing)

            return Response(
                {'listing' : listing.data},
                status=status.HTTP_200_OK
            )


        except:
            return Response(
                {'error' : 'Error retrieving listing' },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class ListingsView(APIView):
    permission_classes = (permissions.AllowAny, )

    def get(self, request, format=None):
        try:
            if not Listing.objects.filter(is_published=True).exists():
                return Response(
                    {'error' : 'No published listings in the database'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            listings  = Listing.objects.order_by('-date_created').filter(is_published=True)
            listings = ListingSerializer(listings, many=True)

            return Response(
                {'listings' : listings.data},
                status=status.HTTP_200_OK
            )
        
        except:
            return Response(
                {'error' : 'Something went wrong when retrieving listings'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

from django.db.models import Q


from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector

from django import forms
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
    ('realtor', 'Realtor'),
    ('sale_type', 'Sale Type'),
    ('slug', 'Slug'),
    ('state', 'State'),
    ('title', 'Title'),
    ('zipcode', 'Zip Code'),
]

class SearchForm(forms.Form):
    # Define a field for search criteria with the choices
    search_field = forms.ChoiceField(choices=SEARCH_FIELDS_CHOICES, label='Search Field')
    # Define a field for the search term
    search_term = forms.CharField(max_length=100, label='Search Term')

class SearchListingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        try:
            # Process the search form data
            search_form = SearchForm(request.GET)

            if search_form.is_valid():
                search_field = search_form.cleaned_data['search_field']
                search_term = search_form.cleaned_data['search_term']

                # Check if a valid search field is selected
                if search_field not in search_fields:
                    return Response(
                        {'error': 'Invalid search field'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Construct the query based on the selected field and term
                query = Q(is_published=True)
                query |= Q(**{f'{search_field}__icontains': search_term})

            else:
                # If the form is not valid or no search criteria is provided, use keyword search
                search = request.query_params.get('search')

                if not search:
                    return Response(
                        {'error': 'No search query provided'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Define the fields you want to search
                search_fields = [
                    'address',
                    'bathrooms',
                    'bedrooms',
                    'city',
                    'description',
                    'home_type',
                    'realtor',
                    'sale_type',
                    'slug',
                    'state',
                    'title',
                    'zipcode',
                ]

                # Create a SearchQuery object
                search_query = SearchQuery(search)

                # Initialize a query object
                query = Q(is_published=True)  # Add the condition for is_published

                # Build the dynamic query for each field
                for field in search_fields:
                    query |= Q(**{f'{field}__icontains': search})

                # Execute the query
                listings = Listing.objects.filter(query)

                for listing in listings:
                    print(listing.title)

                return Response(
                    {'success': 'Search successful', 'listings': [listing.title for listing in listings]},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'error': f'Something went wrong when searching for listings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# for the html page
# <form method="get" action="{% url 'search' %}">
#     {% csrf_token %}
#     <label for="{{ search_form.search_field.id_for_label }}">Search Field:</label>
#     {{ search_form.search_field }}
#     <br>
#     <label for="{{ search_form.search_term.id_for_label }}">Search Term:</label>
#     {{ search_form.search_term }}
#     <br>
#     <button type="submit">Search</button>
# </form>



from .models import House

def housing(request):
    # Retrieve all house objects from the database
    houses = House.objects.all()
    rent_houses = House.objects.filter(status='rent')
    sale_houses = House.objects.filter(status='sale')
    
    context = {
        'rent_houses': rent_houses,
        'sale_houses': sale_houses,
        'houses': houses

    }


    # Render the template with the context data
    return render(request, 'housing.html', context)


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


