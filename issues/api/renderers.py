import io

from django.utils.encoding import smart_text
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
        stream = io.StringIO()
        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        root_tag_name = (getattr(data, "xml_tag", None) or self.root_tag_name)
        self._to_xml(xml, data, root_tag_name)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data, tag_name=None):

        if tag_name:
            xml.startElement(tag_name, {})

        if hasattr(data, 'write_xml'):
            # Support for the `IWriteXML` protocol.
            data.write_xml(xml)
        elif data is True:
            xml.characters('true')
        elif data is False:
            xml.characters('false')
        elif isinstance(data, (list, tuple)):
            for item in data:
                self._to_xml(xml, item, tag_name=(getattr(data, "xml_tag", None) or self.item_tag_name))
        elif isinstance(data, dict):
            key_order = getattr(data, "key_order", ())
            for key in sorted(data.keys(), key=order_by_sort_order(key_order)):
                self._to_xml(xml, data[key], key)
        elif data is None:  # Don't output any value
            pass
        else:
            xml.characters(smart_text(data))

        if tag_name:
            xml.endElement(tag_name)


class SparkJSONRenderer(JSONRenderer):
    format = 'sjson'  # Short for sparkjson
    ensure_ascii = False
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        xml = XMLRenderer().render(
            data,
            accepted_media_type=XMLRenderer.media_type,
            renderer_context=renderer_context
        )
        return transform_xml_to_json(xml)
