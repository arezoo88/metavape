from django.db import models
from django.db.models import fields
from rest_framework import serializers
from product.models import Comment, Favorite, Product,ProductImage,ImageList, Rating, Shop
from authentication.serializers import UserSerializer
from django.db.models import Q,Avg
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]
    
    def to_representation(self, instance):
        """Convert `image` to url of the image."""
        ret = super().to_representation(instance)
        ret['image'] = 'https://res.cloudinary.com/metavape/' + ret['image']
        return ret

class ImageListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)

    class Meta:
        model = ImageList
        fields = ['images']

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["pk","name"]
class ProductSerializer(serializers.ModelSerializer):
    image = ImageListSerializer()
    shop = ShopSerializer(read_only=True)
    rating_avarage = serializers.SerializerMethodField('calculate_avarage_rating')

    def calculate_avarage_rating(self,obj):
        list_of_rates = Rating.objects.filter(product=obj.pk)
        if len(list_of_rates)==0:
            return 0
        get_rate_in_app = list_of_rates.filter(Q(rating_number=None))
        get_rates_in_site = list_of_rates.filter(~Q(rating_number=None))
        avg_in_app = list_of_rates.aggregate(average_stars = Avg('star'))["average_stars"]*len(get_rate_in_app)
        avg_in_site = get_rates_in_site[0].star * get_rates_in_site[0].rating_number
        total_avg = (avg_in_app+avg_in_site)/(len(get_rate_in_app)+get_rates_in_site[0].rating_number)

        return total_avg
    class Meta:
        model = Product
        fields = ['pk', 'name', 'description', 'shop', 'image','rating_avarage']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['user','shop','title','body','product']
        read_only_fields = ['user']


class RatingSerializer(serializers.ModelSerializer):
        user = UserSerializer(read_only=True)
        shop = ShopSerializer(read_only=True)
        class Meta:
            model = Rating
            fields = ['user','shop','star','product']
            read_only_fields = ['user']

class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Favorite
        fields = ['user','product']
        read_only_fields = ['user']
