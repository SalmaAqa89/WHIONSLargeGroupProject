# Generated by Django 4.2.6 on 2024-03-27 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0003_remove_user_email_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='permanently_deleted',
            field=models.BooleanField(default=False),
        ),
    ]