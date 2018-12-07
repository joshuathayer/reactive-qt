from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QHBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, \
    QLayout, QLineEdit
from PyQt5.QtCore import QObject
import PyQt5.QtGui
from PyQt5.QtCore import Qt
import uuid
from toolz.dicttoolz import dissoc, merge, get_in
from toolz.itertoolz import get
from functools import reduce, partial
import collections


# Recursively walk a layout, yielding each element
def walk_elems(container):
    i = 0

    for ex in range(len(container['contains'])):
        e = container['contains'][ex]

        yield e['id'], e, container['id']

        if 'contains' in e:
            yield from walk_elems(e)

def merge_dicts(acc, new_elem):
    [eid, elem, elem_container] = new_elem
    new_dict = {eid: {'element': elem,
                      'container': elem_container}}
    merged = merge(acc, new_dict)
    return merged

# Given an element, return a map of element ID to element dict for all
# elements the provided element contains, recursively (and the empty
# map if it contains no elements)
def elem_map(container):
    return reduce(merge_dicts, walk_elems(container), {})

# Determine the disposition of each element in a list of elements,
# where that list of elements are all contained together in a single
# container (parent). This function yields an ordered stream of
# commands which should be used to mutate the Qt layout. It calls
# itself recursively.
# - l0 and l1 are ordered lists of element IDs: the contained elements
#   in the container in the layout we're moving _from_ (l0) and moving
#   _to_ (l1)
# - new, rmd, and moved are sets of element IDs representing those
#   elements that are new, removed, and moved between container in the
#   overall layout
# - was_reordered is the list of elements we've found which were
#   reordered in the container- this always starts empty and is added
#   to as those elements are found during our recursion
# - container is the element ID of the container which holds all these
#   elements
def find_reordered(l0, l1, new, rmd, moved,
                   l0ix, l1ix, was_reordered, container):

    # new or moved-into?
    if len(l1) > 0 and (l1[l1ix] in new or l1[l1ix] in moved):
        if l1[l1ix] in new:
            yield ['add', l1[l1ix], l1ix, container]

        if l1[l1ix] in moved:
            yield ['reattach', l1[l1ix], l1ix, container]

        if l0ix >= len(l0) - 1 and l1ix >= len(l1) - 1:
            return

        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  l0ix,
                                  min(len(l1)-1, l1ix+1),
                                  was_reordered, container)

    # unchanged?
    elif len(l1) > 0 and (len(l0) > 0 and l0[l0ix] == l1[l1ix]):

        if l0ix >= len(l0) -1 and l1ix >= len(l1) - 1:
            return

        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  min(len(l0)-1, l0ix+1),
                                  min(len(l1)-1, l1ix+1),
                                  was_reordered, container)

    # something that was reordered? we skip over it.
    elif len(l0) > 0 and l0[l0ix] in was_reordered:

        if l0ix >= len(l0) -1 and l1ix >= len(l1) - 1:
            return

        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  min(len(l0)-1, l0ix+1),
                                  l1ix,
                                  was_reordered, container)

    # removed from layout, or moved to a different container?
    elif len(l0) > 0 and (l0[l0ix] in rmd or l0[l0ix] in moved):

        if l0[l0ix] in rmd:
            yield ['remove', l0[l0ix], container]

        if l0[l0ix] in moved:
            yield ['detach', l0[l0ix], container]

        if l0ix >= len(l0) -1 and l1ix >= len(l1) - 1:
            return

        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  min(len(l0)-1, l0ix+1),
                                  l1ix,
                                  was_reordered, container)

    # anything else means it's something that was reordered
    elif len(l0) > 0 and len(l1) > 0:

        yield ['reorder', l1[l1ix], l1ix, container]

        was_reordered.add(l1[l1ix])

        if l0ix == len(l0) -1 and l1ix == len(l1) - 1:
            return

        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  l0ix,
                                  min(len(l1)-1, l1ix+1),
                                  was_reordered, container)

# This should grow as we support new elements
def instantiate_new_elements(new_elements, element_map):
    for el in new_elements:
        e = el['element']
        comp = e['component']
        if comp == 'label':
            ob = QLabel()
            ob.setText(e['text'])
            element_map[e['id']] = ob
        elif comp == 'vbox':
            ob = QVBoxLayout()
            element_map[e['id']] = ob
        elif comp == 'hbox':
            ob = QHBoxLayout()
            element_map[e['id']] = ob
        elif comp == 'lineedit':
            ob = QLineEdit()
            element_map[e['id']] = ob
            if 'on-edit' in e:
                ob.textEdited.connect(e['on-edit'])
            ob.setText(e['text'])
        elif comp == 'pushbutton':
            ob = QPushButton()
            ob.setText(e['text'])
            element_map[e['id']] = ob
            if 'on-click' in e:
                ob.clicked.connect(e['on-click'])

    return element_map

# Interpret the stream of commands generated by find_reordered to
# mutate the layout
def take_action(action, args, all_elements):
    print("Action: {} {}".format(action, args))

    if action == 'add':
        elem, pos, container = args
        e = all_elements[elem]
        c = all_elements[container]
        if isinstance(e, QLayout):
            c.insertLayout(pos, e)
        else:
            c.insertWidget(pos, e)

    elif action == 'remove':
        elem, container = args
        e = all_elements[elem]
        c = all_elements[container]
        if isinstance(e, QLayout):
            c.removeItem(e)
        else:
            c.removeWidget(e)
        e.deleteLater()

    elif action == 'reorder':
        elem, pos, container = args
        e = all_elements[elem]
        c = all_elements[container]
        if isinstance(e, QLayout):
            c.removeItem(e)
            c.insertLayout(pos, e)
        else:
            c.removeWidget(e)
            c.insertWidget(pos, e)

    elif action == 'detach':
        elem, container = args
        e = all_elements[elem]
        c = all_elements[container]
        if isinstance(e, QLayout):
            c.removeItem(e)
        else:
            c.removeWidget(e)

    elif action == 'reattach':
        elem, pos, container = args
        e = all_elements[elem]
        c = all_elements[container]
        if isinstance(e, QLayout):
            c.insertLayout(pos, e)
        else:
            c.insertWidget(pos, e)

# Do an analysis of the two layouts, finding those elements which are
# new, which were removed, were moved, etc.
def compare_layouts(l0, l1, element_map):

    ret = collections.namedtuple('LayoutAnalysis',
                                 ['elemmap_0', 'elemmap_1'
                                  'new_elems', 'rm_elems',
                                  'changed','moved', 'reordered',
                                  'containers', 'element_map'])

    # generate maps of IDs to dicts representing widgets for _every_
    # element in a layout (recursively)
    elemmap_0 = elem_map(l0)
    elemmap_1 = elem_map(l1)

    # just the keys of those maps
    elems_0 = set(elemmap_0.keys())
    elems_1 = set(elemmap_1.keys())

    # build sets of interesting element IDs
    common = elems_0.intersection(elems_1)
    new_elems = elems_1 - elems_0
    rm_elems = elems_0 - elems_1

    # instantiate Qt objects for every new element, and place them in
    # a dict keyed by the element id
    element_map = instantiate_new_elements(
        list(map(lambda x: elemmap_1[x], new_elems)),
        element_map)

    changed = dict()
    moved = set()
    reordered = set()

    # detect those elements were retained in both layouts. for each,
    # if their contents differ (but importantly, not their `contains`
    # list), we add them to the list of changed elements If the
    # element is contained by different element, we add to the list of
    # moved elements.
    for e0, e1 in zip(map(lambda x: get(x, elemmap_0), common),
                      map(lambda x: get(x, elemmap_1), common)):

        if dissoc(e0['element'], 'contains') != \
           dissoc(e1['element'], 'contains'):
            changed[e1['element']['id']] = e1['element']

        if e0['container'] != e1['container']:
            moved.add(e0['element']['id'])

    # if any removed elements are containers, their contained elements
    # must also be removed (though if we moved an element away from a
    # container that was being removed, we don't delete it)
    for el in rm_elems:
        if 'contains' in elemmap_0[el]['element']:
            for contained in elemmap_0[el]['element']['contains']:
                if contained['id'] not in moved:
                    rm_elems.add(contained['id'])

    all_elems = merge(elemmap_0, elemmap_1)

    containers = filter(lambda x: 'contains'
                        in all_elems[x]['element'],
                        set(all_elems.keys()))

    ret.elemmap_0 = elemmap_0
    ret.elemmap_1 = elemmap_1
    ret.new_elems = new_elems
    ret.rm_elems = rm_elems
    ret.changed = changed
    ret.moved = moved
    ret.reordered = reordered
    ret.element_map = element_map
    ret.containers = containers

    return ret

# l0 is the layout we're moving _from_
# l1 is the layout we're moving _to_
# layouts are a component with an id, and (possibly) a `contains` list
def render_diff(l0, l1, element_map):
    cl  = compare_layouts(l0, l1, element_map)

    render_diff_inner(l0, l1, cl)

    for el in cl.rm_elems:
        del cl.element_map[el]

    for elid, elem in cl.changed.items():
        qelem = cl.element_map[elid]
        print("changed!", elid, elem, qelem)
        qelem.setText(elem['text'])

    return cl.element_map

def render_diff_inner(l0, l1, cl):
    comp_id = l0.get('id', l1.get('id'))

    contained_l0 = list(map(lambda x: x['id'], l0.get('contains', [])))
    contained_l1 = list(map(lambda x: x['id'], l1.get('contains', [])))

    actions = find_reordered(contained_l0,
                             contained_l1,
                             cl.new_elems, cl.rm_elems,
                             cl.moved, 0, 0, set(), comp_id)

    if actions is None:
        return

    for a in actions:
        take_action(a[0], a[1:], cl.element_map)

    em0 = {el_id: cl.elemmap_0[el_id] for el_id in contained_l0}
    em1 = {el_id: cl.elemmap_1[el_id] for el_id in contained_l1}

    for cid in set(em0.keys()).union(em1.keys()):

        render_diff_inner(get_in([cid, 'element'], em0, {}),
                          get_in([cid, 'element'], em1, {}),
                          cl)

#####


# print()
# print("Equivalent lists")
# find_reordered([1, 2, 3, 4], [1, 2, 3, 4], set(), set(), set(), 0, 0, set(), 0)

# print()
# print("Simple reorder")
# for x in find_reordered([1, 2, 3, 4], [1, 3, 2, 4], set(), set(), set(), 0, 0, set(), 0):
#     print(x)

# print()
# print("Simple reorder at tail")
# find_reordered([1, 2, 3, 4], [1, 2, 4, 3], set(), set(), set(), 0, 0, set(), 0)

# print()
# print("Double reorder")
# find_reordered([1, 2, 3, 4, 5, 6], [1, 3, 2, 4, 6, 5], set(), set(), set(), 0, 0, set(), 0)

# print()
# print("Added element 5 in middle")
# find_reordered([1, 2, 3, 4], [1, 2, 5, 3, 4],
#                set([5]), set(), set(), 0, 0, set(), 0)

# print()
# print("Added element 5 at end")
# find_reordered([1, 2, 3, 4], [1, 2, 3, 4, 5],
#                set([5]), set(), set(), 0, 0, set(), 0)

# print()
# print("Removed element 5 at end")
# find_reordered([1, 2, 3, 4, 5], [1, 2, 3, 4],
#                set(), set([5]), set(), 0, 0, set(), 0)

# print()
# print("Removed element")
# find_reordered([1, 2, 3, 4], [1, 2, 4],
#                set(), set([3]), set(), 0, 0, set(), 0)

# print()
# print("Moved element in")
# find_reordered([1, 2, 3, 4], [1, 2, 5, 3, 4],
#                set(), set(), set([5]), 0, 0, set(), 0)

# print()
# print("Moved element out")
# find_reordered([1, 2, 5, 3, 4], [1, 2, 3, 4],
#                set(), set(), set([5]), 0, 0, set(), 0)


# print()
# print("Add element, reorder later ones")
# for x in find_reordered([1, 2, 3, 4], [1, 2, 5, 4, 3],
#                         set([5]), set(), set(), 0, 0, set(), 0):
#     print(x)
