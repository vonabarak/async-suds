"""
Classes for the (WS) SOAP I{rpc/literal} and I{rpc/encoded} bindings.

"""

from asyncsuds.bindings.binding import Binding
from asyncsuds.bindings.binding import envns
from asyncsuds.mx.encoded import Encoded as MxEncoded
from asyncsuds.sax.element import Element
from asyncsuds.umx.encoded import Encoded as UmxEncoded

encns = ("SOAP-ENC", "http://schemas.xmlsoap.org/soap/encoding/")


class RPC(Binding):
    """RPC/Literal binding style."""

    def param_defs(self, method):
        return self.bodypart_types(method)

    def envelope(self, header, body):
        env = super(RPC, self).envelope(header, body)
        env.addPrefix(encns[0], encns[1])
        env.set("%s:encodingStyle" % (envns[0],), encns[1])
        return env

    def bodycontent(self, method, args, kwargs):
        n = 0
        root = self.method(method)
        for pd in self.param_defs(method):
            if n < len(args):
                value = args[n]
            else:
                value = kwargs.get(pd[0])
            p = self.mkparam(method, pd, value)
            if p is not None:
                root.append(p)
            n += 1
        return root

    def replycontent(self, method, body):
        return body[0].children

    def method(self, method):
        """
        Get the document root. For I{rpc/(literal|encoded)}, this is the name
        of the method qualified by the schema tns.

        @param method: A service method.
        @type method: I{service.Method}
        @return: A root element.
        @rtype: L{Element}

        """
        ns = method.soap.input.body.namespace
        if ns[0] is None:
            ns = ("ns0", ns[1])
        return Element(method.name, ns=ns)


class Encoded(RPC):
    """RPC/Encoded (section 5) binding style."""

    def marshaller(self):
        return MxEncoded(self.schema())

    def unmarshaller(self):
        """
        Get the appropriate schema based XML decoder.

        @return: Typed unmarshaller.
        @rtype: L{UmxTyped}

        """
        return UmxEncoded(self.schema())
