from django.urls import path
from .views import mydashboard, delete_listing, get_listing_data

urlpatterns = [
    path('dashboard/', mydashboard, name = 'mydashboard'),
    path('dashboard/<int:id>/', mydashboard, name='mydashboard'),  # Add another pattern
    path('delete-listing/<int:id>/', delete_listing, name='delete_listing'),
    path('dashboard/get-listing-data/<int:property_id>/', get_listing_data, name='get_listing_data'),


]
