# Generated by Django 4.0.5 on 2022-06-26 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_remove_order_total_orderitem_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='usedPoints',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='usedPoints',
            field=models.PositiveIntegerField(default=0),
        ),
    ]