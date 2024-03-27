from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404, get_list_or_404
from tasks.models import FlowerGrowth, JournalEntry, UserPreferences, User,Template
from tasks.helpers import login_prohibited
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from tasks.models import JournalEntry
from tasks.helpers import login_prohibited
from tasks.models import JournalEntry
from tasks.helpers import login_prohibited
from datetime import datetime, timedelta
from reportlab.lib.enums import TA_CENTER
from datetime import timedelta
from django.urls import reverse
from django.db.models import F
from tasks.forms import TemplateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView, UpdateView
from django.db.models import Q





DEFAULT_TEMPLATE = {"name" : "Default template", "text" : "This is the default template","placeholder":"replace this text with your own questions"}

@login_required
def dashboard(request):
        try:
            stage = request.user.flowergrowth.stage
        except FlowerGrowth.DoesNotExist:
            stage = 0
        flower_image_url = get_flower_stage_image(stage) 

        return render(request, 'pages/dashboard.html', {'journal_entries' : JournalEntry.objects.filter(user=request.user),
                                                        'flower_image_url' : flower_image_url,})


@login_required
def journal_log(request):
    start_date = timezone.now() - timedelta(days=30)
    end_date = timezone.now()
    query = Q(user=request.user)
    search_key = request.POST.get('search')
    if search_key:
         query &= Q(title__icontains=search_key) | Q(text__icontains=search_key) 
    last_30_days_query = query & Q(created_at__range=(start_date, end_date))
    return render(request, 'pages/journal_log.html', {'journal_entries' : JournalEntry.objects.filter(query).order_by('-created_at'),
                                                      'journal_entries_last_thirty_days' :  JournalEntry.objects.filter(last_30_days_query).order_by('-created_at')})

@login_required
def favourites(request):
    query = Q(user=request.user) & Q(favourited=True)
    search_key = request.POST.get('search')
    if search_key:
         query &= Q(title__icontains=search_key) | Q(text__icontains=search_key)
    return render(request, 'pages/favourites.html', {'journal_entries' : JournalEntry.objects.filter(query)})

@login_required
def templates(request):
    return render(request, 'pages/templates.html', {'templates':Template.objects.all()})

@login_required
def trash(request):
    query = Q(user=request.user) & Q(deleted=True) & Q( permanently_deleted=False)
    search_key = request.POST.get('search')
    if search_key:
         query &= Q(title__icontains=search_key) | Q(text__icontains=search_key)
    return render(request, 'pages/trash.html',{'journal_entries' : JournalEntry.objects.filter(query)})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'pages/home.html')


def get_flower_stage_image(stage):
    image_dict = {
        0: 'images/flower_stage_0.png',
        1: 'images/flower_stage_1.png',
        2: 'images/flower_stage_2.png',
        3: 'images/flower_stage_3.png',
        4: 'images/flower_stage_4.png',
        5: 'images/flower_stage_5.png',
        6: 'images/flower_stage_6.png',
        7: 'images/flower_stage_7.png',
    }
    return image_dict.get(stage, 'images/flower_stage_0.png')

def template_choices(request):
    if request.method == 'POST':
        selected_template_name = request.POST.get('selected_template_name')
        request.session['template_name'] = selected_template_name
        return redirect('create_entry')

    templates = Template.objects.all()  
    context = {'templates': templates}
    
    return render(request, 'pages/template_choices.html', context)

class CreateTemplateView(LoginRequiredMixin, FormView):
    """Display the create template screen and handle entry creation"""

    form_class = TemplateForm
    template_name = "components/create_template.html"

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the create entry form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user, 'text': DEFAULT_TEMPLATE["placeholder"]})
        return kwargs


    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    

    def get_success_url(self):
        return reverse('templates')