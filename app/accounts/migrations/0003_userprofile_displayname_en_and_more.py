# Generated by Django 5.2.4 on 2025-07-14 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='displayname_en',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='displayname_th',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
