# Generated by Django 3.2.8 on 2021-11-26 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20211126_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_payed',
            field=models.BooleanField(default=False, help_text='Has been payed through Payeer'),
        ),
    ]
