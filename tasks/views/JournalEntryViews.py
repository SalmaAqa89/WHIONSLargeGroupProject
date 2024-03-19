from venv import logger
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from matplotlib.ticker import MaxNLocator
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, JournalEntryForm, UserPreferenceForm
from tasks.models import FlowerGrowth, JournalEntry, UserPreferences, User
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


DEFAULT_TEMPLATE = {"name" : "Default template", "text" : "This is the default template"}


class CreateJournalEntryView(LoginRequiredMixin, FormView):
    """Display the create entry screen and handle entry creation"""

    form_class = JournalEntryForm
    template_name = "components/create_entry.html"

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

    return render(request, 'pages/mood_breakdown.html', context)

def export_journal_entry_to_pdf(request, entry_id):
    journal_entry = get_object_or_404(JournalEntry, pk=entry_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{journal_entry.title}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, 800, journal_entry.title) 

    p.setFont("Helvetica", 12)
    text_object = p.beginText(72, 780)  
    text_object.setLeading(15)  

    for line in journal_entry.text.split('\n'):  
        text_object.textLine(line)
   
    p.drawText(text_object)

    p.showPage()
    p.save()
    return response

def export_journal_entry_to_rtf(request, entry_id):
    journal_entry = get_object_or_404(JournalEntry, pk=entry_id)
    response = HttpResponse(content_type='application/rtf')
    response['Content-Disposition'] = f'attachment; filename="{journal_entry.title}.rtf"'
    rtf_content = "{\\rtf1\\ansi\\deff0 "
    rtf_content += "{\\b " + journal_entry.title + "}"
    rtf_content += "\\line "
    rtf_content += journal_entry.text.replace('\n', '\\line ')
    rtf_content += " }"

    response.write(rtf_content)
    return response

def get_pdf_elements_for_entry(entry, styles):
    elements = []
    title_style = ParagraphStyle(name='title_style', parent=styles['Title'], alignment=TA_CENTER)
    
   
    elements.append(Paragraph(entry.title, title_style))
    elements.append(Spacer(1, 12))
    

    content_style = styles['BodyText']
    elements.append(Paragraph(entry.text, content_style))
    elements.append(PageBreak())  

    return elements
def get_rtf_content_for_entry(entry):
    rtf_content = []
    rtf_content.append(r"{\pard\qc\b " + entry.title + r"\b0\par}")  
    rtf_content.append(r"{\pard " + entry.text.replace("\n", r"\par ") + r"\par}") 
    rtf_content.append(r"\page") 
    return "\n".join(rtf_content)

def export_entries(request):
    entry_ids = request.GET.get('entries', '').split(',')
    entry_ids = [int(id) for id in entry_ids if id.isdigit()]
    export_format = request.GET.get('format', 'pdf')

    entries = get_list_or_404(JournalEntry, id__in=entry_ids)

    if export_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="journal_entries.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        for entry in entries:
            elements += get_pdf_elements_for_entry(entry, styles)
        
        doc.build(elements)
        return response

    elif export_format == 'rtf':
        response = HttpResponse(content_type='application/rtf')
        response['Content-Disposition'] = 'attachment; filename="journal_entries.rtf"'
        
        rtf_content = []
        rtf_content.append(r"{\rtf1\ansi")  
        for entry in entries:
            rtf_content.append(get_rtf_content_for_entry(entry))
        rtf_content.append("}")  

        response.write("\n".join(rtf_content))
        return response

    else:
        return HttpResponse("Unsupported format", status=400)

    
