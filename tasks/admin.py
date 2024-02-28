from django.contrib import admin
from .models import User, UserPreferences, JournalEntry
# user: @admin password: 123Admin
# Register your models here.

admin.site.register(User)
admin.site.register(UserPreferences)
admin.site.register(JournalEntry)
