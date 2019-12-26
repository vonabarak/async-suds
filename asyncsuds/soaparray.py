"""
The I{soaparray} module provides XSD extensions for handling
soap (section 5) encoded arrays.
"""


from asyncsuds.xsd.sxbasic import Attribute as SXAttribute
from asyncsuds.xsd.sxbasic import Factory as SXFactory


class Attribute(SXAttribute):
    """
    Represents an XSD <attribute/> that handles special
    attributes that are extensions for WSDLs.
    @ivar aty: Array type information.
    @type aty: The value of wsdl:arrayType.
    """

    def __init__(self, schema, root, aty):
        """
        @param aty: Array type information.
        @type aty: The value of wsdl:arrayType.
        """
        SXAttribute.__init__(self, schema, root)
        if aty.endswith("[]"):
            self.aty = aty[:-2]
        else:
            self.aty = aty

    def autoqualified(self):
        aqs = SXAttribute.autoqualified(self)
        aqs.append("aty")
        return aqs

    def description(self):
        d = SXAttribute.description(self)
        d = d + ("aty",)
        return d


#
# Builder function, only builds Attribute when arrayType
# attribute is defined on root.
#
def __fn(x, y):
    ns = (None, "http://schemas.xmlsoap.org/wsdl/")
    aty = y.get("arrayType", ns=ns)
    if aty is None:
        return SXAttribute(x, y)
    return Attribute(x, y, aty)


#
# Remap <xs:attribute/> tags to __fn() builder.
#
SXFactory.maptag("attribute", __fn)
