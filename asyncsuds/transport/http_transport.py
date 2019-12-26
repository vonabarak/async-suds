"""
Basic HTTP transport implementation classes.

"""

import asyncio
import base64
import sys
from http.cookiejar import CookieJar
from logging import getLogger

import aiohttp
from asyncsuds.properties import Unskin
from asyncsuds.transport import *

log = getLogger(__name__)


class HttpTransport(Transport):
    """
    Basic HTTP transport implemented using using urllib2, that provides for
    cookies & proxies but no authentication.

    """

    def __init__(self, **kwargs):
        """
        @param kwargs: Keyword arguments.
            - B{proxy} - An HTTP proxy to be specified on requests.
                 The proxy is defined as {protocol:proxy,}
                    - type: I{dict}
                    - default: {}
            - B{timeout} - Set the URL open timeout (seconds).
                    - type: I{float}
                    - default: 90

        """
        Transport.__init__(self)
        Unskin(self.options).update(kwargs)
        self.cookiejar = CookieJar()

    @asyncio.coroutine
    def open(self, request):
        headers = request.headers
        log.debug("sending:\n%s", request)
        if request.proxy:
            connector = aiohttp.ProxyConnector(
                proxy=request.proxy, verify_ssl=request.verify_ssl
            )
        else:
            connector = aiohttp.TCPConnector(verify_ssl=request.verify_ssl)
        client = aiohttp.ClientSession(
            connector=connector, cookies=dict(self.cookiejar)
        )
        try:
            res = yield from client.get(request.url, headers=headers)
            reply = yield from res.content.read()
            res.close()
            log.debug("received:\n%s", reply)
            return str(reply, encoding="utf-8")
        finally:
            client.close()
            connector.close()

    @asyncio.coroutine
    def send(self, request):
        msg = request.message
        headers = request.headers
        log.debug("sending:\n%s", request)
        if request.proxy:
            connector = aiohttp.ProxyConnector(
                proxy=request.proxy, verify_ssl=request.verify_ssl
            )
        else:
            connector = aiohttp.TCPConnector(verify_ssl=request.verify_ssl)
        client = aiohttp.ClientSession(
            connector=connector, cookies=dict(self.cookiejar)
        )
        try:
            res = yield from client.post(request.url, data=msg, headers=headers)
            reply = yield from res.content.read()
            res.close()
            log.debug("received:\n%s", reply)
            return str(reply, encoding="utf-8")
        finally:
            client.close()
            connector.close()

    def __deepcopy__(self):
        clone = self.__class__()
        p = Unskin(self.options)
        cp = Unskin(clone.options)
        cp.update(p)
        return clone


class HttpAuthenticated(HttpTransport):
    """
    Provides basic HTTP authentication for servers that do not follow the
    specified challenge/response model. Appends the I{Authorization} HTTP
    header with base64 encoded credentials on every HTTP request.

    """

    @asyncio.coroutine
    def open(self, request):
        self.add_credentials(request)
        return HttpTransport.open(self, request)

    @asyncio.coroutine
    def send(self, request):
        self.add_credentials(request)
        return HttpTransport.send(self, request)

    def add_credentials(self, request):
        credentials = self.credentials()
        if None not in credentials:
            credentials = ":".join(credentials)
            if sys.version_info < (3, 0):
                encoded_string = base64.b64encode(credentials)
            else:
                encoded_bytes = base64.urlsafe_b64encode(credentials.encode())
                encoded_string = encoded_bytes.decode()
            request.headers["Authorization"] = "Basic %s" % encoded_string

    def credentials(self):
        return self.options.username, self.options.password
