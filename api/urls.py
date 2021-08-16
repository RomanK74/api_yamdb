from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CommentViewSet,
    CategoryViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    EmailConfirmViewSet,
    UsersViewSet,
)


router_api_v1 = DefaultRouter()
router_api_v1.register(
    'genres',
    GenreViewSet,
    basename="genre")
router_api_v1.register(
    'categories',
    CategoryViewSet,
    basename="category")
router_api_v1.register(
    'titles',
    TitleViewSet,
    basename='titles')
router_api_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')
router_api_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router_api_v1.register(
    r'users',
    UsersViewSet,
    basename='users')
router_api_v1.register(
    r'auth',
    EmailConfirmViewSet,
    basename='auth')

urlpatterns = [
    path('v1/', include(router_api_v1.urls)),
]
