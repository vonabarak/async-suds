__author__ = "kamyar"

import asyncio
import logging
import uuid

from asyncsuds.client import Client

# logging.basicConfig(level=logging.DEBUG)


@asyncio.coroutine
def Test():
    c = Client(
        "https://sep.shaparak.ir/Payments/InitPayment.asmx?wsdl",
        headers={"User-Agent": "Snapp"},
    )
    c.verify_ssl = False
    yield from c.connect()
    res = yield from c.service.RequestToken("10345926", uuid.uuid1().hex, 1000)
    print(res)


asyncio.async(Test())
asyncio.get_event_loop().run_forever()
# asyncio.get_event_loop().close()
