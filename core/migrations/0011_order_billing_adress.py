# Generated by Django 2.2 on 2021-07-23 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_billingadress'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='billing_adress',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.BillingAdress'),
        ),
    ]
