import re
from django.http import request
from rest_framework import generics, serializers, status, views
from product.serializers import (
    CommentSerializer,
    FavoriteSerializer,
    ProductSerializer,
    RatingSerializer,
)
from product.models import Comment, Favorite, Product, Rating, Shop
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from utils import load_html


class ProductApiView(generics.ListAPIView):
    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        name = self.request.query_params.get("name")
        if name:
            self.queryset = self.queryset.filter(name__contains=name)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

class CommentCreateApiView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        product = get_object_or_404(Product, pk=self.request.data.get("product"))
        check_exist_comment = Comment.objects.filter(user=user, product=product)
        if len(check_exist_comment):
            raise PermissionDenied(
                {"detail": "previously ,you registerd your comment for this product"}
            )
        serializer.save(user=user, body=self.request.data.get("body"), product=product)


class CommentListApiView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        product_id = self.kwargs["product_id"]
        product = get_object_or_404(Product, pk=product_id)
        produc_url = product.product_url
        shop = product.shop
        shop_obj = get_object_or_404(Shop, pk=shop.id)
        comment_xpath = shop_obj.comment_xpath
        title_xpath = shop_obj.title_xpath
        xpath = {"title": comment_xpath, "comment": title_xpath}
        data = load_html.get_data(produc_url, xpath)
        comments = Comment.objects.filter(product_id=product_id)
        serializer = CommentSerializer(comments, many=True)
        arr = [
            {"user":None,"shop":{"pk":shop.pk,"name":shop_obj.name},"title": item, "body": data["comment"][index],"product":product_id}
            for index, item in enumerate(data["title"])
        ]        
        return Response(serializer.data+arr)


class RatingCreateApiView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        product = get_object_or_404(Product, pk=self.request.data.get("product"))
        check_user_rated = Rating.objects.filter(user=user, product=product)
        if len(check_user_rated):
            raise PermissionDenied({"detail": "previously ,you rated to this product"})
        serializer.save(user=user, star=self.request.data.get("star"), product=product)


class RatingListApiView(generics.ListAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        product_id = self.kwargs["product_id"]
        rates = Rating.objects.filter(product_id=product_id)
        serializer = RatingSerializer(rates, many=True)
        return Response(serializer.data)


class FavoriteApiView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        product = get_object_or_404(Product, pk=self.request.data.get("product"))
        favorite = Favorite.objects.filter(user=user, product=product)
        if len(favorite):
            raise PermissionDenied(
                {"detail": "previously ,you added this product to your favorites"}
            )
        serializer.save(user=user, product=product)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        favorites = Favorite.objects.filter(user=user)
        serializer = self.serializer_class(favorites,many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        product_id = self.request.query_params.get("product_id")
        product = get_object_or_404(Favorite, product_id=product_id,user_id=request.user.id)
        product.delete()
        return Response({'success':True},status=status.HTTP_200_OK)
