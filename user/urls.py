from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.mydashboard, name = 'mydashboard'),
    path('dashboard/<int:id>/', views.mydashboard, name='mydashboard'),  # Add another pattern
    path('delete-listing/<int:id>/', views.delete_listing, name='delete_listing'),
    path('dashboard/get-listing-data/<int:property_id>/', views.get_listing_data, name='get_listing_data'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/<int:chat_id>/send/', views.send_message, name='send_message'),
    path('initiate_chat/<str:email>/', views.initiate_chat, name='initiate_chat'),
    path('notifications/', views.notifications_page, name='notifications_page'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
        # Traditional login, register, logout
    path('login/', views.user_login, name='user_login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='user_logout'),

    path('auth/google/signin/', views.google_auth_init, {'action': 'signin'}, name='google_auth_signin'),
    path('auth/google/signup/', views.google_auth_init, {'action': 'signup'}, name='google_auth_signup'),
    path('auth/google/callback/', views.google_auth_callback, name='google_auth_callback'),

    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),


]

