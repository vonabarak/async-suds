"""
Provides soap encoded unmarshaller classes.
"""

from asyncsuds import *
from asyncsuds.sax import Namespace
from asyncsuds.umx import *
from asyncsuds.umx.typed import Typed

#
# Add encoded extensions
# aty = The soap (section 5) encoded array type.
#
Content.extensions.append("aty")


class Encoded(Typed):
    """
    A SOAP section (5) encoding unmarshaller.
    This marshaller supports rpc/encoded soap styles.
    """

    def start(self, content):
        #
        # Grab the array type and continue
        #
        self.setaty(content)
        Typed.start(self, content)

    def end(self, content):
        #
        # Squash soap encoded arrays into python lists.  This is
        # also where we insure that empty arrays are represented
        # as empty python lists.
        #
        aty = content.aty
        if aty is not None:
            self.promote(content)
        return Typed.end(self, content)

    def postprocess(self, content):
        #
        # Ensure proper rendering of empty arrays.
        #
        if content.aty is None:
            return Typed.postprocess(self, content)
        else:
            return content.data

    def setaty(self, content):
        """
        Grab the (aty) soap-enc:arrayType and attach it to the
        content for proper array processing later in end().
        @param content: The current content being unmarshalled.
        @type content: L{Content}
        @return: self
        @rtype: L{Encoded}
        """
        name = "arrayType"
        ns = (None, "http://schemas.xmlsoap.org/soap/encoding/")
        aty = content.node.get(name, ns)
        if aty is not None:
            content.aty = aty
            parts = aty.split("[")
            ref = parts[0]
            if len(parts) == 2:
                self.applyaty(content, ref)
            else:
                pass  # (2) dimensional array
        return self

    def applyaty(self, content, xty):
        """
        Apply the type referenced in the I{arrayType} to the content
        (child nodes) of the array.  Each element (node) in the array
        that does not have an explicit xsi:type attribute is given one
        based on the I{arrayType}.
        @param content: An array content.
        @type content: L{Content}
        @param xty: The XSI type reference.
        @type xty: str
        @return: self
        @rtype: L{Encoded}
        """
        name = "type"
        ns = Namespace.xsins
        parent = content.node
        for child in parent.getChildren():
            ref = child.get(name, ns)
            if ref is None:
                parent.addPrefix(ns[0], ns[1])
                attr = ":".join((ns[0], name))
                child.set(attr, xty)
        return self

    def promote(self, content):
        """
        Promote (replace) the content.data with the first attribute
        of the current content.data that is a I{list}.  Note: the
        content.data may be empty or contain only _x attributes.
        In either case, the content.data is assigned an empty list.
        @param content: An array content.
        @type content: L{Content}
        """
        for n, v in content.data:
            if isinstance(v, list):
                content.data = v
                return
        content.data = []
