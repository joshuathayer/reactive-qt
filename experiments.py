from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout
from PyQt5.QtCore import QObject

from deepdiff import DeepDiff

app = QApplication([])
window = QWidget()
vbox = QVBoxLayout()

def render(old, new):

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
               'text': 'my name is joshua'},
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



window.setLayout(vbox)
window.show()
app.exec_()


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
