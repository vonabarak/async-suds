from asyncsuds.sax import Namespace
from asyncsuds.sax import splitPrefix


def qualify(ref, resolvers, defns=Namespace.default):
    """
    Get a reference that is I{qualified} by namespace.
    @param ref: A referenced schema type name.
    @type ref: str
    @param resolvers: A list of objects to be used to resolve types.
    @type resolvers: [L{sax.element.Element},]
    @param defns: An optional target namespace used to qualify references
        when no prefix is specified.
    @type defns: A default namespace I{tuple: (prefix,uri)} used when ref not prefixed.
    @return: A qualified reference.
    @rtype: (name, namespace-uri)
    """
    ns = None
    p, n = splitPrefix(ref)
    if p is not None:
        if not isinstance(resolvers, (list, tuple)):
            resolvers = (resolvers,)
        for r in resolvers:
            resolved = r.resolvePrefix(p)
            if resolved[1] is not None:
                ns = resolved
                break
        if ns is None:
            raise Exception("prefix (%s) not resolved" % p)
    else:
        ns = defns
    return (n, ns[1])


def isqref(object):
    """
    Get whether the object is a I{qualified reference}.
    @param object: An object to be tested.
    @type object: I{any}
    @rtype: boolean
    @see: L{qualify}
    """
    return (
        isinstance(object, tuple)
        and len(object) == 2
        and isinstance(object[0], str)
        and isinstance(object[1], str)
    )


class Filter:
    def __init__(self, inclusive=False, *items):
        self.inclusive = inclusive
        self.items = items

    def __contains__(self, x):
        if self.inclusive:
            result = x in self.items
        else:
            result = x not in self.items
        return result
