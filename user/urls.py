from django.urls import path
from .views import RegisterView, LoginView, LogoutView, RetrieveUserView, mydashboard, delete_listing, get_listing_data

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', RetrieveUserView.as_view(), name='retrieve_user'),
    path('dashboard/', mydashboard, name = 'mydashboard'),
    path('dashboard/<int:id>/', mydashboard, name='mydashboard'),  # Add another pattern
    path('delete-listing/<int:id>/', delete_listing, name='delete_listing'),
    path('dashboard/get-listing-data/<int:property_id>/', get_listing_data, name='get_listing_data'),


]
