# Generated by Django 3.2 on 2021-05-02 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scansion', '0007_poem_scansion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poem',
            name='human_scanned',
        ),
    ]
