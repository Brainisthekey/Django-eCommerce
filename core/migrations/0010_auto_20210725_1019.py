# Generated by Django 2.2 on 2021-07-25 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20210725_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdevilevered',
            name='item_title',
        ),
        migrations.AddField(
            model_name='orderdevilevered',
            name='item_title',
            field=models.CharField(default=False, max_length=100),
        ),
    ]