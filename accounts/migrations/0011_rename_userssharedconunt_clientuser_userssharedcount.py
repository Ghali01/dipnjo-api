# Generated by Django 4.0.5 on 2022-06-29 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_clientuser_sharecodevalidated_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clientuser',
            old_name='usersSharedConunt',
            new_name='usersSharedCount',
        ),
    ]
