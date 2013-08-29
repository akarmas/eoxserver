#-------------------------------------------------------------------------------
# $Id$
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2013 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------


import re

from lxml.builder import ElementMaker

from eoxserver.core.util.xmltools import NameSpace, NameSpaceMap
from eoxserver.services.subset import Trim, Slice


# namespace declarations
ns_xlink = NameSpace("http://www.w3.org/1999/xlink", "xlink")
ns_ogc = NameSpace("http://www.opengis.net/ogc", "ogc")
ns_ows = NameSpace("http://www.opengis.net/ows/2.0", "ows")
ns_gml = NameSpace("http://www.opengis.net/gml/3.2", "gml")
ns_gmlcov = NameSpace("http://www.opengis.net/gml/3.2", "gmlcov")
ns_wcs = NameSpace("http://www.opengis.net/wcs/2.0", "wcs")
ns_crs = NameSpace("http://www.opengis.net/wcs/service-extension/crs/1.0", "crs")
ns_eowcs = NameSpace("http://www.opengis.net/wcseo/1.0", "eowcs")

# namespace map
nsmap = NameSpaceMap(
    ns_xlink, ns_ogc, ns_ows, ns_gml, ns_gmlcov, ns_wcs, ns_crs, ns_eowcs
)

# Element factories
OWS = ElementMaker(namespace=ns_ows.uri, nsmap=nsmap)
GML = ElementMaker(namespace=ns_gml.uri, nsmap=nsmap)
WCS = ElementMaker(namespace=ns_wcs.uri, nsmap=nsmap)
CRS = ElementMaker(namespace=ns_crs.uri, nsmap=nsmap)
EOWCS = ElementMaker(namespace=ns_eowcs.uri, nsmap=nsmap)

subset_re = re.compile(r'(\w+)(,([^(]+))?\(([^,]*)(,([^)]*))?\)')
size_re = re.compile(r'(\w+)\(([^)]*)\)')
resolution_re = re.compile(r'(\w+)\(([^)]*)\)')


class Size(object):
    def __init__(self, axis, value):
        self.axis = axis
        self.value = int(value)


class Resolution(object):
    def __init__(self, axis, value):
        self.axis = axis
        self.value = float(value)



class SectionsMixIn(object):
    """ Mix-in for request decoders that use sections.
    """

    def section_included(self, *sections):
        """ See if one of the sections is requested.
        """
        if not self.sections:
            return True

        requested_sections = map(lambda s: s.lower(), self.sections)

        for section in map(lambda s: s.lower(), sections):
            section = section.lower()
            if "all" in self.sections or section in requested_sections:
                return True

        return False



def parse_subset_kvp(string):
    """ Parse one subset from the WCS 2.0 KVP notation.
    """

    match = subset_re.match(string)
    if not match:
        raise

    axis = match.group(1)
    crs = match.group(3)
    
    if match.group(6) is not None:
        return Trim(axis, match.group(4), match.group(6), crs)
    else:
        return Slice(axis_label, match.group(4), crs)

def parse_size_kvp(string):
    """ 
    """

    match = size_re.match(string)
    if not match:
        raise

    return Size(match.group(1), match.group(2))


def parse_resolution_kvp(string):
    """ 
    """

    match = resolution_re.match(string)
    if not match:
        raise

    return Resolution(match.group(1), match.group(2))



def parse_subset_xml(elem):
    """ Parse one subset from the WCS 2.0 XML notation. Expects an lxml.etree
        Element as parameter.
    """

    if elem.tag == ns_wcs("DimensionTrim"):
        return Trim(
            elem.findtext(ns_wcs("Dimension")),
            elem.findtext(ns_wcs("TrimLow")),
            elem.findtext(ns_wcs("TrimHigh"))
        )
    elif elem.tag == ns_wcs("DimensionSlice"):
        return Slice()
        #TODO
