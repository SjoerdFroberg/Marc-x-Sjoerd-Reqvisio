# Generated by Django 4.2.16 on 2024-12-05 09:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('procurement01', '0012_oem_company_oems'),
    ]

    operations = [
        migrations.AddField(
            model_name='oem',
            name='procurer',
            field=models.ForeignKey(default=17, limit_choices_to={'company_type': 'Procurer'}, on_delete=django.db.models.deletion.CASCADE, related_name='procurer_oems', to='procurement01.company'),
            preserve_default=False,
        ),
    ]