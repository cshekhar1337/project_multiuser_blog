from __future__ import unicode_literals
from django.utils import timezone

from django.db import models

class User_Blog(models.Model):
    '''
        Model for user_blog
    '''

    name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100, unique=True, primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    pw_hash = models.CharField(max_length=100)
    created_at = models.DateField(default=timezone.now)


    def __str__(self):
        return '%s %s %s %s' % (self.name, self.user_name, self.email, self.pw_hash)

class Blog_Post(models.Model):
    '''
        Model for user_blog
    '''
    blog_id = models.AutoField(serialize=False, primary_key=True)
    subject = models.CharField(max_length=100)
    content = models.CharField(max_length=300)
    user_name = models.ForeignKey(
        User_Blog,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(default=timezone.now)

    def __str__(self):
        return '%s %s %s %s' % (self.blog_id, self.subject, self.content, self.user_name)

class Post_Like(models.Model):
    '''
        Model for user_blog
    '''
    user_name = models.ForeignKey(
        User_Blog,
        on_delete=models.CASCADE,

    )
    blog_id = models.ForeignKey(
        Blog_Post,
        on_delete=models.CASCADE,

    )



    def __str__(self):
        return '%s %s' % (self.blog_id, self.user_name)
