# Generated by Django 4.2.6 on 2024-01-30 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_alter_user_preferred_days_to_journal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='preferred_time_to_journal',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
