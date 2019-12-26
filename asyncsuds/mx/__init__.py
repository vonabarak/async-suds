"""
Provides modules containing classes to support marshalling to XML.

"""

from asyncsuds.sudsobject import Object


class Content(Object):
    """
    Marshaller content.

    @ivar tag: The content tag.
    @type tag: str
    @ivar value: The content's value.
    @type value: I{any}

    """

    extensions = []

    def __init__(self, tag=None, value=None, **kwargs):
        """
        @param tag: The content tag.
        @type tag: str
        @param value: The content's value.
        @type value: I{any}

        """
        Object.__init__(self)
        self.tag = tag
        self.value = value
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            pass
        if name in self.extensions:
            value = None
            setattr(self, name, value)
            return value
        raise AttributeError("Content has no attribute %s" % (name,))
