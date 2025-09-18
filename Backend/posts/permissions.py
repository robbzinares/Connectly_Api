# posts/permissions.py
from rest_framework import permissions
from .models import Follow

class IsOwnerOrModeratorOrAdmin(permissions.BasePermission):
    """Write perms: only object owner or moderator/admin can edit/delete."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return (hasattr(obj, 'author') and obj.author == user) or user.is_authenticated and (user.role in ('moderator', 'admin'))

class PostPrivacyPermission(permissions.BasePermission):
    """
    Read object-level permission depending on Post.privacy:
    - PUBLIC: anyone
    - FOLLOWERS: author, followers, moderators/admins
    - PRIVATE: only author, moderators/admins
    """
    def has_object_permission(self, request, view, obj):
        if obj.privacy == obj.PRIVACY_PUBLIC:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        # admin/moderator override
        if user.role in ('moderator', 'admin'):
            return True
        if obj.privacy == obj.PRIVACY_PRIVATE:
            return obj.author == user
        if obj.privacy == obj.PRIVACY_FOLLOWERS:
            if obj.author == user:
                return True
            # does 'user' follow the author?
            return obj.author.followers.filter(follower=user).exists()
        return False
