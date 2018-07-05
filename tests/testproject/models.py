from django.db import models


class RelatedResource1(models.Model):
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    @property
    def _link_title(self):
        return 'some title'


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
    related_resource_1 = models.ForeignKey(
        RelatedResource1, on_delete=models.CASCADE)
    related_resource_2 = models.OneToOneField(
        RelatedResource2, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class CustomResource(models.Model):
    created = models.DateTimeField(auto_now=True)
    related_resource_2 = models.ForeignKey(
        RelatedResource2, on_delete=models.CASCADE, null=True, default=None)
    related_resource_3 = models.ForeignKey(
        RelatedResource3, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)


class SlugRelatedResource(models.Model):
    slug_related = models.ManyToManyField(TestResource)


class AbundantResource(models.Model):
    created = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)


class URLResource(models.Model):
    url_abs = models.CharField(max_length=255)
    url_rel = models.CharField(max_length=255)


class FileResource(models.Model):
    file = models.FileField(max_length=255, upload_to='./tmp')
    image = models.ImageField(max_length=255, upload_to='./tmp')
