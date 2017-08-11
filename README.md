[![Build Status](https://travis-ci.org/Artory/drf-hal-json.svg?branch=master)](https://travis-ci.org/Artory/drf-hal-json)

drf-hal-json
=================
Extension for Django REST Framework 3 which allows for using content-type application/hal-json.

## Status ##

This fork of https://github.com/seebass/drf-hal-json is under active development.
As soon as there is a stable version ready, we'll do a merge and push a PyPI package.
Until then this should not be considered stable.

## Setup ##

    pip install drf-hal-json

    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'drf_hal_json.pagination.HalPageNumberPagination',
        'DEFAULT_PARSER_CLASSES': ('drf_hal_json.parsers.JsonHalParser',),
        'DEFAULT_RENDERER_CLASSES': (
            'drf_hal_json.renderers.JsonHalRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),

        # To make self links render as 'self' and not 'url', as per the HAL spec
        'URL_FIELD_NAME': 'self',
    }

## Requirements ##

* Python 3.4+
* Django 1.11+
* Django REST Framework 3

## Features ##

By using the **HalModelSerializer** the content is serialized in the HAL JSON format.

Pagination is supported and will produce `next` and `previous` links.

Model-level relations are both `_linked` and `_embedded` per default. For only
linking, use `HalHyperlinkedRelatedField` in the serializer.

Django `FileField` and `ImageField` fields are automatically rendered as links.

## Example ##

Serializer:

```python
    class ResourceSerializer(HalModelSerializer):
        class Meta:
            model = Resource
```

View:

```python
    class ResourceViewSet(HalCreateModelMixin, ModelViewSet):
        serializer_class = ResourceSerializer
        queryset = Resource.objects.all()
```

Request:

```
    GET http://localhost/api/resources/1/ HTTP/1.1
    Content-Type  application/hal+json

    {
        "_links": {
            "self": {"href": "http://localhost/api/resources/1/"},
            "relatedResource": {"href": "http://localhost/api/related-resources/1/"}
        },
        "id": 1,
        "_embedded": {
            "subResource": {
                "_links": {
                    "self": {"href": "http://localhost/resources/1/sub-resources/26/"},
                    "subSubResource": {"href": "http://localhost/resources/1/sub-resources/26/sub-sub-resources/3"}
                },
                "id": 26,
                "name": "Sub Resource 26"
            }
        }
    }
```

### Optional link properties

The HAL spec defines a number of optional link properties, such as [`title`][hal spec title].
These are supported in two different ways.

#### Applying optional properties to links defined as model relations

If the link relationship is based on a model-layer relationship, you can use
`HalHyperlinkedRelatedField`, which supports a number of additional keyword
parameters, corresponding to the optional link properties in the HAL specification:

```python
from drf_hal_json.fields import HalHyperlinkedRelatedField

class Resource1Serializer(HalModelSerializer):
    # when using HalHyperlinkedRelatedField, the related resources
    # will not be embedded, just linked.
    related_resources = HalHyperlinkedRelatedField(
        many=True, read_only=True, view_name='relatedresource-detail',
        title_field='name')  # .. also type_field, templated_field, etc.

    class Meta:
        model = Resource1
        fields = ('self', 'related_resources')
```

The above will look up the `name` field of the each related resource and
use that as the link `title`.

There is also a `HalHyperlinkedIdentityField` which behaves in the same way.

#### Contributing optional properties to links directly

The other way to add custom properties to a link relation is to use
`HalContributeToLinkField`. This requires a serializer method to be
added.

```python
from drf_hal_json.fields import HalContributeToLinkField

class FileSerializer(HalModelSerializer):
    file_title = HalContributeToLinkField(place_on='file')
    file_type = HalContributeToLinkField(place_on='file', property_name='type')

    class Meta:
        model = FileResource
        fields = ('file', 'file_title', 'file_type')

    def get_file_title(self, obj):
        return str(obj.pk)

    def get_file_type(self, obj):
        return 'application/zip'
```

In the above example, we ride on the fact that Django `FileField`
and `ImageField` fields are automatically rendered as links.

`HalContributeToLinkField` can be used for any model-level relation
which are not explicitly linked using `HalHyperlinkedRelatedField`.
In this case, `HalContributeToLinkField` can be used to adorn the `self`
relation of the resource that is linked to with additional properties.

### Other link types

If you need to process a link URL, or need to insert a URL that is
completely separate from whatever model you are serializing, the
`HalHyperlinkedPropertyField` can be used.

``` python
from drf_hal_json.fields import HalHyperlinkedPropertyField

class ResourceWithUrl(Model):
    @property
    def get_docs_url(self):
        return '/docs/foo'

    @property
    def external_url(self):
        return 'http://example.com/'

class CustomSerializer(HalModelSerializer):
    docs_url = HalHyperlinkedPropertyField(
        source='get_docs_url',
        process_value=lambda val: val + '?bar')
    external_url = HalHyperlinkedPropertyField()

    class Meta:
        model = ResourceWithUrl
        fields = ('self', 'docs_url', 'external_url')
```

This will serialize into:

``` json
{
    "_links": {
        "docs_url": {
            "href": "http://localhost/docs/foo?bar"
        },
        "external_url": {
            "href": "http://example.com/"
        }
    }
}
```

### Example project

See the tests for a complete example project that excercises all the features
of this library.

## Contributing

Run tests:

```
$> make test
```

[test project]: tests/
[hal spec title]: https://tools.ietf.org/html/draft-kelly-json-hal-06#section-5.7
