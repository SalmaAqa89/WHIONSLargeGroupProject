"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from tasks.views import PageViews, AuthViews, JournalEntryViews
from ckeditor_uploader import views as ckeditor_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PageViews.home, name='home'),
    path('dashboard/', PageViews.dashboard, name='dashboard'),
    path('log_in/', AuthViews.LogInView.as_view(), name='log_in'),
    path('log_out/', AuthViews.log_out, name='log_out'),
    path('password/', AuthViews.PasswordView.as_view(), name='password'),
    path('profile/', AuthViews.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', AuthViews.SignUpView.as_view(), name='sign_up'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('journal_log/',PageViews.journal_log,name ='journal_log'),
    path('journal/entry/<int:entry_id>/pdf/', JournalEntryViews.export_journal_entry_to_pdf, name='export_journal_entry_to_pdf'),
    path('journal/entry/<int:entry_id>/rtf/', JournalEntryViews.export_journal_entry_to_rtf, name='export_journal_entry_to_rtf'),
    path('export_entries/', JournalEntryViews.export_entries, name='export_entries'),
    path('favourites/',PageViews.favourites,name ='favourites'),
    path('mood_breakdown/',JournalEntryViews.mood_breakdown,name ='mood_breakdown'),
    path('templates/',PageViews.templates,name ='templates'),
    path('trash/',PageViews.trash,name ='trash'),
    path('create_entry/', JournalEntryViews.CreateJournalEntryView.as_view(), name="create_entry"),
    path('delete_entry/<int:entry_id>', JournalEntryViews.delete_journal_entry, name="delete_entry"),
    path('favourite_entry/<int:entry_id>', JournalEntryViews.favourite_journal_entry, name="favourite_entry"),
    path('unfavourite_entry/<int:entry_id>', JournalEntryViews.unfavourite_journal_entry, name="unfavourite_entry"),
    path('delete_entry_permanent/<int:entry_id>',JournalEntryViews.delete_journal_entry_permanent,name = "delete_entry_permanent"),
    path('recover_entry/<int:entry_id>',JournalEntryViews.recover_journal_entry,name = "recover_entry"),
    path('set_preferences/',AuthViews.SetPreferences.as_view(),name = "set_preferences"),
    path('edit_preferences/',AuthViews.EditPreferences.as_view(),name = "edit_preferences"),
    path('ckeditor/', include('ckeditor_uploader.urls')), 
    path('r^ckeditor/upload/', login_required(ckeditor_views.upload), name='ckeditor_upload'),
    path('edit/<int:pk>/', JournalEntryViews.JournalEntryUpdateView.as_view(), name='edit_entry'),
    path('get_journal_entries/', JournalEntryViews.get_journal_entries, name='get_journal_entries'),
    path('create_template/',PageViews.CreateTemplateView.as_view(),name = "create_template"),
    path('template_choices/',PageViews.template_choices,name = 'template_choices'),
    


    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

