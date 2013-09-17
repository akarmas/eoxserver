#-------------------------------------------------------------------------------
# $Id$
#
# Project: EOxServer <http://eoxserver.org>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2011 EOX IT Services GmbH
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


from eoxserver.resources.coverages import models
from eoxserver.core.decoders import InvalidParameterException
from eoxserver.services.subset import Trim, Slice


def parse_bbox(string):
    try:
        return map(float, string.split(","))
    except ValueError:
        raise InvalidParameterException("Invalid BBOX parameter.", "bbox")


def parse_time(string):
    items = string.split("/")
    if len(items) == 1:
        return Slice("t", '"%s"' % items[0])
    elif len(items) == 2:
        return Trim("t", '"%s"' % items[0], '"%s"' % items[1])


def int_or_str(string):
    try:
        return int(string)
    except ValueError:
        return string


def lookup_layers(layers, subsets, suffixes=None):
    """ Performs a layer lookup for the given layer names. Applies the given 
        subsets and looks up all layers with the given suffixes. Returns a 
        hierarchy of ``LayerGroup`` objects.
    """
    suffix_related_ids = {}
    root_group = LayerGroup(None)
    suffixes = suffixes or (None,)

    for layer_name in layers:
        for suffix in suffixes:
            if not suffix:
                identifier = layer_name
            else:
                identifier = layer_name[:-len(suffix)]
            
            # TODO: nasty, nasty bug... dunno where
            eo_objects = models.EOObject.objects.filter(
                identifier=identifier
            )
            if len(eo_objects):
                eo_object = eo_objects[0]
                break
        else:
            raise InvalidParameterException(
                "No such layer %s" % layer_name, "layers"
            )

        if models.iscollection(eo_object):
            # recursively iterate over all sub-collections and collect all
            # coverages

            used_ids = suffix_related_ids.setdefault(suffix, set())

            def recursive_lookup(collection, suffix, used_ids, subsets):
                # get all EO objects related to this collection, excluding 
                # those already searched
                eo_objects = models.EOObject.objects.filter(
                    collections__in=[collection.pk]
                ).exclude(
                    pk__in=used_ids
                ).order_by("begin_time", "end_time")
                # apply subsets
                eo_objects = subsets.filter(eo_objects)

                #group = LayerGroup(collection.identifier)
                group = []

                # append all retrived EO objects, either as a coverage of 
                # the real type, or as a subgroup.
                for eo_object in eo_objects:
                    used_ids.add(eo_object.pk)

                    if models.iscoverage(eo_object):
                        group.append((eo_object.cast(), suffix))
                    elif models.iscollection(eo_object):
                        group.extend(recursive_lookup(
                            eo_object, suffix, used_ids, subsets
                        ))
                    else: 
                        raise "Type '%s' is neither a collection, nor a coverage."

                return group

            root_group.append(
                LayerGroup(eo_object.identifier,
                    recursive_lookup(eo_object, suffix, used_ids, subsets)
                )
            )

        elif models.iscoverage(eo_object):
            # TODO: suffix
            root_group.append((eo_object.cast(), suffix))

    return root_group


# TODO: rename to layer selection

class LayerGroup(list):
    def __init__(self, name, iterable=None):
        self.name = name
        if iterable:
            super(LayerGroup, self).__init__(iterable)


    def __contains__(self, eo_object):
        for item in self:
            if eo_object == item:
                return True
            try:
                if eo_object in item:
                    return True
            except TypeError:
                pass
        return False


    def walk(self, breadth_first=True):
        for item in self:
            try:
                for names, suffix, eo_object in item.walk():
                    yield (self.name,) + names, suffix, eo_object
            except AttributeError:
                yield (self.name,), item[1], item[0]

