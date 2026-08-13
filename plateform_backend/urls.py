from django.urls import path
from . import views
urlpatterns = [


    path('auth/register/', views.register_user, name='register_user'),
    path('auth/login/', views.login_user, name='login_user'),

    # class Users urls
    path('rest/Users/', views.Users.as_view()),
    path('rest/Users/<int:pk>', views.Users_PK.as_view()),

    # class Profile urls
    path('rest/Profile/', views.Profiles.as_view()),
    path('rest/Profile/<uuid:pk>', views.Profiles_PK.as_view()),

    # class Content urls
    path('rest/Content-articles/', views.Contents.as_view()),
    path('rest/Content-articles/<uuid:pk>', views.Contents_PK.as_view()),

    # class BookDeails urls
    path('rest/BookDeatils/', views.BooksDeatils.as_view()),
    path('rest/BookDeatils/<uuid:pk>', views.BooksDeatils_pk.as_view()),

    # class BookDeails urls
    path('rest/ArticleDeatils/', views.ArticlesDeatils.as_view()),
    path('rest/ArticleDeatils/<uuid:pk>', views.ArticlesDeatils_pk.as_view()),

    # class BookDeails urls
    path('rest/Purchases/', views.Purchases.as_view()),
    path('rest/Purchases_pk/<uuid:pk>', views.Purchases_pk.as_view()),

]