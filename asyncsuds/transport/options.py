"""
Classes modeling transport options.

"""


from asyncsuds.properties import *
from asyncsuds.transport import *


class Options(Skin):
    """
    Options:
        - B{proxy} - An HTTP proxy to be specified on requests, defined as
            {protocol:proxy, ...}.
                - type: I{dict}
                - default: {}
        - B{timeout} - Set the URL open timeout (seconds).
                - type: I{float}
                - default: 90
        - B{headers} - Extra HTTP headers.
                - type: I{dict}
                    - I{str} B{http} - The I{HTTP} protocol proxy URL.
                    - I{str} B{https} - The I{HTTPS} protocol proxy URL.
                - default: {}
        - B{username} - The username used for HTTP authentication.
                - type: I{str}
                - default: None
        - B{password} - The password used for HTTP authentication.
                - type: I{str}
                - default: None

    """

    def __init__(self, **kwargs):
        domain = __name__
        definitions = [
            Definition("proxy", dict, {}),
            Definition("timeout", (int, float), 90),
            Definition("headers", dict, {}),
            Definition("username", str, None),
            Definition("password", str, None),
        ]
        Skin.__init__(self, domain, definitions, kwargs)
