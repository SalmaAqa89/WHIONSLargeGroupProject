from venv import logger
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from matplotlib.ticker import MaxNLocator
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, UserPreferenceForm
from tasks.models import FlowerGrowth, JournalEntry, UserPreferences, User
from tasks.helpers import login_prohibited
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from collections import Counter
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, CalendarForm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from tasks.models import JournalEntry
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from tasks.helpers import login_prohibited
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from datetime import timedelta
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, CalendarForm
from tasks.models import JournalEntry
from tasks.helpers import login_prohibited
from datetime import datetime, timedelta
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from reportlab.lib.enums import TA_CENTER
from datetime import timedelta

class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN
    

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        FlowerGrowth.objects.create(user=self.object, stage=0)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("set_preferences")
    

class SetPreferences(LoginRequiredMixin, FormView):
    """Display the create entry screen and handle entry creation"""

    form_class = UserPreferenceForm
    template_name = "set_preferences.html"

    def dispatch(self, request, *args, **kwargs):
        """ If a preference form has already been made for the user they do not 
        need to access this page therefore it redirects"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if UserPreferences.objects.filter(user=request.user).exists():
            messages.warning(request, "Preferences already exist.")
            return redirect('dashboard')  

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user_preference = form.save(commit=False)
        user_preference.user = self.request.user
        user_preference.save()
        messages.success(self.request, "Preferences Saved!")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')
    
class EditPreferences(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserPreferences
    template_name = "edit_preferences.html"
    form_class = UserPreferenceForm

     
    def get_success_url(self):
        return reverse('dashboard')

    def get_object(self, queryset=None):
        """Return the object (user preferences) to be updated."""
        return get_object_or_404(UserPreferences, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Preferences updated!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


    
