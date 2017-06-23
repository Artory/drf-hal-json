from django.test import TestCase
from drf_hal_json import EMBEDDED_FIELD_NAME, LINKS_FIELD_NAME
from rest_framework.reverse import reverse

from .models import (AbundantResource, CustomResource, RelatedResource1,
                     RelatedResource2, RelatedResource3, TestResource,
                     URLResource)


class HalTest(TestCase):
    TESTSERVER_URL = "http://testserver"

    def setUp(self):
        self.related_resource_1 = RelatedResource1.objects.create(name="Related-Resource1")
        self.nested_related_resource_1_1 = RelatedResource1.objects.create(name="Nested-Related-Resource11")
        self.nested_related_resource_1_2 = RelatedResource1.objects.create(name="Nested-Related-Resource12")
        self.related_resource_2 = RelatedResource2.objects.create(name="Related-Resource2")
        self.related_resource_2.related_resources_1.add(self.nested_related_resource_1_1, self.nested_related_resource_1_2)
        self.test_resource_1 = TestResource.objects.create(name="Test-Resource", related_resource_1=self.related_resource_1,
                                                           related_resource_2=self.related_resource_2)
        self.related_resource_3 = RelatedResource3.objects.create(name="Related-Resource3")
        self.custom_resource_1 = CustomResource.objects.create(name="Custom-Resource-1", related_resource_3=self.related_resource_3)
        self.custom_resource_2 = CustomResource.objects.create(name="Custom-Resource-2", related_resource_3=self.related_resource_3,
                                                               related_resource_2=self.related_resource_2)
        self.url_resource = URLResource.objects.create(url="https://www.example.com/")

        for i in range(0, 50):
            AbundantResource.objects.create(name="Abundant Resource {}".format(i))

    def test_basic_data(self):
        resp = self.client.get("/test-resources/1/")
        self.assertEqual(200, resp.status_code, resp.content)
        test_resource_data = resp.data
        self.assertEqual(4, len(test_resource_data))
        self.assertEqual(self.test_resource_1.id, test_resource_data['id'])
        self.assertEqual(self.test_resource_1.name, test_resource_data['name'])

    def test_links(self):
        resp = self.client.get("/test-resources/1/")

        test_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertEqual(3, len(test_resource_links))
        self.assertEqual(self.TESTSERVER_URL + reverse('testresource-detail', kwargs={'pk': self.test_resource_1.id}),
                         test_resource_links['self']['href'])
        self.assertEqual(self.TESTSERVER_URL + reverse('relatedresource1-detail', kwargs={'pk': self.related_resource_1.id}),
                         test_resource_links['related_resource_1']['href'])
        self.assertEqual(self.TESTSERVER_URL + reverse('relatedresource2-detail', kwargs={'pk': self.related_resource_2.id}),
                         test_resource_links['related_resource_2']['href'])

    def test_embedded_resource_data(self):
        resp = self.client.get("/test-resources/1/")
        test_resource_data = resp.data
        related_resource_2_data = test_resource_data[EMBEDDED_FIELD_NAME]['related_resource_2']
        self.assertEqual(5, len(related_resource_2_data))
        self.assertEqual(self.related_resource_2.name, related_resource_2_data['name'])

    def test_embedded_resource_links(self):
        resp = self.client.get("/test-resources/1/")
        test_resource_data = resp.data
        related_resource_2_data = test_resource_data[EMBEDDED_FIELD_NAME]['related_resource_2']
        related_resource_2_links = related_resource_2_data[LINKS_FIELD_NAME]
        self.assertEqual(1, len(related_resource_2_links))
        self.assertEqual(self.TESTSERVER_URL + reverse('relatedresource2-detail', kwargs={'pk': self.related_resource_2.id}),
                         related_resource_2_links['self']['href'])

    def test_deep_embedding(self):
        resp = self.client.get("/test-resources/1/")
        test_resource_data = resp.data
        related_resource_2_data = test_resource_data[EMBEDDED_FIELD_NAME]['related_resource_2']
        related_resource_2_links = related_resource_2_data[LINKS_FIELD_NAME]
        related_resource_2_embedded = related_resource_2_data[EMBEDDED_FIELD_NAME]
        self.assertEqual(1, len(related_resource_2_embedded))
        nested_related_resources_data = related_resource_2_embedded['related_resources_1']
        self.assertEqual(2, len(nested_related_resources_data))
        self.assertEqual(4, len(nested_related_resources_data[0]))
        self.assertEqual(4, len(nested_related_resources_data[1]))
        self.assertEqual(self.nested_related_resource_1_1.id, nested_related_resources_data[0]['id'])
        self.assertEqual(self.nested_related_resource_1_1.name, nested_related_resources_data[0]['name'])
        self.assertEqual(
            self.TESTSERVER_URL + reverse('relatedresource1-detail', kwargs={'pk': self.nested_related_resource_1_1.id}),
            nested_related_resources_data[0][LINKS_FIELD_NAME]['self']['href'])
        self.assertEqual(self.nested_related_resource_1_2.id, nested_related_resources_data[1]['id'])
        self.assertEqual(self.nested_related_resource_1_2.name, nested_related_resources_data[1]['name'])
        self.assertEqual(
            self.TESTSERVER_URL + reverse('relatedresource1-detail', kwargs={'pk': self.nested_related_resource_1_2.id}),
            nested_related_resources_data[1][LINKS_FIELD_NAME]['self']['href'])

    def test_custom_lookup_field(self):
        resp = self.client.get("/custom-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertEqual(2, len(custom_resource_links))
        self.assertEqual(self.TESTSERVER_URL + reverse("customresource-detail", kwargs={"pk": self.custom_resource_1.id}),
                         custom_resource_links["self"]["href"])
        self.assertEqual(self.TESTSERVER_URL + reverse("relatedresource3-detail", kwargs={"name": self.custom_resource_1.name}),
                         custom_resource_links["related_resource_3"]["href"])

    def test_hypelinked_property_field(self):
        resp = self.client.get("/url-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertEqual('https://www.example.com/',
                         custom_resource_links["url"]["href"])
        self.assertEqual('https://www.example.com/?foo=bar',
                         custom_resource_links["url_processed"]["href"])

    def test_pagination(self):
        no_pages = self.client.get("/test-resources/").data
        self.assertIn("self", no_pages["_links"])
        self.assertNotIn("previous", no_pages["_links"])
        self.assertNotIn("next", no_pages["_links"])

        pages = self.client.get("/abundant-resources/").data
        self.assertIn("self", pages["_links"])
        self.assertNotIn("previous", pages["_links"])
        self.assertIn("next", pages["_links"])
        next_link = pages["_links"]["next"]["href"]

        pages = self.client.get(next_link).data
        self.assertIn("self", pages["_links"])
        self.assertIn("previous", pages["_links"])
        self.assertIn("next", pages["_links"])

    def test_empty_relation(self):
        resp = self.client.get("/custom-resources/1/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertNotIn("related_resource_2", custom_resource_links)

        resp = self.client.get("/custom-resources/2/")
        custom_resource_links = resp.data[LINKS_FIELD_NAME]
        self.assertIn("related_resource_2", custom_resource_links)
