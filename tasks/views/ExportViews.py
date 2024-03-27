""" Views for exporting pdfs and rtfs of journal entries.
    As the majority of these views are comprised of helper methods the code is not covered by unit tests.
    The views are tested as a conjunction of each other in tasks.tests.views.test_export_journal_entry.py .
"""
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

