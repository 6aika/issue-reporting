from rest_framework_xml.renderers import XMLRenderer


class SmartXMLRenderer(XMLRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = (renderer_context.get("view") if renderer_context else None)
        self.item_tag_name = getattr(view, "item_tag_name", self.item_tag_name)
        self.root_tag_name = getattr(view, "root_tag_name", self.root_tag_name)
        return super().render(data, accepted_media_type, renderer_context)

    def _to_xml(self, xml, data):
        if data is True:
            return xml.characters('true')
        if data is False:
            return xml.characters('false')
        return super()._to_xml(xml, data)

