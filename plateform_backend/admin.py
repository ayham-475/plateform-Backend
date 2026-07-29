from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile, Content, BookDetail, ArticleDetail, Purchase


admin.site.register(Profile)
admin.site.register(Content)
admin.site.register(BookDetail)
admin.site.register(ArticleDetail)
admin.site.register(Purchase)