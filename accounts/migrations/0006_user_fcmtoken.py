# Generated by Django 4.0.5 on 2022-06-11 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_clientuser_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fcmToken',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
