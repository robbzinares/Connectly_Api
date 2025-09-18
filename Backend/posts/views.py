from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, Count
from .models import Post, Comment, Like, Follow
from .serializers import PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer

# Custom permission: only post author or moderator/admin can delete/update
class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.is_moderator()
            or request.user.is_admin()
        )


# Posts
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            public_posts = Q(privacy=Post.PRIVACY_PUBLIC)
            following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
            followers_posts = Q(privacy=Post.PRIVACY_FOLLOWERS, author__id__in=following_ids)
            private_posts = Q(privacy=Post.PRIVACY_PRIVATE, author=user)
            qs = Post.objects.filter(public_posts | followers_posts | private_posts, is_deleted=False)
        else:
            qs = Post.objects.filter(privacy=Post.PRIVACY_PUBLIC, is_deleted=False)

        # Annotate counts of likes and comments for easier frontend display
        qs = qs.annotate(
            likes_count=Count('like', distinct=True),
            comments_count=Count('comment', distinct=True)
        ).order_by('-created_at')

        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# Comments
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = Comment.objects.select_related('post')
        post_id = self.request.query_params.get('post')  # filter comments by post id
        if user.is_authenticated:
            visible_posts = Post.objects.filter(
                Q(privacy=Post.PRIVACY_PUBLIC) |
                Q(privacy=Post.PRIVACY_FOLLOWERS, author__followers__follower=user) |
                Q(privacy=Post.PRIVACY_PRIVATE, author=user),
                is_deleted=False
            )
        else:
            visible_posts = Post.objects.filter(privacy=Post.PRIVACY_PUBLIC, is_deleted=False)

        qs = qs.filter(post__in=visible_posts)

        if post_id:
            qs = qs.filter(post_id=post_id)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        serializer.save(author=self.request.user, post_id=post_id)


# Likes
class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Like.objects.select_related('post')
        post_id = self.request.query_params.get('post')  # filter likes by post id
        visible_posts = Post.objects.filter(
            Q(privacy=Post.PRIVACY_PUBLIC) |
            Q(privacy=Post.PRIVACY_FOLLOWERS, author__followers__follower=user) |
            Q(privacy=Post.PRIVACY_PRIVATE, author=user),
            is_deleted=False
        )
        qs = qs.filter(post__in=visible_posts)

        if post_id:
            qs = qs.filter(post_id=post_id)

        return qs

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        post = Post.objects.get(pk=post_id)
        if Like.objects.filter(post=post, user=self.request.user).exists():
            raise PermissionDenied("You have already liked this post.")
        serializer.save(user=self.request.user, post=post)


# Follows
class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        following_user = serializer.validated_data['following']
        if following_user == self.request.user:
            raise PermissionDenied("You cannot follow yourself.")
        if Follow.objects.filter(follower=self.request.user, following=following_user).exists():
            raise PermissionDenied("You are already following this user.")
        serializer.save(follower=self.request.user)
