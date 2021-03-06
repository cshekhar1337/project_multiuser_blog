# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-16 15:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_blog', '0001_mymodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.AutoField(primary_key=True, serialize=False)),
                ('comment', models.CharField(max_length=300)),
                ('blog_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_blog.Blog_Post')),
                ('user_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_blog.User_Blog')),
            ],
        ),
    ]
