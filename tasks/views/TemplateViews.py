
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
from tasks.models import FlowerGrowth, JournalEntry, UserPreferences, User,Template
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
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from reportlab.lib.enums import TA_CENTER
from datetime import timedelta
import os
import re
from PyPDF2 import PdfMerger
from xhtml2pdf import pisa
import tempfile
import json 
from tasks.forms import JournalSearchForm
from django.utils.html import mark_safe


def delete_template(request,template_id):
    template = Template.objects.get(pk=template_id)
    if template.user_entry:
        template.delete_template()
        messages.add_message(request, messages.SUCCESS, "Template moved to trash!")
        return redirect('templates')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete a premade template!")
        return redirect('templates')
    

def recover_template_entry(request,template_id):
    template = Template.objects.get(pk=template_id)
    if template.user_entry:
        template.recover_entry()
        messages.add_message(request,messages.SUCCESS,"Entry has been recovered!")
        return redirect('trash')
    else:
        messages.add_message(request, messages.ERROR, "entry cannot be recovered")
        return redirect('trash')

def delete_template_entry_permanent(request,template_id):
    template = Template.objects.get(pk=template_id)
    if template.user_entry:
        template.permanently_delete()
        messages.add_message(request, messages.SUCCESS, "Entry deleted!")
        return redirect("trash") 
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete a premade template!")
        return redirect('trash')