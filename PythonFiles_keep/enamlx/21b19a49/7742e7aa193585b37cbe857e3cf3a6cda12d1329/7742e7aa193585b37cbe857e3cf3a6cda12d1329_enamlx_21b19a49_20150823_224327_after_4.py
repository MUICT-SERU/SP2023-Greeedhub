from atom.api import Atom, Unicode, Range, Bool, observe

import enamlx
enamlx.install()

import enaml
from enaml.qt.qt_application import QtApplication

if __name__ == '__main__':
    with enaml.imports():
        from table_widget import Main

    app = QtApplication()
    view = Main()
    view.show()

    app.start()