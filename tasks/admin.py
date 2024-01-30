from django.contrib import admin
from .models import User, Template

""" Superuser created with username: admin_user, password: 1234AdminUser!"""

# Register your models here.
admin.site.register(User)