# Generated by Django 4.0.5 on 2022-06-09 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_clientuser_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientuser',
            name='points',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
