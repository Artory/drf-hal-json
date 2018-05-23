from django.core.files.base import ContentFile
from django.test import TestCase
from drf_hal_json import EMBEDDED_FIELD_NAME, LINKS_FIELD_NAME
from rest_framework.reverse import reverse

from .models import (AbundantResource, CustomResource, FileResource, RelatedResource1, RelatedResource2,
                     RelatedResource3, SlugRelatedResource, TestResource, URLResource)


class HalTest(TestCase):
    TESTSERVER_URL = "http://testserver"

    def setUp(self):
        self.related_resource_1 = RelatedResource1.objects.create(name="Related-Resource1")
        self.nested_related_resource_1_1 = RelatedResource1.objects.create(name="Nested-Related-Resource11")
        self.nested_related_resource_1_2 = RelatedResource1.objects.create(name="Nested-Related-Resource12")
        self.related_resource_2 = RelatedResource2.objects.create(name="Related-Resource2")
        self.related_resource_2.related_resources_1.add(
            self.nested_related_resource_1_1, self.nested_related_resource_1_2)
        self.test_resource_1 = TestResource.objects.create(
            name="Test-Resource",
            related_resource_1=self.related_resource_1,
            related_resource_2=self.related_resource_2)
        self.related_resource_3 = RelatedResource3.objects.create(name="Related-Resource3")
        self.custom_resource_1 = CustomResource.objects.create(
            name="Custom-Resource-1", related_resource_3=self.related_resource_3)
        self.custom_resource_2 = CustomResource.objects.create(
            name="Custom-Resource-2",
            related_resource_3=self.related_resource_3,
            related_resource_2=self.related_resource_2)
        self.url_resource = URLResource.objects.create(
            url_abs="https://www.example.com/",
            url_rel="/example/")
        self.file_resource = FileResource()
        self.file_resource.file.save('foo', ContentFile(b'bar'))
        self.file_resource.image.save('image', ContentFile(b'JPEG'))
        self.slug_resource = SlugRelatedResource()
        self.slug_resource.save()
        self.slug_resource.slug_related.add(self.test_resource_1)
        self.slug_resource.save()

        for i in range(0, 50):
            AbundantResource.objects.create(name="Abundant Resource {}".format(i))

    def test_basic_data(self):
        resp = self.client.get("/test-resources/1/")
        self.assertEqual(200, resp.status_code, resp.content)
        test_resource_data = resp.data
        self.assertEqual(
            {'_embedded', '_links', 'id', 'name'},
            set(test_resource_data.keys())
        )
        self.assertEqual(self.test_resource_1.id, test_resource_data['id'])
        self.assertEqual(self.test_resource_1.name, test_resource_data['name'])

    def test_links(self):
        resp = self.client.get("/test-resources/1/")

        test_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertEqual(
            {'self', 'related_resource_2', 'related_resource_1'},
            set(test_resource_links.keys())
        )
        self.assertEqual(self.TESTSERVER_URL + reverse('testresource-detail', kwargs={'pk': self.test_resource_1.id}),
                         test_resource_links['self']['href'])
        self.assertEqual(
            self.TESTSERVER_URL + reverse('relatedresource1-detail', kwargs={'pk': self.related_resource_1.id}),
            test_resource_links['related_resource_1']['href'])
        self.assertEqual(
            self.TESTSERVER_URL + reverse('relatedresource2-detail', kwargs={'pk': self.related_resource_2.id}),
            test_resource_links['related_resource_2']['href'])

    def test_embedded_resource_data(self):
        resp = self.client.get("/test-resources/1/")
        test_resource_data = resp.data
        related_resource_2_data = test_resource_data[EMBEDDED_FIELD_NAME]['related_resource_2']
        self.assertEqual(
            {'active', '_links', '_embedded', 'name', 'id'},
            set(related_resource_2_data.keys())
        )
        self.assertEqual(self.related_resource_2.name, related_resource_2_data['name'])

    def test_embedded_resource_links(self):
        resp = self.client.get("/test-resources/1/")
        test_resource_data = resp.data
        related_resource_2_data = test_resource_data[EMBEDDED_FIELD_NAME]['related_resource_2']
        related_resource_2_links = related_resource_2_data[LINKS_FIELD_NAME]
        self.assertEqual(
            {'related_resources_1', 'self', 'related_resources'},
            set(related_resource_2_links.keys())
        )
        self.assertEqual(
            self.TESTSERVER_URL + reverse('relatedresource2-detail', kwargs={'pk': self.related_resource_2.id}),
            related_resource_2_links['self']['href'])

    def test_link_titles(self):
        resp = self.client.get("/related-resources-2/1/")
        self.assertIn('related_resources_1', resp.data[LINKS_FIELD_NAME])
        related = resp.data[LINKS_FIELD_NAME]['related_resources_1']
        self.assertEqual(2, len(related))
        self.assertEqual('Nested-Related-Resource11', related[0]['title'])
        self.assertEqual('Nested-Related-Resource12', related[1]['title'])

    def test_custom_lookup_field(self):
        resp = self.client.get("/custom-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertEqual(
            {'self', 'related_resource_3', 'custom_link', 'custom_link_empty'},
            set(custom_resource_links.keys())
        )
        self.assertEqual(
            self.TESTSERVER_URL + reverse("customresource-detail", kwargs={"pk": self.custom_resource_1.id}),
            custom_resource_links["self"]["href"])
        self.assertEqual(
            self.TESTSERVER_URL + reverse("relatedresource3-detail", kwargs={"name": self.custom_resource_1.name}),
            custom_resource_links["related_resource_3"]["href"])
        self.assertEqual(self.custom_resource_1.name,
                         custom_resource_links["related_resource_3"]["title"])

    def test_hyperlinked_property_field(self):
        resp = self.client.get("/url-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertEqual('https://www.example.com/',
                         custom_resource_links["url_abs"]["href"])
        self.assertEqual(self.TESTSERVER_URL + '/example/',
                         custom_resource_links["url_rel"]["href"])
        self.assertEqual('https://www.example.com/?foo=bar',
                         custom_resource_links["url_abs_processed"]["href"])
        self.assertEqual(self.TESTSERVER_URL + '/example/?foo=bar',
                         custom_resource_links["url_rel_processed"]["href"])

    def test_slug(self):
        slug = self.client.get("/slug-resources/1/").data
        self.assertEqual(
            {LINKS_FIELD_NAME, 'slug_related'},
            set(slug.keys())
        )
        self.assertNotIn('slug_related', slug[LINKS_FIELD_NAME])

    def test_pagination(self):
        no_pages = self.client.get("/test-resources/").data
        self.assertIn("self", no_pages[LINKS_FIELD_NAME])
        self.assertNotIn("previous", no_pages[LINKS_FIELD_NAME])
        self.assertNotIn("next", no_pages[LINKS_FIELD_NAME])

        pages = self.client.get("/abundant-resources/").data
        self.assertIn("self", pages[LINKS_FIELD_NAME])
        self.assertNotIn("previous", pages[LINKS_FIELD_NAME])
        self.assertIn("next", pages[LINKS_FIELD_NAME])
        next_link = pages[LINKS_FIELD_NAME]["next"]["href"]
        self.assertEqual(len(pages['_embedded']['items']), 10)

        unpaged = self.client.get("/abundant-unpaged/").data
        # Renders with _links and _embedded
        self.assertIn("_links", unpaged)
        self.assertIn("_embedded", unpaged)
        self.assertIn("self", unpaged["_links"])
        # Includes no pages
        self.assertNotIn("previous", unpaged["_links"])
        self.assertNotIn("next", unpaged["_links"])

        pages = self.client.get(next_link).data
        self.assertIn("self", pages[LINKS_FIELD_NAME])
        self.assertIn("previous", pages[LINKS_FIELD_NAME])
        self.assertIn("next", pages[LINKS_FIELD_NAME])

    def test_empty_relation(self):
        resp = self.client.get("/custom-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertNotIn("related_resource_2", custom_resource_links)

        resp = self.client.get("/custom-resources/2/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertIn("related_resource_2", custom_resource_links)

    def test_filefield_serialization(self):
        resp = self.client.get("/file-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertNotIn("file", custom_resource_links,
                         msg="basic FileFields should not be included in links")
        self.assertNotIn("none", custom_resource_links['self'],
                         msg="HalContributeToLinkField returning None should be suppressed")

    def test_readme_contribute_example(self):
        resp = self.client.get("/hal-file-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertIn("file", custom_resource_links,
                      msg='HalFileField should be included in _links')
        self.assertIn("title", custom_resource_links['file'],
                      msg='HalContributeToLinkField should have been included in _links.file')
        self.assertIn("type", custom_resource_links['file'],
                      msg='HalContributeToLinkField should have been included in _links.file')
        self.assertEqual(custom_resource_links['file']['type'], "application/zip",
                         msg='_links.file.type should equal static return of get_file_type (i.e. "application/zip")')

    def test_serializer_method_link(self):
        resp = self.client.get("/custom-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertIn("custom_link", custom_resource_links)
        self.assertEqual("http://www.example.com", custom_resource_links["custom_link"]["href"])
        self.assertIsNone(custom_resource_links["custom_link_empty"]["href"])
