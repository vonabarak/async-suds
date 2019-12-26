"""
Provides encoded I{marshaller} classes.
"""

from asyncsuds import *
from asyncsuds.mx import *
from asyncsuds.mx.literal import Literal
from asyncsuds.mx.typer import Typer
from asyncsuds.sudsobject import Factory
from asyncsuds.sudsobject import Object
from asyncsuds.xsd.query import TypeQuery

#
# Add encoded extensions
# aty = The soap (section 5) encoded array type.
#
Content.extensions.append("aty")


class Encoded(Literal):
    """
    A SOAP section (5) encoding marshaller.
    This marshaller supports rpc/encoded soap styles.
    """

    def start(self, content):
        #
        # For soap encoded arrays, the 'aty' (array type) information
        # is extracted and added to the 'content'.  Then, the content.value
        # is replaced with an object containing an 'item=[]' attribute
        # containing values that are 'typed' suds objects.
        #
        start = Literal.start(self, content)
        if start and isinstance(content.value, (list, tuple)):
            resolved = content.type.resolve()
            for c in resolved:
                if hasattr(c[0], "aty"):
                    content.aty = (content.tag, c[0].aty)
                    self.cast(content)
                    break
        return start

    def end(self, parent, content):
        #
        # For soap encoded arrays, the soapenc:arrayType attribute is
        # added with proper type and size information.
        # Eg: soapenc:arrayType="xs:int[3]"
        #
        Literal.end(self, parent, content)
        if content.aty is None:
            return
        tag, aty = content.aty
        ns0 = ("at0", aty[1])
        ns1 = ("at1", "http://schemas.xmlsoap.org/soap/encoding/")
        array = content.value.item
        child = parent.getChild(tag)
        child.addPrefix(ns0[0], ns0[1])
        child.addPrefix(ns1[0], ns1[1])
        name = "%s:arrayType" % ns1[0]
        value = "%s:%s[%d]" % (ns0[0], aty[0], len(array))
        child.set(name, value)

    def encode(self, node, content):
        if content.type.any():
            Typer.auto(node, content.value)
            return
        if content.real.any():
            Typer.auto(node, content.value)
            return
        ns = None
        name = content.real.name
        if self.xstq:
            ns = content.real.namespace()
        Typer.manual(node, name, ns)

    def cast(self, content):
        """
        Cast the I{untyped} list items found in content I{value}.
        Each items contained in the list is checked for XSD type information.
        Items (values) that are I{untyped}, are replaced with suds objects and
        type I{metadata} is added.
        @param content: The content holding the collection.
        @type content: L{Content}
        @return: self
        @rtype: L{Encoded}
        """
        aty = content.aty[1]
        resolved = content.type.resolve()
        array = Factory.object(resolved.name)
        array.item = []
        query = TypeQuery(aty)
        ref = query.execute(self.schema)
        if ref is None:
            raise TypeNotFound(ref)
        for x in content.value:
            if isinstance(x, (list, tuple)):
                array.item.append(x)
                continue
            if isinstance(x, Object):
                md = x.__metadata__
                md.sxtype = ref
                array.item.append(x)
                continue
            if isinstance(x, dict):
                x = Factory.object(ref.name, x)
                md = x.__metadata__
                md.sxtype = ref
                array.item.append(x)
                continue
            x = Factory.property(ref.name, x)
            md = x.__metadata__
            md.sxtype = ref
            array.item.append(x)
        content.value = array
        return self
