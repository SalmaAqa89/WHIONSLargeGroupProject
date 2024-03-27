# https://python.plainenglish.io/how-to-send-email-with-verification-link-in-django-efb21eefffe8
from django.contrib.auth.tokens import PasswordResetTokenGenerator
    
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            user.pk + timestamp +
            user.email_is_verified
        )
account_activation_token = TokenGenerator()