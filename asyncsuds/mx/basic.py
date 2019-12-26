"""
Provides basic I{marshaller} classes.
"""

from asyncsuds import *
from asyncsuds.mx import *
from asyncsuds.mx.core import Core


class Basic(Core):
    """
    A I{basic} (untyped) marshaller.
    """

    def process(self, value, tag=None):
        """
        Process (marshal) the tag with the specified value using the
        optional type information.
        @param value: The value (content) of the XML node.
        @type value: (L{Object}|any)
        @param tag: The (optional) tag name for the value.  The default is
            value.__class__.__name__
        @type tag: str
        @return: An xml node.
        @rtype: L{Element}
        """
        content = Content(tag=tag, value=value)
        result = Core.process(self, content)
        return result
