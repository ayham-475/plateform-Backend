from django.urls import path
from . import views
urlpatterns = [


    path('auth/register/', views.register_user, name='register_user'),
    path('auth/login/', views.login_user, name='login_user'),

    # class Profile urls
    path('rest/Profile/', views.Profiles.as_view()),

    path('rest/Profile/<uuid:pk>', views.Profiles_PK.as_view()),

    # class Content urls
    path('rest/Content-articles/', views.Contents.as_view()),

    path('rest/Content-articles/<uuid:pk>', views.Contents_PK.as_view()),
]