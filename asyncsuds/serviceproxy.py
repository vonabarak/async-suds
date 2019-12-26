"""
The service proxy provides access to web services.

Replaced by: L{client.Client}
"""

from asyncsuds.client import Client


class ServiceProxy(object):

    """
    A lightweight soap based web service proxy.
    @ivar __client__: A client.
        Everything is delegated to the 2nd generation API.
    @type __client__: L{Client}
    @note:  Deprecated, replaced by L{Client}.
    """

    def __init__(self, url, **kwargs):
        """
        @param url: The URL for the WSDL.
        @type url: str
        @param kwargs: keyword arguments.
        @keyword faults: Raise faults raised by server (default:True),
                else return tuple from service method invocation as (http code, object).
        @type faults: boolean
        @keyword proxy: An http proxy to be specified on requests (default:{}).
                           The proxy is defined as {protocol:proxy,}
        @type proxy: dict
        """
        client = Client(url, **kwargs)
        self.__client__ = client

    def get_instance(self, name):
        """
        Get an instance of a WSDL type by name
        @param name: The name of a type defined in the WSDL.
        @type name: str
        @return: An instance on success, else None
        @rtype: L{sudsobject.Object}
        """
        return self.__client__.factory.create(name)

    def get_enum(self, name):
        """
        Get an instance of an enumeration defined in the WSDL by name.
        @param name: The name of a enumeration defined in the WSDL.
        @type name: str
        @return: An instance on success, else None
        @rtype: L{sudsobject.Object}
        """
        return self.__client__.factory.create(name)

    def __str__(self):
        return str(self.__client__)

    def __getattr__(self, name):
        builtin = name.startswith("__") and name.endswith("__")
        if builtin:
            return self.__dict__[name]
        else:
            return getattr(self.__client__.service, name)
