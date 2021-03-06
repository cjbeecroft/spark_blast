# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 19:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0008_remove_dataset_jobs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='databases',
        ),
        migrations.AlterField(
            model_name='raw',
            name='database',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raw_data', to='webapp.Database'),
        ),
        migrations.AlterField(
            model_name='raw',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='raw_data', to='webapp.Dataset'),
        ),
    ]
