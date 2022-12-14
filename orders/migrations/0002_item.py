# Generated by Django 4.0.5 on 2022-06-09 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_clientuser_user'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('r', 'rejected'), ('c', 'cooking'), ('w', 'waiting'), ('d', 'delivering'), ('f', 'finshed')], max_length=1)),
                ('payMethod', models.CharField(choices=[('ca', 'cash'), ('cc', 'card')], max_length=2)),
                ('total', models.PositiveIntegerField()),
                ('inStore', models.BooleanField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.clientuser')),
            ],
        ),
    ]
