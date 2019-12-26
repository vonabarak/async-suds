"""
Classes providing a (D)ocument (O)bject (M)odel representation of an XML
document.

The goal is to provide an easy, intuitive interface for managing XML documents.
Although the term DOM is used above, this model is B{far} better.

XML namespaces in suds are represented using a (2) element tuple containing the
prefix and the URI, e.g. I{('tns', 'http://myns')}.

"""

from io import StringIO
from xml.sax import ContentHandler
from xml.sax import InputSource
from xml.sax import make_parser
from xml.sax.handler import feature_external_ges

import asyncsuds
from asyncsuds.sax.attribute import Attribute
from asyncsuds.sax.document import Document
from asyncsuds.sax.element import Element
from asyncsuds.sax.text import Text


class Handler(ContentHandler):
    """SAX handler."""

    def __init__(self):
        self.nodes = [Document()]

    def startElement(self, name, attrs):
        top = self.top()
        node = Element(str(name))
        for a in attrs.getNames():
            n = str(a)
            v = str(attrs.getValue(a))
            attribute = Attribute(n, v)
            if self.mapPrefix(node, attribute):
                continue
            node.append(attribute)
        node.charbuffer = []
        top.append(node)
        self.push(node)

    def mapPrefix(self, node, attribute):
        if attribute.name == "xmlns":
            if len(attribute.value):
                node.expns = str(attribute.value)
            return True
        if attribute.prefix == "xmlns":
            prefix = attribute.name
            node.nsprefixes[prefix] = str(attribute.value)
            return True
        return False

    def endElement(self, name):
        name = str(name)
        current = self.pop()
        if name != current.qname():
            raise Exception("malformed document")
        if current.charbuffer:
            current.text = Text(u"".join(current.charbuffer))
        del current.charbuffer
        if current:
            current.trim()

    def characters(self, content):
        text = str(content)
        node = self.top()
        node.charbuffer.append(text)

    def push(self, node):
        self.nodes.append(node)
        return node

    def pop(self):
        return self.nodes.pop()

    def top(self):
        return self.nodes[-1]


class Parser:
    """SAX parser."""

    @classmethod
    def saxparser(cls):
        p = make_parser()
        p.setFeature(feature_external_ges, 0)
        h = Handler()
        p.setContentHandler(h)
        return p, h

    def parse(self, file=None, string=None):
        """
        SAX parse XML text.

        @param file: Parse a python I{file-like} object.
        @type file: I{file-like} object
        @param string: Parse string XML.
        @type string: str
        @return: Parsed XML document.
        @rtype: L{Document}

        """
        if file is None and string is None:
            return
        timer = asyncsuds.metrics.Timer()
        timer.start()
        source = file
        if file is None:
            source = InputSource(None)
            source.setByteStream(StringIO(string))
        sax, handler = self.saxparser()
        sax.parse(source)
        timer.stop()
        if file is None:
            asyncsuds.metrics.log.debug("%s\nsax duration: %s", string, timer)
        else:
            asyncsuds.metrics.log.debug("sax (%s) duration: %s", file, timer)
        return handler.nodes[0]
