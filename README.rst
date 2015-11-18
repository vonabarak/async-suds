SOAP 1 and 1.1 client base on asyncio (PEP3156)
===============================================

This package is a fork pg great old package suds, but we had to make a bit change to be able to make the whole tyihng async: You have to call an extar method cvalled connect, since we can not yield (or await) constructur.

.. code-block:: python

	from asyncsuds.client import Client
	
	c = Client(service_uri)
	await c.connect()  # Here is the difference!
	result = c.HelloWorld('Kamyar')
	
Please help me with your opinions and bug/feature reports.