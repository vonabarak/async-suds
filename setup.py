#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import setuptools
from asyncsuds.version import __version__


long_description = """
Lightweight SOAP client (Kamyar's fork).
=======================================

  Based on the original 'suds' project by Jeff Ortel (jortel at redhat
dot com) hosted at 'http://fedorahosted.org/suds'.

  'Suds' is a lightweight SOAP-based web service client for Python
licensed under LGPL (see the LICENSE.txt file included in the
distribution).

  This is hopefully just a temporary fork of the original suds Python
library project created because the original project development seems
to have stalled. Should be reintegrated back into the original project
if it ever gets revived again.

"""


def safe_version(version_string):
    """
    Convert an arbitrary string to a standard version string

    Spaces become dots, and all other non-alphanumeric characters become
    dashes, with runs of multiple dashes condensed to a single dash.

    """
    version_string = version_string.replace(" ", ".")
    return re.sub("[^A-Za-z0-9.]+", "-", version_string)


def unicode2ascii(unicode):
    """Convert a unicode string to its approximate ASCII equivalent."""
    return unicode.encode("ascii", "xmlcharrefreplace").decode("ascii")


package_name = "async-suds-v7k"
version_tag = safe_version(__version__)
project_url = "https://github.com/vonabarak/async-suds"
base_download_url = project_url + "/downloads"
download_distribution_name = "%s-%s.tar.bz2" % (package_name, version_tag)
download_url = "%s/%s" % (base_download_url, download_distribution_name)

setuptools.setup(
    name=package_name,
    version=__version__,
    description="Lightweight async SOAP client (Kamyar's fork)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["SOAP", "web", "service", "client"],
    url=project_url,
    download_url=download_url,
    packages=setuptools.find_packages(),
    author="Jeff Ortel",
    author_email="jortel@redhat.com",
    maintainer="vonabarak",
    maintainer_email="github@vonabarak.ru",
    # See PEP-301 for the classifier specification. For a complete list of
    # available classifiers see
    # 'http://pypi.python.org/pypi?%3Aaction=list_classifiers'.
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: "
        "GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet",
    ],
    # PEP-314 states that, if possible, license & platform should be specified
    # using 'classifiers'.
    license="(specified using classifiers)",
    platforms=["(specified using classifiers)"],
    install_requires=["aiohttp"],
    python_requires='>=3.7',
)
