# Generated by Django 4.0.3 on 2022-06-11 05:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foods', '0006_food_points_alter_addition_food'),
        ('orders', '0003_rename_item_oredr'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('f', 'free'), ('p', 'paid')], max_length=1)),
                ('count', models.PositiveSmallIntegerField()),
                ('additions', models.ManyToManyField(to='foods.addition')),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foods.food')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.oredr')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
