# Generated by Django 3.2.8 on 2021-11-26 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20211122_1844'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderproduct',
            old_name='additionalOptions',
            new_name='selected_items',
        ),
        migrations.RenameField(
            model_name='orderproduct',
            old_name='additionalOptionsMeta',
            new_name='selected_items_meta',
        ),
    ]
