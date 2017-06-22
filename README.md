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
        'DEFAULT_RENDERER_CLASSES': ('drf_hal_json.renderers.JsonHalRenderer',),

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

## Example ##

Serializer:

    class ResourceSerializer(HalModelSerializer):
        class Meta:
            model = Resource

View:
    
    class ResourceViewSet(HalCreateModelMixin, ModelViewSet):
        serializer_class = ResourceSerializer
        queryset = Resource.objects.all()

Request:

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
    
### Link titles

The optional `title` attribute is supported for link relations. If a serializer includes a field called
`title`, it will not be serialized as part of the object itself. Instead, the `title` field enhances
the link relation of the object.

See the [test project][] for a complete Django project with more examples. 

## Contributing

Run tests:

```
$> make test
```

[test project]: tests/
