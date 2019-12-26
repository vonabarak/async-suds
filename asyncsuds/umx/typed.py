"""
Provides typed unmarshaller classes.
"""

from logging import getLogger

from asyncsuds import *
from asyncsuds.resolver import Frame
from asyncsuds.resolver import NodeResolver
from asyncsuds.sudsobject import Factory
from asyncsuds.umx import *
from asyncsuds.umx.core import Core

log = getLogger(__name__)


#
# Add typed extensions
# type = The expected xsd type
# real = The 'true' XSD type
#
Content.extensions.append("type")
Content.extensions.append("real")


class Typed(Core):
    """
    A I{typed} XML unmarshaller
    @ivar resolver: A schema type resolver.
    @type resolver: L{NodeResolver}
    """

    def __init__(self, schema):
        """
        @param schema: A schema object.
        @type schema: L{xsd.schema.Schema}
        """
        self.resolver = NodeResolver(schema)

    def process(self, node, type):
        """
        Process an object graph representation of the xml L{node}.
        @param node: An XML tree.
        @type node: L{sax.element.Element}
        @param type: The I{optional} schema type.
        @type type: L{xsd.sxbase.SchemaObject}
        @return: A suds object.
        @rtype: L{Object}
        """
        content = Content(node)
        content.type = type
        return Core.process(self, content)

    def reset(self):
        log.debug("reset")
        self.resolver.reset()

    def start(self, content):
        #
        # Resolve to the schema type; build an object and setup metadata.
        #
        if content.type is None:
            found = self.resolver.find(content.node)
            if found is None:
                log.error(self.resolver.schema)
                raise TypeNotFound(content.node.qname())
            content.type = found
        else:
            known = self.resolver.known(content.node)
            frame = Frame(content.type, resolved=known)
            self.resolver.push(frame)
        real = self.resolver.top().resolved
        content.real = real
        cls_name = real.name
        if cls_name is None:
            cls_name = content.node.name
        content.data = Factory.object(cls_name)
        md = content.data.__metadata__
        md.sxtype = real

    def end(self, content):
        self.resolver.pop()

    def multi_occurrence(self, content):
        return content.type.multi_occurrence()

    def nillable(self, content):
        resolved = content.type.resolve()
        return content.type.nillable or (resolved.builtin() and resolved.nillable)

    def append_attribute(self, name, value, content):
        """
        Append an attribute name/value into L{Content.data}.
        @param name: The attribute name
        @type name: basestring
        @param value: The attribute's value
        @type value: basestring
        @param content: The current content being unmarshalled.
        @type content: L{Content}
        """
        type = self.resolver.findattr(name)
        if type is None:
            log.warn("attribute (%s) type, not-found", name)
        else:
            value = self.translated(value, type)
        Core.append_attribute(self, name, value, content)

    def append_text(self, content):
        """
        Append text nodes into L{Content.data}
        Here is where the I{true} type is used to translate the value
        into the proper python type.
        @param content: The current content being unmarshalled.
        @type content: L{Content}
        """
        Core.append_text(self, content)
        known = self.resolver.top().resolved
        content.text = self.translated(content.text, known)

    def translated(self, value, type):
        """ translate using the schema type """
        if value is not None:
            resolved = type.resolve()
            return resolved.translate(value)
        return value
