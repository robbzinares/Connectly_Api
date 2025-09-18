from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = "Test encryption and decryption of User model fields (phone, address)."

    def handle(self, *args, **options):
        username = "alice_test"

        # Clean up if user already exists
        User.objects.filter(username=username).delete()

        # Create user
        u = User.objects.create_user(username=username, password="pass123")

        # Set encrypted fields
        u.phone = "09171234567"
        u.address = "123 Secret St, Manila"
        u.save()

        # Display results
        self.stdout.write(self.style.SUCCESS("✅ User created: " + u.username))
        self.stdout.write("Decrypted phone (property): " + str(u.phone))
        self.stdout.write("Decrypted address (property): " + str(u.address))
        self.stdout.write("Encrypted phone (DB): " + str(u.encrypted_phone))
        self.stdout.write("Encrypted address (DB): " + str(u.encrypted_address))
