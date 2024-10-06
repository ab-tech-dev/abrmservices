from django.urls import path
from . import views
from .views import RegisterView, RetrieveUserView



urlpatterns = [
    path('register', RegisterView.as_view()),
    path('me', RetrieveUserView.as_view()),
    path('listings', views.listings, name = 'listings')

]

