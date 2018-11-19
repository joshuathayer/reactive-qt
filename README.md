## ractive qt

_Like react, but for qt_

This project intends to allow declarative PyQt creation and modification.

Layouts are expressed as recursive python dictionaries.

Two layouts can be compared, which generates a list of mutations that can be taken to move from the first layout to the second.

Those mutations can then be applied to the current PyQt application, which updates the user-facing UI.

This is intended to be a low level library which more expressive UI modification libraries can be built on.

See `example.py` for use.

This is very early work: only a couple of element types are supported, only element movement, creation, and deletion are supported (not modification yet), there are bugs, etc.
