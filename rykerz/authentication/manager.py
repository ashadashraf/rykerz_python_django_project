from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, mobile=None, name=None):
        if not email:
            raise ValueError('The given email must be set')
        
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, mobile=mobile, password=password)
        user.set_password(password)
        user.save()
        return user
    