from django.conf import settings
from django.shortcuts import redirect

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def verification_required(view_function):
    """Decorator for view functions that redirect users to the verfification page if their email is not verified"""
    
    def modified_view_function(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.email_is_verified:
            return view_function(request, *args, **kwargs)
        elif request.user.is_authenticated:
            return redirect("verify-email")
        else:
            return redirect(settings.LOGIN_URL)
    return modified_view_function