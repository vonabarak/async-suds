"""
The plugin module provides suds plugin implementation classes.

"""

from logging import getLogger

log = getLogger(__name__)


class Context(object):
    """Plugin context."""


class InitContext(Context):
    """
    Init Context.

    @ivar wsdl: The WSDL.
    @type wsdl: L{wsdl.Definitions}

    """


class DocumentContext(Context):
    """
    The XML document load context.

    @ivar url: The URL.
    @type url: str
    @ivar document: Either the XML text or the B{parsed} document root.
    @type document: (str|L{sax.element.Element})

    """


class MessageContext(Context):
    """
    The context for sending the SOAP envelope.

    @ivar envelope: The SOAP envelope to be sent.
    @type envelope: (str|L{sax.element.Element})
    @ivar reply: The reply.
    @type reply: (str|L{sax.element.Element}|object)

    """


class Plugin:
    """Plugin base."""


class InitPlugin(Plugin):
    """Base class for all suds I{init} plugins."""

    def initialized(self, context):
        """
        Suds client initialization.

        Called after WSDL the has been loaded. Provides the plugin with the
        opportunity to inspect/modify the WSDL.

        @param context: The init context.
        @type context: L{InitContext}

        """


class DocumentPlugin(Plugin):
    """Base class for suds I{document} plugins."""

    def loaded(self, context):
        """
        Suds has loaded a WSDL/XSD document.

        Provides the plugin with an opportunity to inspect/modify the unparsed
        document. Called after each WSDL/XSD document is loaded.

        @param context: The document context.
        @type context: L{DocumentContext}

        """

    def parsed(self, context):
        """
        Suds has parsed a WSDL/XSD document.

        Provides the plugin with an opportunity to inspect/modify the parsed
        document. Called after each WSDL/XSD document is parsed.

        @param context: The document context.
        @type context: L{DocumentContext}

        """


class MessagePlugin(Plugin):
    """Base class for suds I{SOAP message} plugins."""

    def marshalled(self, context):
        """
        Suds is about to send the specified SOAP envelope.

        Provides the plugin with the opportunity to inspect/modify the envelope
        Document before it is sent.

        @param context: The send context.
            The I{envelope} is the envelope document.
        @type context: L{MessageContext}

        """

    def sending(self, context):
        """
        Suds is about to send the specified SOAP envelope.

        Provides the plugin with the opportunity to inspect/modify the message
        text before it is sent.

        @param context: The send context.
            The I{envelope} is the envelope text.
        @type context: L{MessageContext}

        """

    def received(self, context):
        """
        Suds has received the specified reply.

        Provides the plugin with the opportunity to inspect/modify the received
        XML text before it is SAX parsed.

        @param context: The reply context.
            The I{reply} is the raw text.
        @type context: L{MessageContext}

        """

    def parsed(self, context):
        """
        Suds has SAX parsed the received reply.

        Provides the plugin with the opportunity to inspect/modify the SAX
        parsed DOM tree for the reply before it is unmarshalled.

        @param context: The reply context.
            The I{reply} is DOM tree.
        @type context: L{MessageContext}

        """

    def unmarshalled(self, context):
        """
        Suds has unmarshalled the received reply.

        Provides the plugin with the opportunity to inspect/modify the
        unmarshalled reply object before it is returned.

        @param context: The reply context.
            The I{reply} is unmarshalled suds object.
        @type context: L{MessageContext}

        """


class PluginContainer:
    """
    Plugin container provides easy method invocation.

    @ivar plugins: A list of plugin objects.
    @type plugins: [L{Plugin},]
    @cvar ctxclass: A dict of plugin method / context classes.
    @type ctxclass: dict

    """

    domains = {
        "init": (InitContext, InitPlugin),
        "document": (DocumentContext, DocumentPlugin),
        "message": (MessageContext, MessagePlugin),
    }

    def __init__(self, plugins):
        """
        @param plugins: A list of plugin objects.
        @type plugins: [L{Plugin},]

        """
        self.plugins = plugins

    def __getattr__(self, name):
        domain = self.domains.get(name)
        if not domain:
            raise Exception("plugin domain (%s), invalid" % (name,))
        ctx, pclass = domain
        plugins = [p for p in self.plugins if isinstance(p, pclass)]
        return PluginDomain(ctx, plugins)


class PluginDomain:
    """
    The plugin domain.

    @ivar ctx: A context.
    @type ctx: L{Context}
    @ivar plugins: A list of plugins (targets).
    @type plugins: list

    """

    def __init__(self, ctx, plugins):
        self.ctx = ctx
        self.plugins = plugins

    def __getattr__(self, name):
        return Method(name, self)


class Method:
    """
    Plugin method.

    @ivar name: The method name.
    @type name: str
    @ivar domain: The plugin domain.
    @type domain: L{PluginDomain}

    """

    def __init__(self, name, domain):
        """
        @param name: The method name.
        @type name: str
        @param domain: A plugin domain.
        @type domain: L{PluginDomain}

        """
        self.name = name
        self.domain = domain

    def __call__(self, **kwargs):
        ctx = self.domain.ctx()
        ctx.__dict__.update(kwargs)
        for plugin in self.domain.plugins:
            method = getattr(plugin, self.name, None)
            if method and callable(method):
                method(ctx)
        return ctx
