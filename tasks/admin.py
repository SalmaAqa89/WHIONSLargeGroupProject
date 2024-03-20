from django.contrib import admin
from .models import User, UserPreferences, JournalEntry,Template
# user: @admin password: 123Admin

# Register your models here.

admin.site.register(User)
admin.site.register(UserPreferences)
admin.site.register(JournalEntry)
admin.site.register(Template)
