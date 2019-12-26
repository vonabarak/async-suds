"""
Lightweight SOAP Python client providing a Web Service proxy.

"""


#
# Project properties
#


#
# Exceptions
#


class MethodNotFound(Exception):
    def __init__(self, name):
        Exception.__init__(self, u"Method not found: '%s'" % (name,))


class PortNotFound(Exception):
    def __init__(self, name):
        Exception.__init__(self, u"Port not found: '%s'" % (name,))


class ServiceNotFound(Exception):
    def __init__(self, name):
        Exception.__init__(self, u"Service not found: '%s'" % (name,))


class TypeNotFound(Exception):
    def __init__(self, name):
        Exception.__init__(self, u"Type not found: '%s'" % (tostr(name),))


class BuildError(Exception):
    def __init__(self, name, exception):
        Exception.__init__(
            self,
            u"An error occurred while building an "
            "instance of (%s). As a result the object you requested could not "
            "be constructed. It is recommended that you construct the type "
            "manually using a Suds object. Please open a ticket with a "
            "description of this error. Reason: %s" % (name, exception),
        )


class WebFault(Exception):
    def __init__(self, fault, document):
        if hasattr(fault, "faultstring"):
            Exception.__init__(
                self, u"Server raised fault: '%s'" % (fault.faultstring,)
            )
        self.fault = fault
        self.document = document


#
# Logging
#


class Repr:
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return repr(self.x)


#
# Utility
#


class null:
    """I{null} object used to pass NULL for optional XML nodes."""


def objid(obj):
    return obj.__class__.__name__ + ":" + hex(id(obj))


def tostr(object, encoding=None):
    """Get a unicode safe string representation of an object."""
    if isinstance(object, str):
        if encoding is None:
            return object
        return object.encode(encoding)
    if isinstance(object, tuple):
        s = ["("]
        for item in object:
            s.append(tostr(item))
            s.append(", ")
        s.append(")")
        return "".join(s)
    if isinstance(object, list):
        s = ["["]
        for item in object:
            s.append(tostr(item))
            s.append(", ")
        s.append("]")
        return "".join(s)
    if isinstance(object, dict):
        s = ["{"]
        for item in object.items():
            s.append(tostr(item[0]))
            s.append(" = ")
            s.append(tostr(item[1]))
            s.append(", ")
        s.append("}")
        return "".join(s)
    try:
        return str(object)
    except Exception:
        return str(object)


#
# Python 3 compatibility
#


# Used instead of byte literals as they are not supported on Python versions
# prior to 2.6.
def byte_str(s="", encoding="utf-8", input_encoding="utf-8", errors="strict"):
    """
    Returns a byte string version of 's', encoded as specified in 'encoding'.

    Accepts str & unicode objects, interpreting non-unicode strings as byte
    strings encoded using the given input encoding.

    """
    assert isinstance(s, str)
    if isinstance(s, str):
        return s.encode(encoding, errors)
    if s and encoding != input_encoding:
        return s.decode(input_encoding, errors).encode(encoding, errors)
    return s


# Class used to represent a byte string. Useful for asserting that correct
# string types are being passed around where needed.

byte_str_class = bytes
