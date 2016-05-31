import json
from collections import OrderedDict

from lxml import etree
from six import text_type


def spark_node(node, in_list=False):
    """
    "Sparkify" a single XML node.

    :param node: The LXML node to sparkify
    :type node: lxml.etree.Element
    :param in_list: Internal flag; used by this fn when sparkifying a list
    :type in_list: bool
    :return: list|dict
    """
    kids = node.getchildren()
    if kids and all(c.tag == kids[0].tag for c in kids):  # Homogeneous children; this must be an array
        children = [
            node for node in [spark_node(k, in_list=True) for k in kids]
            if node is not None
        ]

        # The following has not really been specified, but it prevents some mistransforms:
        if not children:
            return {}

        if all(isinstance(j_kid, text_type) for j_kid in children):  # All of the children turned into bare strings:
            return {node.tag: children}  # Wrap them in an object
        elif all(isinstance(j_kid, dict) and len(j_kid) == 1 for j_kid in children):  # The children got turned into 1-dicts?
            n_kids = {}
            for kid in children:
                n_kids.update(kid)
            return n_kids  # Unravel them.
        else:  # Mixed bag? Return the list.
            return children

    if in_list and not kids and not node.items():
        return node.text

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
