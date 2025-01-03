from django.urls import path
from .views import mydashboard, delete_listing, get_listing_data, chat_list, chat_detail, send_message, initiate_chat_with_superuser
urlpatterns = [
    path('dashboard/', mydashboard, name = 'mydashboard'),
    path('dashboard/<int:id>/', mydashboard, name='mydashboard'),  # Add another pattern
    path('delete-listing/<int:id>/', delete_listing, name='delete_listing'),
    path('dashboard/get-listing-data/<int:property_id>/', get_listing_data, name='get_listing_data'),
    path('chats/', chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('chat/<int:chat_id>/send/', send_message, name='send_message'),
    path('initiate_chat/', initiate_chat_with_superuser, name='initiate_chat'),
]
