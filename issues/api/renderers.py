from __future__ import unicode_literals

from django.utils import six
from django.utils.encoding import smart_text
from django.utils.six.moves import StringIO
from django.utils.xmlutils import SimplerXMLGenerator
from rest_framework.renderers import BaseRenderer, JSONRenderer

from issues.api.transforms import transform_xml_to_json


def order_by_sort_order(sort_order):
    """
    Generate a function for sorting values according to a list.

    :param sort_order: The sort order list.
    :return: Return a function that is usable as a `key=` for `sorted()`.

    """
    keys = set(sort_order)

    def keyfunc(val):
        return (
            sort_order.index(val) if (val in keys) else None,
            val
        )

    return keyfunc


class XMLRenderer(BaseRenderer):
    """
    Renderer which serializes to XML.
    Based on https://github.com/jpadilla/django-rest-framework-xml
    """

    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    item_tag_name = 'list-item'
    root_tag_name = 'root'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return ''
        view = (renderer_context.get("view") if renderer_context else None)
        self.item_tag_name = getattr(view, "item_tag_name", self.item_tag_name)
        self.root_tag_name = getattr(view, "root_tag_name", self.root_tag_name)
        stream = StringIO()
        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        root_tag_name = (getattr(data, "xml_tag", None) or self.root_tag_name)
        xml.startElement(root_tag_name, {})
        self._to_xml(xml, data)
        xml.endElement(root_tag_name)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if data is True:
            return xml.characters('true')
        if data is False:
            return xml.characters('false')

        if isinstance(data, (list, tuple)):
            for item in data:
                tag_name = (getattr(data, "xml_tag", None) or self.item_tag_name)
                xml.startElement(tag_name, {})
                self._to_xml(xml, item)
                xml.endElement(tag_name)

        elif isinstance(data, dict):
            key_order = getattr(data, "key_order", ())
            for key in sorted(six.iterkeys(data), key=order_by_sort_order(key_order)):
                xml.startElement(key, {})
                self._to_xml(xml, data[key])
                xml.endElement(key)

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(smart_text(data))


class SparkJSONRenderer(JSONRenderer):
    ensure_ascii = False
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        xml = XMLRenderer().render(
            data,
            accepted_media_type=XMLRenderer.media_type,
            renderer_context=renderer_context
        )
        return transform_xml_to_json(xml)
