from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, LikeViewSet, FollowViewSet

router = DefaultRouter()
router.register(r'newsfeed', PostViewSet, basename='newsfeed')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'likes', LikeViewSet, basename='likes')
router.register(r'follows', FollowViewSet, basename='follows')

urlpatterns = [
    path('', include(router.urls)),
]
