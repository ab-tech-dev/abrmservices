from django.urls import path
from . import views

# from django.urls import path
# from .views import SearchListingsView



urlpatterns = [
    path('', views.main, name = 'main'),
    path('relocation', views.movingServices, name = 'moving-services'),
    path('cleaning', views.cleaningServices, name = 'cleaning-services'),
    path('contact', views.contact, name = 'contact'),
    path('about', views.about, name = 'about'),
    path('quotes', views.getaquote, name = 'get-a-quote'),
    path('termsandconditions', views.termsandconditions, name = 'termsandconditions'),
    path('housing/', views.housing, name = 'housing'),
    path('submitmyform', views.submitmyform, name = 'submitmyform'),
    path('listing/<slug:slug>/', views.housing, name='listing_detail'),
]