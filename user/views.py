from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
User = get_user_model()
from .serializers import UserSerializer
from django.shortcuts import render



def listings(request):
    return render(request, 'index.html')


# Import statements...

class RegisterView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        try:
            data = request.data

            name = data.get('name')
            email = data.get('email')
            email = email.lower()
            password = data.get('password')
            re_password = data.get('re_password')
            is_realtor = data.get('is_realtor') 

            if password == re_password and len(password) >= 8:
                if not User.objects.filter(email=email).exists():
                    if is_realtor == "True":
                        is_realtor = True
                        user = User.objects.create_realtor(name=name, email=email, password=password)
                        serializer = UserSerializer(user)  # Serialize the created user
                        return Response(
                            {'success' : 'Realtor account created successfully'},
                            status=status.HTTP_201_CREATED
                        )
                    else:
                        user = User.objects.create_user(name=name, email=email, password=password)
                        serializer = UserSerializer(user)  # Serialize the created user
                        return Response(
                            {'success' : 'User created successfully'},
                            status=status.HTTP_201_CREATED
                        )
                else:
                    return Response(
                        {'error' : 'User with this email already exists'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif len(password) < 8:
                return Response(
                    {'error' : 'Password must be at least 8 characters in length'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'error' : 'Passwords do not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except ValueError as e:
            return Response(
                {'error' : f'ValueError: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error' : f'Something went wrong when registering an account: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RetrieveUserView(APIView):
    def get(self, request, format=None):
        try:
            user = request.user
            user_serializer = UserSerializer(user)
            return Response({'user': user_serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An error occurred while retrieving user details: {str(e)}")
            # Raise a more specific exception or handle it accordingly
            raise APIException('Something went wrong when retrieving user details')

from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        data = request.data
        email = data.get('email').lower()
        password = data.get('password')

        try:
            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({
                        'success': 'Login successful',
                        'token': token.key,
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'User account is deactivated'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    def post(self, request):
        try:
            request.user.auth_token.delete()
            logout(request)
            return Response({'success': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
