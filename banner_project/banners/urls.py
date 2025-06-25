from django.urls import path
from . import views


urlpatterns = [
    path('articles/<slug:slug>/', views.article_with_banners, name='article_with_banners'),
    path('written-article/<slug:slug>/', views.written_article_with_banners, name='written_article_with_banners'),
    path('get_tags_by_verticals/', views.get_tags_by_verticals, name='get_tags_by_verticals'),
    path('go/', views.banner_redirect, name='banner_redirect'),
    path('', views.homepage, name='home_page'),

]