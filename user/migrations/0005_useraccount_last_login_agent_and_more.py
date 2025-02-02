# Generated by Django 5.1.3 on 2025-01-29 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_failedloginattempt_useraccount_google_authenticated_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='last_login_agent',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='last_login_ip',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='last_login_location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
