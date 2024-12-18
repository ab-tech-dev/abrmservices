# Generated by Django 5.0.1 on 2024-10-11 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abrmservices', '0004_delete_house_remove_listing_city_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='listing',
            name='sale_type',
            field=models.CharField(choices=[('For Sale', 'For Sale'), ('For Rent', 'For Rent')], default='For Sale', max_length=8),
        ),
        migrations.AlterField(
            model_name='listing',
            name='zipcode',
            field=models.CharField(max_length=20),
        ),
    ]
