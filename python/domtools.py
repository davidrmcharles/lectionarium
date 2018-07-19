#!/usr/bin/env python
'''
Let's fix DOM
'''

def text(node):
    '''
    Return the text content of a `node`
    '''

    return node.childNodes[0].nodeValue

def firstChild(parent_node, localName):
    '''
    Return the first child of `parent_node` having `localName`.
    '''

    for child_node in parent_node.childNodes:
        if child_node.localName == localName:
            return child_node
    return None

def children(parent_node, localNames):
    '''
    Return all children of `parent_node` having a localName in
    `localNames`.
    '''

    if isinstance(localNames, basestring):
        localNames = [localNames]

    result_nodes = []
    for child_node in parent_node.childNodes:
        if child_node.localName in localNames:
            result_nodes.append(child_node)
    return result_nodes

class RaiseIfAttrIsMissing(object):
    '''
    The intent to raise an exception if an attribute is
    missing
    '''

    pass

class MissingAttrException(Exception):
    '''
    An attribute was missing, but unexpected
    '''

    pass

def attr(node, localName, ifMissing=RaiseIfAttrIsMissing):
    '''
    Return the value of the attribute of `node` having `localName`.
    '''

    if not node.hasAttribute(localName):
        if ifMissing is RaiseIfAttrIsMissing:
            raise MissingAttrException()
        else:
            return ifMissing
    return node.getAttribute(localName)
