from rest_framework import serializers
from .models import Profile,Content,BookDetail,ArticleDetail,Purchase

class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'

class ContentSerializers(serializers.ModelSerializer):
    class Meta:
        model=Content
        fields='__all__'

class BookDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model=BookDetail
        fields='__all__'

class ArticleDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model=ArticleDetail
        fields='__all__'

class PurchaseSerializers(serializers.ModelSerializer):
    class Meta:
        model=Purchase
        fields='__all__'


