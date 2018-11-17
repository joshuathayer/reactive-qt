from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
from PyQt5.QtCore import QObject

from deepdiff import DeepDiff

from dictdiffer import diff

import uuid

from toolz.dicttoolz import dissoc, merge
from toolz.itertoolz import get
from functools import reduce, partial

app = QApplication([])
window = QWidget()
vbox = QVBoxLayout()

def render0(old, new):

    diff = DeepDiff(old, new, view='tree',
                    ignore_order=False,
                    exclude_types={QObject})

    if 'iterable_item_added' in diff:
        for a in diff['iterable_item_added']:
            at = a.up.t2_child_rel.param
            item = a.up.t2_child_rel.child

            if item['element'] == 'label':
                ql = QLabel()
                ql.setText(item['text'])
                vbox.addWidget(ql)

                # mutate our local representation of the layout!
                item['_qobj'] = ql
                old.insert(at, item)

    if 'values_changed' in diff:
        for change in diff['values_changed']:
            element = change.up.t1['element']
            obj = change.up.t1['_qobj']
            param = change.up.t1_child_rel.param

            if element == 'label':
                if param == 'text':
                    obj.setText(change.t2)

    return old

elements = {}
components = {}

def render(old, new):
    diffs = diff(old, new)

    for d in diffs:
        (action, path, item) = d
        current_element = elements
        if action == 'add':

            # point into `elements` at the right place...
            for e in path:
                if path not in current_element:
                    current_element[path] = {}
                current_element = current_element[path]

            # add the element at the right place...
            for (at, content) in item:

                # update current representation of the layout
                current_element['id'] = str(uuid.uuid4())
                current_element[at] = item

        print(d)

    print("-----")

    return new

current_layout = []

new_layout = [{'element': 'label',
               'text': 'hello world'}]

current_layout = render(current_layout, new_layout)

new_layout = [{'element': 'label',
               'text': 'hello world'},
              {'element': 'label',
               'text': 'my name is joshua'}]

current_layout = render(current_layout, new_layout)


new_layout = [{'element': 'label',
               'text': 'hello world'},
              {'element': 'label',
               'text': 'my name is josh'},
              {'element': 'label',
               'text': 'i am not feeling so great'}]

current_layout = render(current_layout, new_layout)

new_layout = [{'element': 'label',
               'text': 'hello world'},
              {'element': 'label',
               'text': 'my name is josh!!!'},
              {'element': 'label',
               'text': 'i am not feeling so great'}]

current_layout = render(current_layout, new_layout)


# i don't think it's quite that easy. consider...

layout0  = [{'element': 'label',
             'text': 'hello',
             'id': 1234}]

layout1  = [{'element': 'button',
             'text': 'submit',
             'id': 5678},
            {'element': 'label',
             'text': 'hello',
             'id': 1234}]

# we clearly just added a new element, 5678. but
current_layout = render(layout0, layout1)
# shows us _changing_ every attribute of the first element of the
# list, then adding an new element, 1234. clearly not what we're
# after.

# will we have to make our own algorithm? it might not be so bad,
# especially since we have domain knownledge about our structure

layout0  = [{'element': 'button',
             'text': 'submit!!',
             'id': 5678},
            {'element': 'label',
             'text': 'sal',
             'id': 5679},
            {'element': 'label',
             'text': 'abby',
             'id': 5680},
            {'element': 'label',
             'text': 'bailey',
             'id': 5681},
            {'element': 'button',
             'text': 'i shall be removed',
             'id': 5667},
            {'element': 'button',
             'text': 'i am going to move and change',
             'id': 7777},
            {'element': 'vbox',
             'id': 9876,
             'contains': [
                 {'element': 'label',
                  'text': 'inner',
                  'id': 8765
                 }
             ]}]


layout1  = [{'element': 'button',
             'text': 'submit',
             'id': 5678},
            {'element': 'label',
             'text': 'hello',
             'id': 1234},
            {'element': 'label',
             'text': 'sal',
             'id': 5679},
            {'element': 'label',
             'text': 'bailey',
             'id': 5681},
            {'element': 'label',
             'text': 'abby',
             'id': 5680},
            {'element': 'vbox',
             'id': 9876,
             'contains': [
                 {'element': 'label',
                  'text': 'inner',
                  'id': 8765
                 },
                 {'element': 'button',
                  'text': 'i am going to move and change!',
                  'id': 7777},
             ]}]


def walk_elems(container):
    i = 0

    for ex in range(len(container['contains'])):
        e = container['contains'][ex]

        # XXX jt for containers, we want to return a ref to the first
        # and last object which we contain

        prev = None
        nxt = None
        if ex > 0:
            prev = container['contains'][ex-1]['id']
        if ex < len(container['contains']) - 1:
            nxt = container['contains'][ex+1]['id']

        yield e['id'], dissoc(e, 'contains'), \
            container['id'], prev, nxt

        if 'contains' in e:
            yield from walk_elems(e)

def merge_dicts(acc, new_elem):
    [eid, elem, elem_container, prev, nxt] = new_elem
    new_dict = {eid: {'element': elem,
                      'container': elem_container,
                      'previous': prev,
                      'next': nxt}}
    merged = merge(acc, new_dict)
    return merged

def elem_map(container):
    return reduce(merge_dicts, walk_elems(container), {})


def find_reordered(l0, l1, new, rmd, moved,
                   l0ix=0, l1ix=0, was_reordered=set()):

    # print(l0)
    # print(l1)
    # print(l0ix)
    # print(l1ix)
    # print(was_reordered)
    if l0ix == len(l0)-1 and l1ix == len(l1)-1:
        return

    elif l0[l0ix] == l1[l1ix]:
        # they're the same element
        print("{} and {} are the same".format(l0[l0ix], l1[l1ix]))
        find_reordered(l0, l1,
                       new,
                       rmd,
                       moved,
                       min(len(l0)-1, l0ix+1),
                       min(len(l1)-1, l1ix+1),
                       was_reordered)

    elif l0[l0ix] in was_reordered:
        # we've come across something in original list that we already
        # detected was moved. advance over it.
        print("Came across already-reordered {}".format(l0[l0ix]))
        find_reordered(l0, l1,
                       new,
                       rmd,
                       moved,
                       min(len(l0)-1, l0ix+1),
                       l1ix,
                       was_reordered)

    elif l0[l0ix] in rmd or l0[l0ix] in moved:
        # we've come across something in the original list that was
        # moved from this container, or removed from the
        # layout. advance over it
        print("SIDE EFFECT REMOVE/MOVE-OUT {}".format(l0[l0ix]))
        find_reordered(l0, l1,
                       new,
                       rmd,
                       moved,
                       min(len(l0)-1, l0ix+1),
                       l1ix,
                       was_reordered)

    elif l1[l1ix] in new or l1[l1ix] in moved:
        print("SIDE EFFECT ADD/MOVE-IN {} at {}".format(l1[l1ix], l1ix))
        find_reordered(l0, l1,
                       new,
                       rmd,
                       moved,
                       l0ix,
                       min(len(l1)-1, l1ix+1),
                       was_reordered)

    else:
        # a reordering in our container
        print("REORDERING SIDE EFFECT REMOVE {}".format(l1[l1ix]))
        print("REORDERING SIDE EFFECT ADD {} (at index {}?)".format(l1[l1ix], l0ix))
        was_reordered.add(l1[l1ix])
        find_reordered(l0, l1,
                       new,
                       rmd,
                       moved,
                       l0ix,
                       min(len(l1)-1, l1ix+1),
                       was_reordered)

print()
print("Equivalent lists")
find_reordered([1, 2, 3, 4], [1, 2, 3, 4], set(), set(), set(), 0, 0, set())

print()
print("Simple reorder")
find_reordered([1, 2, 3, 4], [1, 3, 2, 4], set(), set(), set(), 0, 0, set())

print()
print("Simple reorder at tail")
find_reordered([1, 2, 3, 4], [1, 2, 4, 3], set(), set(), set(), 0, 0, set())

print()
print("Double reorder")
find_reordered([1, 2, 3, 4, 5, 6], [1, 3, 2, 4, 6, 5], set(), set(), set(), 0, 0, set())

print()
print("Added element")
find_reordered([1, 2, 3, 4], [1, 2, 5, 3, 4],
               set([5]), set(), set(), 0, 0, set())

print()
print("Removed element")
find_reordered([1, 2, 3, 4], [1, 2, 4],
               set(), set([3]), set(), 0, 0, set())

print()
print("Moved element in")
find_reordered([1, 2, 3, 4], [1, 2, 5, 3, 4],
               set(), set(), set([5]), 0, 0, set())

print()
print("Moved element out")
find_reordered([1, 2, 5, 3, 4], [1, 2, 3, 4],
               set(), set(), set([5]), 0, 0, set())


def render_diff(l0, l1):
    elemmap_0 = elem_map(l0)
    elemmap_1 = elem_map(l1)

    elems_0 = set(elemmap_0.keys())
    elems_1 = set(elemmap_1.keys())

    common = elems_0.intersection(elems_1)

    new_elems = elems_1 - elems_0
    rm_elems = elems_0 - elems_1

    print("Partial?")
    changed = set()
    moved = set()
    reordered = set()


    for e0, e1 in zip(map(lambda x: get(x, elemmap_0), common),
                      map(lambda x: get(x, elemmap_1), common)):
        if e0['element'] != e1['element']:
            changed.add(e0['element']['id'])
        if e0['container'] != e1['container']:
            moved.add(e0['element']['id'])

    find_reordered(l0, l1, new_elems, rm_elems, moved)


    print("new elements: {}".format(new_elems))
    print("rm elements: {}".format(rm_elems))
    print("changed element: {}".format(changed))
    print("moved element: {}".format(moved))
    print("reordered element: {}".format(reordered))

# render_diff({'contains': layout0, 'id': 0},
#             {'contains': layout1, 'id': 0})

# given two layouts, return a 3-tuple of those elements which were added (and their path), those elements which were removed (and their prior path, i guess), and those elements which were changed.

#

#window.setLayout(vbox)
#window.show()
#app.exec_()


# >>> t1 = {'name': 'josh', 'age': 43, 'place': "san francisco"}
# >>> t2 = {'name': 'josh', 'age': 44, 'place': "san francisco", 'status':'sick'}
# >>> dd = DeepDiff(t1, t2, verbose_level=1, view='tree')
# >>> dd
# {'values_changed': {<root['age'] t1:43, t2:44>}, 'dictionary_item_added': {<root['status'] t1:Not Present, t2:'sick'>}}
# >>> (added,) = dd['dictionary_item_added']
# >>> added
# <root['status'] t1:Not Present, t2:'sick'>
# >>> added.up.t2_child_rel.param
# 'status'
# >>> added.up.t2_child_rel.child
# 'sick'

# >>> a=['x','y','z']
# >>> b=['y','z','t']
# >>> ff = DeepDiff(a, b, view='tree')
# >>> ff
# {'values_changed': {<root[2] t1:'z', t2:'t'>, <root[1] t1:'y', t2:'z'>, <root[0] t1:'x', t2:'y'>}}
# >>> ff = DeepDiff(a, b, view='tree', ignore_order=True)
# >>> ff
# {'iterable_item_removed': {<root[0] t1:'x', t2:Not Present>}, 'iterable_item_added': {<root[2] t1:Not Present, t2:'t'>}}
# >>> (removed,) = ff['iterable_item_removed']
# >>> removed
# <root[0] t1:'x', t2:Not Present>
# >>> removed.up.t1_child_rel.child
# 'x'
# >>> removed.up.t1_child_rel.param
# 0
# >>> (added,) = ff['iterable_item_added']
# >>> added.up.t2_child_rel.child
# 't'
# >>> added.up.t2_child_rel.param
# 2
