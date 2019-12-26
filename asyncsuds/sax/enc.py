"""
Provides XML I{special character} encoder classes.

"""

import re


class Encoder:
    """
    An XML special character encoder/decoder.

    @cvar encodings: A mapping of special characters encoding.
    @type encodings: [(str, str),...]
    @cvar decodings: A mapping of special characters decoding.
    @type decodings: [(str, str),...]
    @cvar special: A list of special characters.
    @type special: [char,...]

    """

    encodings = (
        ("&(?!(amp|lt|gt|quot|apos);)", "&amp;"),
        ("<", "&lt;"),
        (">", "&gt;"),
        ('"', "&quot;"),
        ("'", "&apos;"),
    )
    decodings = (
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&apos;", "'"),
        ("&amp;", "&"),
    )
    special = ("&", "<", ">", '"', "'")

    def encode(self, s):
        """
        Encode special characters found in string I{s}.

        @param s: A string to encode.
        @type s: str
        @return: The encoded string.
        @rtype: str

        """
        if isinstance(s, str) and self.__needs_encoding(s):
            for x in self.encodings:
                s = re.sub(x[0], x[1], s)
        return s

    def decode(self, s):
        """
        Decode special characters encodings found in string I{s}.

        @param s: A string to decode.
        @type s: str
        @return: The decoded string.
        @rtype: str

        """
        if isinstance(s, str) and "&" in s:
            for x in self.decodings:
                s = s.replace(x[0], x[1])
        return s

    def __needs_encoding(self, s):
        """
        Get whether string I{s} contains special characters.

        @param s: A string to check.
        @type s: str
        @return: True if needs encoding.
        @rtype: boolean

        """
        if isinstance(s, str):
            for c in self.special:
                if c in s:
                    return True
