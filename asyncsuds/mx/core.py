"""
Provides I{marshaller} core classes.
"""

from logging import getLogger

from asyncsuds.mx.appender import ContentAppender
from asyncsuds.sax.document import Document
from asyncsuds.sax.element import Element
from asyncsuds.sudsobject import Property

log = getLogger(__name__)


class Core:
    """
    An I{abstract} marshaller.  This class implement the core
    functionality of the marshaller.
    @ivar appender: A content appender.
    @type appender: L{ContentAppender}
    """

    def __init__(self):
        """
        """
        self.appender = ContentAppender(self)

    def process(self, content):
        """
        Process (marshal) the tag with the specified value using the
        optional type information.
        @param content: The content to process.
        @type content: L{Object}
        """
        log.debug("processing:\n%s", content)
        self.reset()
        if content.tag is None:
            content.tag = content.value.__class__.__name__
        document = Document()
        if isinstance(content.value, Property):
            self.node(content)
        self.append(document, content)
        return document.root()

    def append(self, parent, content):
        """
        Append the specified L{content} to the I{parent}.
        @param parent: The parent node to append to.
        @type parent: L{Element}
        @param content: The content to append.
        @type content: L{Object}
        """
        log.debug("appending parent:\n%s\ncontent:\n%s", parent, content)
        if self.start(content):
            self.appender.append(parent, content)
            self.end(parent, content)

    def reset(self):
        """
        Reset the marshaller.
        """

    def node(self, content):
        """
        Create and return an XML node.
        @param content: The content for which processing has been suspended.
        @type content: L{Object}
        @return: An element.
        @rtype: L{Element}
        """
        return Element(content.tag)

    def start(self, content):
        """
        Appending this content has started.
        @param content: The content for which processing has started.
        @type content: L{Content}
        @return: True to continue appending
        @rtype: boolean
        """
        return True

    def suspend(self, content):
        """
        Appending this content has suspended.
        @param content: The content for which processing has been suspended.
        @type content: L{Content}
        """

    def resume(self, content):
        """
        Appending this content has resumed.
        @param content: The content for which processing has been resumed.
        @type content: L{Content}
        """

    def end(self, parent, content):
        """
        Appending this content has ended.
        @param parent: The parent node ending.
        @type parent: L{Element}
        @param content: The content for which processing has ended.
        @type content: L{Content}
        """

    def setnil(self, node, content):
        """
        Set the value of the I{node} to nill.
        @param node: A I{nil} node.
        @type node: L{Element}
        @param content: The content to set nil.
        @type content: L{Content}
        """

    def setdefault(self, node, content):
        """
        Set the value of the I{node} to a default value.
        @param node: A I{nil} node.
        @type node: L{Element}
        @param content: The content to set the default value.
        @type content: L{Content}
        @return: The default.
        """

    def optional(self, content):
        """
        Get whether the specified content is optional.
        @param content: The content which to check.
        @type content: L{Content}
        """
        return False
