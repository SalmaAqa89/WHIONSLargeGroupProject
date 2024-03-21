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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from datetime import timedelta
from reportlab.lib.enums import TA_CENTER
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, CalendarForm
from tasks.models import JournalEntry
from tasks.helpers import login_prohibited
from datetime import datetime, timedelta
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.lib.pagesizes import letter
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from datetime import timedelta
from xhtml2pdf import pisa
import re
import os
from django.shortcuts import render
import base64
from datetime import datetime
from PyPDF2 import PdfMerger
import tempfile
from tasks.forms import JournalSearchForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from reportlab.pdfgen import canvas


DEFAULT_TEMPLATE = {"name" : "Default template", "text" : "This is the default template"}

@login_required
def dashboard(request):
    now = timezone.now()
    all_entries = JournalEntry.objects.filter(user=request.user)
    dates_journaled = {entry.created_at.date() for entry in all_entries}
    streak = 0
    date = now.date()
    while True:
        if date in dates_journaled:
            streak += 1
        elif date != now.date():
            break
        date -= timedelta(days=1)


    return render(request, 'dashboard.html', {
        'user': request.user,
        'days_since_account_creation': (now - request.user.created_at).days,
        'days_journaled': len(dates_journaled),
        'journal_streak': streak,
    })

@login_required
def journal_log(request):
    return render(request, 'journal_log.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user)})

@login_required
def favourites(request):
    return render(request, 'favourites.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user, favourited=True)})

@login_required
def templates(request):
    return render(request, 'templates.html', {"templates": [DEFAULT_TEMPLATE]})

@login_required
def trash(request):
    return render(request, 'trash.html',{'journal_entries' : JournalEntry.objects.filter(user=request.user, deleted=True, permanently_deleted=False)})

@login_required
def mood_breakdown(request):
    return render(request, 'mood_breakdown.html')


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


def get_journal_entries(request):
    date_str = request.GET.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseBadRequest('Invalid date format')
    entries = JournalEntry.objects.filter(created_at__date=date, user=request.user, deleted=False).values('title', 'text', 'mood')
    return JsonResponse({'entries': list(entries)})



def export_entries(request):
    entry_ids = request.GET.get('entries', '').split(',')
    entry_ids = [int(id) for id in entry_ids if id.isdigit()]
    export_format = request.GET.get('format', 'pdf')

    if export_format == 'pdf':
        pdf_paths = []
        for entry_id in entry_ids:
            response = export_journal_entry_to_pdf(request, entry_id)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(response.content)
                pdf_paths.append(temp_pdf.name)

        combined_pdf = merge_pdfs(pdf_paths)
        return combined_pdf
    elif export_format == 'rtf':
        rtf_contents = []
        for entry_id in entry_ids:
            response = export_journal_entry_to_rtf(request, entry_id)
            rtf_contents.append(response.content)

        combined_rtf = merge_rtf(rtf_contents)
        return combined_rtf
    else:
        return HttpResponse('Invalid export format')


def merge_pdfs(pdf_paths):
    combined_pdf = BytesIO()

    pdf_merger = PdfMerger()

    for pdf_path in pdf_paths:
        pdf_merger.append(pdf_path)

    pdf_merger.write(combined_pdf)
    pdf_merger.close()
    
    combined_pdf.seek(0)
    response = HttpResponse(combined_pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="journalentries.pdf"'
    return response

def merge_rtf(rtf_contents):
    combined_rtf = BytesIO()

    combined_rtf.write(b"{\\rtf1\\ansi\\deff0\n")
    for i, rtf_content in enumerate(rtf_contents):
        if i != 0:
            combined_rtf.write(b"\\par\n")  
        combined_rtf.write(rtf_content)
    combined_rtf.write(b"}")

    combined_rtf.seek(0)
    response = HttpResponse(combined_rtf, content_type='application/rtf')
    response['Content-Disposition'] = 'attachment; filename="journalentries.rtf"'
    return response



def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri 

    if not os.path.isfile(path):
        raise Exception(f'Media URI must start with {settings.MEDIA_URL} or {settings.STATIC_URL}')

    return path
def export_journal_entry_to_pdf(request, entry_id):
    journal_entry = get_object_or_404(JournalEntry, pk=entry_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{journal_entry.title}.pdf"'

    html_content = f"<h1>{journal_entry.title}</h1>{journal_entry.text}"
    pisa_status = pisa.CreatePDF(
        BytesIO(html_content.encode("UTF-8")), dest=response,
        link_callback=link_callback  
    )
    if pisa_status.err:
        return HttpResponse('Failed to generate PDF. Please try again later.')
    return response



def strip_tags(html):
    clean_text = re.sub('<[^<]+?>', '', html)
    return clean_text
def export_journal_entry_to_rtf(request, entry_id):
    journal_entry = get_object_or_404(JournalEntry, pk=entry_id)
    clean_text = strip_tags(journal_entry.text)

    response = HttpResponse(content_type='application/rtf')
    response['Content-Disposition'] = f'attachment; filename="{journal_entry.title}.rtf"'

    rtf_content = "{\\rtf1\\ansi\\deff0 "
    rtf_content += f"\\b {journal_entry.title} \\b0\\line " 
    rtf_content += clean_text.replace('\n', '\\line ')
    rtf_content += " }"

    response.write(rtf_content)
    return response

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
    

class CreateJournalEntryView(LoginRequiredMixin, FormView):
    """Display the create entry screen and handle entry creation"""

    form_class = JournalEntryForm
    template_name = "create_entry.html"

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the create entry form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user, 'text': DEFAULT_TEMPLATE["text"]})
        return kwargs

    def form_valid(self, form):
        journal_entry = form.save(commit=False)
        journal_entry.user = self.request.user
        journal_entry.save()

        today = timezone.now().date()
        try:
            flower_growth = FlowerGrowth.objects.get(user=self.request.user)
        except FlowerGrowth.DoesNotExist:
            flower_growth = FlowerGrowth.objects.create(user=self.request.user)

        if flower_growth.last_entry_date is None or flower_growth.last_entry_date != today:
            if flower_growth.stage < 7:
                flower_growth.increment_stage()
            flower_growth.update_last_entry_date(today)

        return super(CreateJournalEntryView, self).form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Created new entry!")
        return reverse('journal_log')

def delete_journal_entry(request,entry_id):
    entry = JournalEntry.objects.get(pk=entry_id)
    if entry.user == request.user:
        entry.delete_entry()
        messages.add_message(request, messages.SUCCESS, "Entry moved to trash!")
        return redirect('trash')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete an entry that is not yours!")
        return redirect('journal_log')
    
def recover_journal_entry(request,entry_id):
    entry = JournalEntry.objects.get(pk=entry_id)
    if entry.user == request.user:
        entry.recover_entry()
        messages.add_message(request,messages.SUCCESS,"Entry has been recovered!")
        return redirect('journal_log')
    else:
        messages.add_message(request, messages.ERROR, "entry cannot be recovered")
        return redirect('journal_log')

def delete_journal_entry_permanent(request,entry_id):
    entry = JournalEntry.objects.get(pk=entry_id)
    if entry.user == request.user:
        entry.permanently_delete()
        messages.add_message(request, messages.SUCCESS, "Entry deleted!")
        return redirect("journal_log") 
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete an entry that is not yours!")
        return redirect('journal_log')
    
def favourite_journal_entry(request,entry_id):
    entry = JournalEntry.objects.get(pk=entry_id)
    if entry.user == request.user:
        entry.favourited = True
        entry.save()
        messages.add_message(request,messages.SUCCESS,"Entry has been added to favourites!")
        return redirect('journal_log')
    else:
        messages.add_message(request, messages.ERROR, "Entry is not yours!")
        return redirect('journal_log')
    
def unfavourite_journal_entry(request,entry_id):
    entry = JournalEntry.objects.get(pk=entry_id)
    next_page = request.GET.get('next', "journal_log")
    if entry.user == request.user:
        entry.favourited = False
        entry.save()
        messages.add_message(request,messages.SUCCESS,"Entry has been removed from favourites!")
        return redirect(next_page)
    else:
        messages.add_message(request, messages.ERROR, "Entry is not yours!")
        return redirect(next_page)


def get_mood_representation(mood, use_emoji=False):
    mood_dict = {
        1: ('Very Sad', '😔'),
        2: ('Sad', '🙁'),
        3: ('Neutral', '😐'),
        4: ('Happy', '🙂'),
        5: ('Very Happy', '😄')
    }
    description, emoji = mood_dict.get(mood, ('', ''))
    return f"{description} {emoji}" if use_emoji else description


def generate_mood_chart(user):
    one_month_ago = timezone.now() - timedelta(days=30)
    entries = JournalEntry.objects.filter(user=user, created_at__gte=one_month_ago, deleted=False)
    moods = entries.values_list('mood', flat=True)
    mood_counts = Counter(moods)

    mood_labels = [get_mood_representation(mood) for mood in mood_counts.keys()]
    counts = list(mood_counts.values())

    fig, ax = plt.subplots()
    ax.bar(mood_labels, counts)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    for i, count in enumerate(counts):
        ax.text(i, count + 0.1, str(count), ha='center')

    flike = BytesIO()
    plt.savefig(flike, format='png', bbox_inches='tight')
    plt.close(fig)
    b64 = base64.b64encode(flike.getvalue()).decode()

    return b64

@login_required
def mood_breakdown(request):
    today = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    user_entries = JournalEntry.objects.filter(user=request.user, deleted=False)

    # Aggregating mood data for today, this week, and this month
    mood_today = user_entries.filter(created_at__date=today.date()).values('mood').annotate(count=Count('mood')).order_by('-count').first()
    mood_week = user_entries.filter(created_at__gte=start_of_week).values('mood').annotate(count=Count('mood')).order_by('-count').first()
    mood_month = user_entries.filter(created_at__gte=start_of_month).values('mood').annotate(count=Count('mood')).order_by('-count').first()

    # Convert mood numbers to emojis for display
    # Convert mood numbers to emojis for display
    mood_today_average = get_mood_representation(mood_today['mood'], use_emoji=True) if mood_today else 'No entries today'
    mood_week_average = get_mood_representation(mood_week['mood'], use_emoji=True) if mood_week else 'No entries this week'
    mood_month_average = get_mood_representation(mood_month['mood'], use_emoji=True) if mood_month else 'No entries this month'

    # Generate mood chart for the past month
    mood_chart = generate_mood_chart(request.user)

    context = {
        'mood_today': mood_today_average,
        'mood_week':  mood_week_average,
        'mood_month': mood_month_average,
        'mood_chart': mood_chart,
    }

    return render(request, 'mood_breakdown.html', context)


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
@login_required
def search_journal(request):
    form = JournalSearchForm(request.GET or None)
    journals = JournalEntry.objects.filter(user=request.user, deleted=False)

    if form.is_valid():
        title = form.cleaned_data.get('title')
        if title:
            journals = journals.filter(title__icontains=title)

    
    return render(request, 'journal_log.html', {'form': form, 'journal_entries': journals})


@login_required
def journal_entries(request):
    form = JournalSearchForm(request.GET or None)
    entries = JournalEntry.objects.all()
    return render(request, 'journal_log.html', {'form':form,'journal_entries': entries})


@login_required
def journal_detail(request, entry_id):
    journals = JournalEntry.objects
    entry = get_object_or_404(JournalEntry, id=entry_id)
    return render(request, 'journal_log.html', {'entry': entry})



@login_required
def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
       
        suggestions = JournalEntry.objects.filter(
            title__icontains=query,
            deleted=False
        ).values_list('title', flat=True)[:5]
    else:
        suggestions = JournalEntry.objects.filter(
            deleted=False
        ).order_by('-created_at').values_list('title', flat=True)[:5]
    return JsonResponse({'suggestions': list(suggestions)})

@login_required
def search_trash(request):
    query = request.GET.get('title', '')
    journal_entries = JournalEntry.objects.filter(
        title__icontains=query, 
        deleted=True, 
        user=request.user
    )
    return render(request, 'trash.html', {'journal_entries': journal_entries})


@login_required
def search_suggestions1(request):
    query = request.GET.get('q', '')
    if query:
        suggestions = JournalEntry.objects.filter(title__icontains=query,deleted=True).values_list('title', flat=False)[:5]
    else:
        suggestions = []
    return JsonResponse({'suggestions': list(suggestions)})

@login_required
def search_favourite (request):
    query = request.GET.get('title', '')
    journal_entries = JournalEntry.objects.filter(
        title__icontains=query, 
        deleted=False, 
        user=request.user,
        favourited = True
    )
    return render(request, 'favourites.html', {'journal_entries': journal_entries})



@login_required
def search_favouriteSuggestion(request):
    query = request.GET.get('q', '')
    if query:
        suggestions = JournalEntry.objects.filter(
            title__icontains=query, 
            favourited=True,
           
            user=request.user   
        ).values_list('title', flat=True)[:5] 
    else:
        suggestions = []
    return JsonResponse({'suggestions': list(suggestions)})