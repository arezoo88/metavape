from django.urls import path
from .views import DownloadImageView
urlpatterns = [
    path('image/',DownloadImageView.as_view())

]