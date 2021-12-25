from django.contrib import admin
from django.urls import path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Meta Vape Apis",
      default_version='v1',
      description="Test description",
      terms_of_service="",
      contact=openapi.Contact(email=""),
      license=openapi.License(name="License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/',include('imagedownload.urls')),
    path('account/', include('authentication.urls')),
    path('product/',include('product.urls')),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/api.json', schema_view.without_ui( cache_timeout=0), name='schema-swagger-ui'),# export for postman
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), 
]
