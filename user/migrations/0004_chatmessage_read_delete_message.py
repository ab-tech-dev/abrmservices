# Generated by Django 5.1.3 on 2025-01-17 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='read',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
