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
