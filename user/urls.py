from django.urls import path
from .views import mydashboard, delete_listing, get_listing_data, chat_list, chat_detail, send_message, initiate_chat_with_superuser,notifications_page,mark_as_read,delete_notification
urlpatterns = [
    path('dashboard/', mydashboard, name = 'mydashboard'),
    path('dashboard/<int:id>/', mydashboard, name='mydashboard'),  # Add another pattern
    path('delete-listing/<int:id>/', delete_listing, name='delete_listing'),
    path('dashboard/get-listing-data/<int:property_id>/', get_listing_data, name='get_listing_data'),
    path('chats/', chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', chat_detail, name='chat_detail'),
    path('chat/<int:chat_id>/send/', send_message, name='send_message'),
    path('initiate_chat/', initiate_chat_with_superuser, name='initiate_chat'),
    path('notifications/', notifications_page, name='notifications_page'),
    path('notifications/mark-as-read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
    path('notifications/delete/<int:notification_id>/', delete_notification, name='delete_notification'),

]
