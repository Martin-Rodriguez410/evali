import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obstetricia.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'Admin'
new_password = '123456789'

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    print(f"Password for user '{username}' changed successfully.")
except User.DoesNotExist:
    print(f"User '{username}' not found.")
except Exception as e:
    print(f"Error changing password: {e}")
