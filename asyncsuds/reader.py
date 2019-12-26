"""
XML document reader classes providing integration with the suds library's
caching system.

"""

import asyncio
from hashlib import md5

import asyncsuds.cache
import asyncsuds.plugin
import asyncsuds.sax.parser
import asyncsuds.transport


class Reader(object):
    """
    Provides integration with the cache.

    @ivar options: An options object.
    @type options: I{Options}

    """

    def __init__(self, options):
        """
        @param options: An options object.
        @type options: I{Options}

        """
        self.options = options
        self.plugins = asyncsuds.plugin.PluginContainer(options.plugins)
        self.headers = {}
        self.verify_ssl = True
        self.proxy = None

    def mangle(self, name, x):
        """
        Mangle the name by hashing the I{name} and appending I{x}.

        @return: The mangled name.
        @rtype: str

        """
        h = md5(name.encode()).hexdigest()
        return "%s-%s" % (h, x)


class DefinitionsReader(Reader):
    """
    Integrates between the WSDL Definitions object and the object cache.

    @ivar fn: A factory function used to create objects not found in the cache.
    @type fn: I{Constructor}

    """

    def __init__(self, options, fn):
        """
        @param options: An options object.
        @type options: I{Options}
        @param fn: A factory function used to create objects not found in the
            cache.
        @type fn: I{Constructor}

        """
        super(DefinitionsReader, self).__init__(options)
        self.fn = fn

    @asyncio.coroutine
    def open(self, url, headers=None):
        """
        Open a WSDL schema at the specified I{URL}.

        First, the WSDL schema is looked up in the I{object cache}. If not
        found, a new one constructed using the I{fn} factory function and the
        result is cached for the next open().

        @param url: A WSDL URL.
        @type url: str.
        @return: The WSDL object.
        @rtype: I{Definitions}

        """
        cache = self.__cache()
        id = self.mangle(url, "wsdl")
        wsdl = cache.get(id)
        if wsdl is None:
            wsdl = self.fn(url, self.options, headers=headers)
            wsdl.verify_ssl = self.verify_ssl
            wsdl.proxy = self.proxy
            yield from wsdl.connect()
            cache.put(id, wsdl)
        else:
            # Cached WSDL Definitions objects may have been created with
            # different options so we update them here with our current ones.
            wsdl.options = self.options
            for imp in wsdl.imports:
                imp.imported.options = self.options
        self.wsdl = wsdl
        return wsdl

    def __cache(self):
        """
        Get the I{object cache}.

        @return: The I{cache} when I{cachingpolicy} = B{1}.
        @rtype: L{Cache}

        """
        if self.options.cachingpolicy == 1:
            return self.options.cache
        return asyncsuds.cache.NoCache()


class DocumentReader(Reader):
    """Integrates between the SAX L{Parser} and the document cache."""

    @asyncio.coroutine
    def open(self, url, headers=None):
        """
        Open an XML document at the specified I{URL}.

        First, a preparsed document is looked up in the I{object cache}. If not
        found, its content is fetched from an external source and parsed using
        the SAX parser. The result is cached for the next open().

        @param url: A document URL.
        @type url: str.
        @return: The specified XML document.
        @rtype: I{Document}

        """
        cache = self.__cache()
        id = self.mangle(url, "document")
        self.headers = headers or {}
        xml = cache.get(id)
        if xml is None:
            xml = yield from self.__fetch(url)
            cache.put(id, xml)
        self.plugins.document.parsed(url=url, document=xml.root())
        return xml

    def __cache(self):
        """
        Get the I{object cache}.

        @return: The I{cache} when I{cachingpolicy} = B{0}.
        @rtype: L{Cache}

        """
        if self.options.cachingpolicy == 0:
            return self.options.cache
        return asyncsuds.cache.NoCache()

    @asyncio.coroutine
    def __fetch(self, url):
        """
        Fetch document content from an external source.

        The document content will first be looked up in the registered document
        store, and if not found there, downloaded using the registered
        transport system.

        Before being returned, the fetched document content first gets
        processed by all the registered 'loaded' plugins.

        @param url: A document URL.
        @type url: str.
        @return: A file pointer to the fetched document content.
        @rtype: file-like

        """
        content = None
        store = self.options.documentStore
        if store is not None:
            content = store.open(url)
        if content is None:
            request = asyncsuds.transport.Request(url, headers=self.headers)
            request.verify_ssl = self.verify_ssl
            request.proxy = self.proxy
            content = yield from self.options.transport.open(request)
        ctx = self.plugins.document.loaded(url=url, document=content)
        content = ctx.document
        sax = asyncsuds.sax.parser.Parser()
        return sax.parse(string=content)
