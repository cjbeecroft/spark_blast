# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 19:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0009_auto_20170822_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raw',
            name='database',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='raw_data', to='webapp.Database'),
        ),
        migrations.AlterField(
            model_name='raw',
            name='dataset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='raw_data', to='webapp.Dataset'),
        ),
    ]
