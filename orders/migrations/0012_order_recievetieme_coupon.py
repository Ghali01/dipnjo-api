# Generated by Django 4.0.5 on 2022-06-28 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_alter_location_lat_alter_location_lng'),
        ('orders', '0011_cartitem_usedpoints_orderitem_usedpoints'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='recieveTieme',
            field=models.TimeField(null=True),
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, unique=True)),
                ('enabled', models.BooleanField(default=True)),
                ('value', models.PositiveIntegerField()),
                ('type', models.CharField(choices=[('p', 'Percent'), ('c', 'Cash')], max_length=1)),
                ('users', models.ManyToManyField(to='accounts.clientuser')),
            ],
        ),
    ]