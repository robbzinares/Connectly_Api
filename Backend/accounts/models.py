from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
import os


# Helper: return a Fernet instance based on settings or env
def get_fernet():
    key = getattr(settings, 'FERNET_KEY', None) or os.environ.get('FERNET_KEY')
    if not key:
        raise RuntimeError("FERNET_KEY not set in settings or environment")
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_MOD = 'moderator'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_MOD, 'Moderator'),
        (ROLE_ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)

    # Encrypted storage fields (stored as bytes in DB)
    encrypted_phone = models.BinaryField(null=True, blank=True, editable=False)
    encrypted_address = models.BinaryField(null=True, blank=True, editable=False)

    # Public convenience properties
    @property
    def phone(self):
        if not self.encrypted_phone:
            return None
        try:
            f = get_fernet()
            return f.decrypt(bytes(self.encrypted_phone)).decode()
        except (InvalidToken, TypeError):
            return None

    @phone.setter
    def phone(self, value):
        if value is None:
            self.encrypted_phone = None
            return
        f = get_fernet()
        token = f.encrypt(value.encode())
        self.encrypted_phone = bytes(token)

    @property
    def address(self):
        if not self.encrypted_address:
            return None
        try:
            f = get_fernet()
            return f.decrypt(bytes(self.encrypted_address)).decode()
        except (InvalidToken, TypeError):
            return None

    @address.setter
    def address(self, value):
        if value is None:
            self.encrypted_address = None
            return
        f = get_fernet()
        token = f.encrypt(value.encode())
        self.encrypted_address = bytes(token)

    def is_moderator(self):
        return self.role == self.ROLE_MOD

    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        return self.username
