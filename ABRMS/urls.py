
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('auth/user/', include('user.urls')),
    path('api/abrmservices/', include('abrmservices.urls')),
    path('admin/', admin.site.urls),
    path('', include('abrmservices.urls')),
    path('', include('user.urls')),
    path('', include('payments.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
