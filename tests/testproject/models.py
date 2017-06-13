from django.db import models


class RelatedResource1(models.Model):
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)


class RelatedResource2(models.Model):
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    related_resources_1 = models.ManyToManyField(RelatedResource1)


class RelatedResource3(models.Model):
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)


class TestResource(models.Model):
    created = models.DateTimeField(auto_now=True)
    related_resource_1 = models.ForeignKey(RelatedResource1)
    related_resource_2 = models.OneToOneField(RelatedResource2)
    name = models.CharField(max_length=255)


class CustomResource(models.Model):
    created = models.DateTimeField(auto_now=True)
    related_resource_3 = models.ForeignKey(RelatedResource3)
    name = models.CharField(max_length=255)

    @property
    def some_id(self):
        return None



class AbundantResource(models.Model):
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)

