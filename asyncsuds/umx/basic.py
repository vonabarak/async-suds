"""
Provides basic unmarshaller classes.
"""


from asyncsuds import *
from asyncsuds.umx import *
from asyncsuds.umx.core import Core


class Basic(Core):
    """
    A object builder (unmarshaller).
    """

    def process(self, node):
        """
        Process an object graph representation of the xml I{node}.
        @param node: An XML tree.
        @type node: L{sax.element.Element}
        @return: A suds object.
        @rtype: L{Object}
        """
        content = Content(node)
        return Core.process(self, content)
