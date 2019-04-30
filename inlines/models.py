from builtins import object
from django.db import models
from django.contrib.contenttypes.models import ContentType


class InlineType(models.Model):
    """InlineType model"""
    title = models.CharField(max_length=200)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )

    class Meta(object):
        db_table = 'inline_types'

    def __unicode__(self):
        return self.title
