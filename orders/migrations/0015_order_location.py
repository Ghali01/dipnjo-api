# Generated by Django 4.0.5 on 2022-06-28 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_location_lat_alter_location_lng'),
        ('orders', '0014_order_coupon_alter_order_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.location'),
            preserve_default=False,
        ),
    ]
