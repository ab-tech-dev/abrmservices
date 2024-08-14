from django.urls import path
from .views import ManageListingView, ListingDetailView, ListingsView, SearchListingsView
from . import views


urlpatterns = [
    path('manage', ManageListingView.as_view()),
    path('detail', ListingDetailView.as_view()),
    path('get-listings', ListingsView.as_view()),
    path('search', SearchListingsView.as_view()),
    path('', views.main, name = 'main'),
    path('relocation', views.movingServices, name = 'moving-services'),
    path('cleaning', views.cleaningServices, name = 'cleaning-services'),
    path('contact', views.contact, name = 'contact'),
    path('about', views.about, name = 'about'),
    path('quotes', views.getaquote, name = 'get-a-quote'),
    path('termsandconditions', views.termsandconditions, name = 'termsandconditions'),
    path('housing', views.housing, name = 'housing'),
    path('submitmyform', views.submitmyform, name = 'submitmyform')
]