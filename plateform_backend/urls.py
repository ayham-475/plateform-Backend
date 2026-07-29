from django.urls import path
from . import views
urlpatterns = [

    path('auth/register/', views.register_user, name='register_user'),
    path('auth/login/', views.login_user, name='login_user'),
    path('auth/profile/', views.save_profile_simple, name='save_profile_simple'),
    # path('article/create/', views.create_article, name='create_article'),
    # مسار إنشاء مقال جديد (POST)
    path('article/create/', views.create_or_update_article, name='create_article'),
    
    # مسار تعديل مقال قائم باستخدام الـ UUID (PUT)
    path('article/create/<uuid:pk>/', views.create_or_update_article, name='update_article'),
    path('article/create_articleDeatils/', views.create_ArticleDeatils, name='create_articleDeatils'),

    # class urls
    path('rest/Profile/', views.Profiles.as_view()),

    path('rest/Profile/<uuid:pk>', views.Profiles_PK.as_view()),
]