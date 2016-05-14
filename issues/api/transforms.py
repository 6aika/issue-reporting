import json
from collections import OrderedDict

from lxml import etree
from six import text_type


def spark_node(node):
    """
    "Sparkify" a single XML node.

    :type node: lxml.etree.Element
    :return: list|dict
    """
    kids = node.getchildren()
    if kids and all(c.tag == kids[0].tag for c in kids):  # Homogeneous children; this must be an array
        return [spark_node(k) for k in kids]
    dct = OrderedDict()
    dct.xml_tag = node.tag

    for kid in kids:
        if kid.getchildren():
            dct[kid.tag] = spark_node(kid)
        elif kid.text:
            dct[kid.tag] = kid.text

    for attr, value in node.items():
        dct["@" + attr] = value
    return dct


def transform_xml_to_json(xml):
    """
    Transform XML to JSON according to the Spark convention.

    :param xml: XML string/bytes
    :return: JSON string
    """
    if isinstance(xml, text_type):
        xml = xml.encode("UTF-8")  # Here's hoping it's UTF-8
    xml = etree.fromstring(xml)
    dct = spark_node(xml)
    return json.dumps(dct)
