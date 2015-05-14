__author__ = 'kamyar'

import asyncio
from suds.client import Client
import logging


# logging.basicConfig(level=logging.DEBUG)

@asyncio.coroutine
def Test():
    c=Client('http://www.webservicex.net/whois.asmx?WSDL')
    yield from c.connect()
    res = yield from c.service.GetWhoIS('samasoft.ir')
    print(res)

asyncio.get_event_loop().run_until_complete(Test())
asyncio.get_event_loop().close()