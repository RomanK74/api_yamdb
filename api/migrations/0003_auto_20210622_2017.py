# Generated by Django 3.0.5 on 2021-06-22 17:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20210622_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.PositiveSmallIntegerField(default=10, help_text='Введите от 1 до 10', validators=[django.core.validators.MinValueValidator(1, message='Оценка должна быть от 1 до 10'), django.core.validators.MaxValueValidator(10, message='Оценка должна быть от 1 до 10')], verbose_name='Оценка'),
        ),
    ]
