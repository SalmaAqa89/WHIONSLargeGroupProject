from django.contrib import admin
from tasks.models import UserPreferences, User


admin.site.register(User)
admin.site.register(UserPreferences)

# Register your models here.
