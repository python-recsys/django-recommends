from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from .converters import get_identifier
from .managers import RecommendsManager, SimilarityResultManager, RecommendationManager


class RecommendsBaseModel(models.Model):
    """(RecommendsBaseModel description)"""
    object_ctype = models.ForeignKey(ContentType, related_name="%(app_label)s_%(class)s_object_ctypes")
    object_id = models.PositiveIntegerField()
    object_site = models.ForeignKey(Site, related_name="%(app_label)s_%(class)s_object_sites")

    objects = RecommendsManager()

    class Meta:
        abstract = True
        unique_together = ('object_ctype', 'object_id', 'object_site')

    def __unicode__(self):
        return u"RecommendsBaseModel"

    def _object_identifier(self, ctype, object_id):
        obj = ctype.get_object_for_this_type(pk=object_id)
        return get_identifier(obj)

    def object_identifier(self):
        return self._object_identifier(self.object_ctype, self.object_id)

    def get_object(self):
        ModelClass = self.object_ctype.model_class()
        return ModelClass.objects.get(pk=self.object_id)

    # We can't use a callable name 'get_object' in the django admin, so we have to alias it.
    def get_subject(self):
        return self.get_object()
    get_subject.short_description = u"subject"


class SimilarityResult(RecommendsBaseModel):
    """How much an object is similar to another"""

    score = models.FloatField(null=True, blank=True, default=None)

    related_object_ctype = models.ForeignKey(ContentType, related_name="%(app_label)s_%(class)s_related_object_ctypes")
    related_object_id = models.PositiveIntegerField()
    related_object_site = models.ForeignKey(Site, related_name="%(app_label)s_%(class)s_related_object_sites")

    objects = SimilarityResultManager()

    class Meta:
        unique_together = ('object_ctype', 'object_id', 'object_site', 'related_object_ctype', 'related_object_id', 'related_object_site')
        ordering = ['-score']

    def __unicode__(self):
        return u"Similarity between %s and %s" % (self.get_object(), self.get_related_object())

    def related_object_identifier(self):
        return self._object_identifier(self.related_object_ctype, self.related_object_id)

    def get_related_object(self):
        ModelClass = self.related_object_ctype.model_class()
        return ModelClass.objects.get(pk=self.related_object_id)
    get_related_object.short_description = u"related object"


class Recommendation(RecommendsBaseModel):
    """Recommended an object for a particular user"""
    user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_users")
    score = models.FloatField(null=True, blank=True, default=None)

    objects = RecommendationManager()

    class Meta:
        unique_together = ('object_ctype', 'object_id', 'user')
        ordering = ['-score']

    def __unicode__(self):
        return u"Recommendation for user %s" % (self.user)
