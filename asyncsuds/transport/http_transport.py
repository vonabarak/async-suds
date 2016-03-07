# This program is free software; you can redistribute it and/or modify it under
# the terms of the (LGPL) GNU Lesser General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Library Lesser General Public License
# for more details at ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )

"""
Basic HTTP transport implementation classes.

"""

from asyncsuds.properties import Unskin
from asyncsuds.transport import *

import base64
from http.cookiejar import CookieJar
import sys
import asyncio
from aiohttp.client import request as async_request
import aiohttp

from logging import getLogger
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
        log.debug('sending:\n%s', request)
        if request.proxy:
            connector = aiohttp.ProxyConnector(proxy=request.proxy,verify_ssl=request.verify_ssl)
        else:
            connector = aiohttp.TCPConnector(verify_ssl=request.verify_ssl)
        client = aiohttp.ClientSession(connector=connector, cookies=dict(self.cookiejar))
        try:
            res = yield from client.get(request.url, headers=headers)
            reply = yield from res.content.read()
            res.close()
            log.debug('received:\n%s', reply)
            return str(reply, encoding='utf-8')
        finally:
            client.close()
            connector.close()


    @asyncio.coroutine
    def send(self, request):
        msg = request.message
        headers = request.headers
        log.debug('sending:\n%s', request)
        if request.proxy:
            connector = aiohttp.ProxyConnector(proxy=request.proxy,verify_ssl=request.verify_ssl)
        else:
            connector = aiohttp.TCPConnector(verify_ssl=request.verify_ssl)
        client = aiohttp.ClientSession(connector=connector, cookies=dict(self.cookiejar))
        try:
            res = yield from client.post(request.url, data=msg, headers=headers)
            reply = yield from res.content.read()
            res.close()
            log.debug('received:\n%s', reply)
            return str(reply, encoding='utf-8')
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
            credentials = ':'.join(credentials)
            if sys.version_info < (3, 0):
                encodedString = base64.b64encode(credentials)
            else:
                encodedBytes = base64.urlsafe_b64encode(credentials.encode())
                encodedString = encodedBytes.decode()
            request.headers['Authorization'] = 'Basic %s' % encodedString

    def credentials(self):
        return self.options.username, self.options.password
