# Generated by Django 5.1.2 on 2024-11-14 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procurement01', '0014_alter_rfp_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]