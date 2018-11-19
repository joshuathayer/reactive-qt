from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, \
    QLayout
from PyQt5.QtCore import QObject
import PyQt5.QtGui
from PyQt5.QtCore import Qt

import uuid

from toolz.dicttoolz import dissoc, merge
from toolz.itertoolz import get
from functools import reduce, partial

def input(prompt):
    [vbox
     [label {text: db_val('prompt')}]
     [input {on-submit: ...}]]

[vbox
 [input "what's your name"]]


[vbox {id: 123, color: blue}
 [label {text: "this is a label"}]
 [label {text: "this is another label"}]]

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
             'text': 'hello i am new',
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

        prev = None
        nxt = None
        if ex > 0:
            prev = container['contains'][ex-1]['id']
        if ex < len(container['contains']) - 1:
            nxt = container['contains'][ex+1]['id']

        # yield e['id'], dissoc(e, 'contains'), \
        #     container['id'], prev, nxt
        yield e['id'], e, \
            container['id'], prev, nxt

        if 'contains' in e:
            yield from walk_elems(e)

def merge_dicts(acc, new_elem):
    [eid, elem, elem_container, prev, nxt] = new_elem
    new_dict = {eid: {'element': elem,
                      'container': elem_container}}
    merged = merge(acc, new_dict)
    return merged

def elem_map(container):
    return reduce(merge_dicts, walk_elems(container), {})

def find_reordered(l0, l1, new, rmd, moved,
                   l0ix, l1ix, was_reordered, container):
    # print("----vv---")
    # print("{} {}".format(l0, l0ix))
    # print("{} {}".format(l1, l1ix))
    # print("{} {}".format(l0, l0ix))
    # print("{} {}".format(l1, l1ix))
    # print(len(l0))
    # print(was_reordered)
    # print("len0 {}".format(len(l0)))
    # print("len1 {}".format(len(l1)))

    if len(l1) > 0 and (l1[l1ix] in new or l1[l1ix] in moved):
        # print("SIDE EFFECT ADD/MOVE-IN {} at {} container {}".format(l1[l1ix], l1ix, container))

        if l1[l1ix] in new:
            yield ['add', l1[l1ix], l1ix, container]

        if l1[l1ix] in moved:
            yield ['reattach', l1[l1ix], l1ix, container]

        # >= catches case where l0 is empty
        if l0ix >= len(l0) - 1 and l1ix >= len(l1) - 1:
            return

        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  l0ix,
                                  min(len(l1)-1, l1ix+1),
                                  was_reordered, container)

    elif len(l1) > 0 and (len(l0) > 0 and l0[l0ix] == l1[l1ix]):
        # they're the same element
        # print("{} and {} are the same".format(l0[l0ix], l1[l1ix]))
        if l0ix >= len(l0) -1 and l1ix >= len(l1) - 1:
            return
        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  min(len(l0)-1, l0ix+1),
                                  min(len(l1)-1, l1ix+1),
                                  was_reordered, container)

    elif len(l0) > 0 and l0[l0ix] in was_reordered:
        # we've come across something in original list that we already
        # detected was moved. advance over it.
        # print("Came across already-reordered {}".format(l0[l0ix]))
        if l0ix >= len(l0) -1 and l1ix >= len(l1) - 1:
            return
        yield from find_reordered(l0, l1,
                                  new,
                                  rmd,
                                  moved,
                                  min(len(l0)-1, l0ix+1),
                                  l1ix,
                                  was_reordered, container)

    elif len(l0) > 0 and (l0[l0ix] in rmd or l0[l0ix] in moved):
        # we've come across something in the original list that was
        # moved from this container, or removed from the
        # layout. advance over it
        # print("SIDE EFFECT REMOVE/MOVE-OUT {} container {}".format(l0[l0ix], container))
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

    elif len(l0) > 0 and len(l1) > 0:
        # a reordering in our container
        # print("REORDERING SIDE EFFECT REMOVE {}".format(l1[l1ix]))
        # print("REORDERING SIDE EFFECT ADD {} at index {} container {}".format(l1[l1ix], l1ix, container))

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



def instantiate_new_elements(new_elements, element_map):
    for el in new_elements:
        if el['element']['element'] == 'label':
            ob = QLabel()
            ob.setText(el['element']['text'])
            element_map[el['element']['id']] = ob
        elif el['element']['element'] == 'button':
            ob = QPushButton()
            ob.setText(el['element']['text'])
            element_map[el['element']['id']] = ob
        elif el['element']['element'] == 'vbox':
            ob = QVBoxLayout()
            element_map[el['element']['id']] = ob

    return element_map

def take_action(action, args, all_elements):

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
        # del all_elements[elem]

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


def render_diff(l0, l1, element_map): # should return new element map
    elemmap_0 = elem_map(l0) # native objects
    elemmap_1 = elem_map(l1) # native objects
    # print("elemmap 1 {}".format(elemmap_1))
    # print("element map {}".format(element_map))

    elems_0 = set(elemmap_0.keys())
    elems_1 = set(elemmap_1.keys())

    common = elems_0.intersection(elems_1)

    new_elems = elems_1 - elems_0  # just IDs
    print("new elems {}".format(new_elems))
    rm_elems = elems_0 - elems_1

    # if any removed elements are containers, their contained elements
    # must also be removed!
    for el in rm_elems:
        if 'contains' in elemmap_0[el]['element']:
            for contained in elemmap_0[el]['element']['contains']:
                print("ALSO REMOVING {}".format(contained['id']))
                rm_elems.add(contained['id'])

    changed = set()
    moved = set()
    reordered = set()

    new_element_objs = list(map(lambda x: elemmap_1[x], new_elems))
    element_map = instantiate_new_elements(new_element_objs,
                                           element_map)

    for e0, e1 in zip(map(lambda x: get(x, elemmap_0), common),
                      map(lambda x: get(x, elemmap_1), common)):
        if e0['element'] != e1['element']:
            changed.add(e0['element']['id'])
        if e0['container'] != e1['container']:
            moved.add(e0['element']['id'])

    # print("new elements: {}".format(new_elems))
    # print("rm elements: {}".format(rm_elems))
    # print("changed element: {}".format(changed))
    # print("moved element: {}".format(moved))

    actions = find_reordered(list(map(lambda x: x['id'], l0['contains'])),
                             list(map(lambda x: x['id'], l1['contains'])),
                             new_elems, rm_elems, moved, 0, 0, set(),
                             l0['id'])

    all_elems = merge(elemmap_0, elemmap_1)

    # containers = filter(lambda x: 'contains'
    #                     in elemmap_1[x]['element'], elems_1)

    containers = filter(lambda x: 'contains'
                        in all_elems[x]['element'], set(all_elems.keys()))

    def do_action(the_actions, em0, em1):
        if the_actions is None:
            return

        for a in the_actions:
            print(a)
            take_action(a[0], a[1:], element_map)

        print("in do action, em0 is {}".format(em0))
        print("in do action, em1 is {}".format(em1))
        all_elems = merge(em0, em1)

        containers = filter(lambda x: 'contains'
                            in all_elems[x]['element'], set(all_elems.keys()))

        for cid in containers:

            if cid in em0:
                e0 = list(map(lambda x: x['id'],
                              em0[cid]['element']['contains']))

            else:
                e0 = []

            e1 = list(map(lambda x: x['id'],
                          em1[cid]['element']['contains']))

            print("RECURSE CONTAINED 0 {}".format(e0))
            print("RECURSE CONTAINED 1 {}".format(e1))

            e1_dict = {}
            e0_dict = {}
            for el_id in e0:
                e0_dict[el_id] = all_elems[el_id]
            for el_id in e1:
                e1_dict[el_id] = all_elems[el_id]

            new_actions = find_reordered(e0,
                                         e1,
                                         new_elems,
                                         rm_elems,
                                         moved,
                                         0,
                                         0,
                                         set(),
                                         cid)
            do_action(new_actions, e0_dict, e1_dict)

    do_action(actions, elemmap_0, elemmap_1)

    for el in rm_elems:
        del element_map[el]

    return element_map


app = QApplication([])
window = QWidget()
vbox = QVBoxLayout()

class AppWindow(QWidget):
    def __init__(self, layouts, elements):
        super().__init__()
        self.layouts = layouts
        self.current_layout_ix = 0
        self.elements = elements

    def next_layout(self):
        c = self.layouts[self.current_layout_ix]
        self.current_layout_ix = (self.current_layout_ix + 1) % len(self.layouts)
        c_next = self.layouts[self.current_layout_ix]
        self.elements = render_diff({'contains': c, 'id': 0},
                                    {'contains': c_next, 'id': 0},
                                    self.elements)

    def prev_layout(self):
        c = self.layouts[self.current_layout_ix]
        self.current_layout_ix = (self.current_layout_ix - 1) % len(self.layouts)
        c_next = self.layouts[self.current_layout_ix]
        self.elements = render_diff({'contains': c, 'id': 0},
                                    {'contains': c_next, 'id': 0},
                                    self.elements)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Q:
            self.close()
        elif e.key() == Qt.Key_Comma:
            self.next_layout()
        elif e.key() == Qt.Key_Period:
            self.prev_layout()

layouts = [[], layout0, layout1]
elements = {0: vbox}

appwindow = AppWindow(layouts, elements)

render_diff({'contains': [], 'id': 0},
            {'contains': [], 'id': 0},
            elements)


appwindow.setLayout(vbox)
appwindow.show()
app.exec_()


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
