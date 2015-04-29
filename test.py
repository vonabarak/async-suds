__author__ = 'kamyar'

import asyncio
from suds.client import Client


# @asyncio.coroutine
# def Test():
c=Client('https://sep.shaparak.ir/Payments/InitPayment.asmx?wsdl')


# asyncio.get_event_loop().run_until_complete(Test())