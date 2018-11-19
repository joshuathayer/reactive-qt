## ractive qt

_Like react, but for qt_

This project intends to allow declarative PyQt layout creation and modification.

Layouts are expressed as recursive python dictionaries.

Two layouts can be compared, which generates a list of mutations that can be taken to move from the first layout to the second.

Those mutations can then be applied to the current PyQt application, which updates the user-facing UI.

This is intended to be a low level library which more expressive UI modification libraries can be built on.

Here's the idea.

Imagine you've bootstrapped your Qt app with a simple vbox:

    vbox = QVBoxlayout()
    window = QWidget()
    window.setLayout(vbox)

We build a simple python data structure which represents the initial state of the app:

    layout0 = [{'component': 'vbox',
                'id': 0,
                'contains': []}]

...and create a data structure for the "next" state of the app (which is to say, the state we _want_ our app to be in):

    layout0 = [{'component': 'vbox',
                'id': 0,
                'contains': [
                  {'component': 'label',
                   'id': 1000,
                   'text': 'hello'},
                  {'component': 'label',
                   'id': 1001,
                   'text': 'world'}]]}]

Then we call `render_diff`, giving the current layout, the next layout, and a dictionary of all known Qt elements. This call will update the Qt UI to make it reflect the new application state, and will return a new value for the dictionary of all known Qt elements.

    elements = render_diff(layout0, layout1, {0: vbox})

Now we can make changes to the UI:

    layout2 = [{'component': 'vbox',
                'id': 0,
                'contains': [
                  {'component': 'label',
                   'id': 1001,
                   'text': 'world:'}
                  {'component': 'label',
                   'id': 1000,
                   'text': 'hello!'},
                  {'component': 'vbox',
                   'id': 2000,
                   'contains': [
                      {'component': 'button',
                       'id': 2001,
                       'text': 'continue'},
                      {'component': 'button',
                       'id': 2002,
                       'text': 'quit'}]}]}]

    elements = render_diff(layout1, layout2, elements)

The `render_diff` call here calculates a series of mutations required to move the UI `layout1` to `layout2`, and makes those mutations on the Qt UI. In this case, that means reordering elements 1000 and 1001, and adding the new vbox (id 2000) and its subelements.

See `example.py` for working example.

This is very early work: only a couple of element types are supported, only element movement, creation, and deletion are supported (not modification yet), there are bugs, etc.
