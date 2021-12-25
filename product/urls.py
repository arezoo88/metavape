from django.urls import path
from product.views import (
    ProductApiView,
    CommentCreateApiView,
    CommentListApiView,
    RatingListApiView,
    RatingCreateApiView,
    FavoriteApiView
)

urlpatterns = [
    path("", ProductApiView.as_view()),
    path("comment/create/", CommentCreateApiView.as_view()),
    path("comment/list/<str:product_id>/", CommentListApiView.as_view()),
    path("rate/create/", RatingCreateApiView.as_view()),
    path("rate/list/<str:product_id>/", RatingListApiView.as_view()),
    path("favorite/", FavoriteApiView.as_view()),

]
