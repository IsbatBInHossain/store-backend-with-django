# Generated by Django 5.0.3 on 2024-03-29 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_review'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='descripiton',
            new_name='descripition',
        ),
    ]
