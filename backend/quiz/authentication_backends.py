from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

class MongoDBBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        try:
            # Try exact match for email first
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Try exact match for username
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None
        
        # Check password
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None