"""
Provides modules containing classes to support
unmarshalling (XML).
"""

from asyncsuds.sudsobject import Object


class Content(Object):
    """
    @ivar node: The content source node.
    @type node: L{sax.element.Element}
    @ivar data: The (optional) content data.
    @type data: L{Object}
    @ivar text: The (optional) content (xml) text.
    @type text: basestring
    """

    extensions = []

    def __init__(self, node, **kwargs):
        Object.__init__(self)
        self.node = node
        self.data = None
        self.text = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        if name not in self.__dict__:
            if name in self.extensions:
                v = None
                setattr(self, name, v)
            else:
                raise AttributeError("Content has no attribute %s" % name)
        else:
            v = self.__dict__[name]
        return v
