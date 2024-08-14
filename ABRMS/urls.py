
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),
    path('auth/user/', include('user.urls')),
    path('api/token/verify/', TokenVerifyView.as_view()),
    path('api/abrmservices/', include('abrmservices.urls')),
    path('admin/', admin.site.urls),
    path('', include('abrmservices.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
