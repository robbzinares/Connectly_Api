from rest_framework import serializers
from .models import Post, Comment, Like, Follow
from accounts.models import User

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


# Like Serializer
class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


# Post Serializer with nested comments and likes, using annotated counts
class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)      # annotated in queryset
    comments_count = serializers.IntegerField(read_only=True)   # annotated in queryset
    comments = CommentSerializer(source='comment_set', many=True, read_only=True)  # nested comments
    likes = LikeSerializer(source='like_set', many=True, read_only=True)          # nested likes

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'content',
            'privacy',
            'created_at',
            'updated_at',
            'likes_count',
            'comments_count',
            'likes',
            'comments',
        ]
        read_only_fields = fields  # everything read-only except content/privacy on create/update


# Follow Serializer
class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following']
        read_only_fields = ['id', 'follower', 'following']
