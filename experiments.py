from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
from PyQt5.QtCore import QObject

from deepdiff import DeepDiff

from dictdiffer import diff

import uuid

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

layout1  = [{'element': 'button',
             'text': 'submit',
             'id': 5678},
            {'element': 'label',
             'text': 'hello',
             'id': 1234},
            {'element': 'vbox',
             'id': 9876,
             'contains': [
                 {'element': 'label',
                  'text': 'inner',
                  'id': 8765
                 }
             ]}]

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
