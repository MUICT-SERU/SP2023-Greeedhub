# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 24, 2015
"""
from atom.api import Instance, Property, ForwardInstance, Bool
from enaml.core.pattern import Pattern
from enaml.qt.qt_control import QtControl
from enaml.qt.qt_menu import QtMenu
from enaml.qt.qt_widget import QtWidget
from enaml.qt import QT_API, PYSIDE_API, PYQT4_API, PYQT5_API, PYSIDE2_API

if QT_API in PYSIDE_API+PYQT4_API:
    from enaml.qt.QtGui import QHeaderView
else:
    from qtpy.QtWidgets import QHeaderView
from enaml.qt.QtCore import QModelIndex

from enamlx.widgets.abstract_item import (
    ProxyAbstractWidgetItem,
    ProxyAbstractWidgetItemGroup
)

TEXT_H_ALIGNMENTS = {
    'left': 0x01,       # Qt.AlignLeft,
    'right': 0x02,      # Qt.AlignRight,
    'center': 0x04,     # Qt.AlignHCenter,
    'justify': 0x08,    # Qt.AlignJustify,
}

TEXT_V_ALIGNMENTS = {
    'top': 0x20,        # Qt.AlignTop,
    'bottom': 0x40,     # Qt.AlignBottom,
    'center': 0x80,     # Qt.AlignVCenter,
}

RESIZE_MODES = {
    'interactive': QHeaderView.Interactive,
    'fixed': QHeaderView.Fixed,
    'stretch': QHeaderView.Stretch,
    'resize_to_contents': QHeaderView.ResizeToContents,
    'custom': QHeaderView.Custom
}


class AbstractQtWidgetItemGroup(QtControl, ProxyAbstractWidgetItemGroup):
    """ Base class for Table and Tree Views
    
    """
    #: Context menu for this group
    menu = Instance(QtMenu)

    def _get_items(self):
        return [c for c in self.children()
                if isinstance(c, AbstractQtWidgetItem)]

    #: Internal items
    #: TODO: Is a cached property the right thing to use here??
    #: Why not a list??
    _items = Property(lambda self: self._get_items(), cached=True)

    def init_layout(self):
        for child in self.children():
            if isinstance(child, QtMenu):
                self.menu = child

    def refresh_style_sheet(self):
        pass  # Takes a lot of time

    def child_added(self, child):
        """ When a child is added, reset the cached item list. 
        
        """
        super(AbstractQtWidgetItemGroup, self).child_added(child)
        self.get_member('_items').reset(self)

    def child_removed(self, child):
        """ When a child is removed, reset the cached item list. 
        
        """
        super(AbstractQtWidgetItemGroup, self).child_removed(child)
        self.get_member('_items').reset(self)


def _abstract_item_view():
    from .qt_abstract_item_view import QtAbstractItemView
    return QtAbstractItemView


class AbstractQtWidgetItem(AbstractQtWidgetItemGroup, ProxyAbstractWidgetItem):
    #: Index within the view
    index = Instance(QModelIndex)

    #: Delegate widget to display when editing the cell
    #: if the widget is editable
    delegate = Instance(QtWidget)

    #: Reference to view
    view = ForwardInstance(_abstract_item_view)

    #: Used to check if the item has been destroyed already
    is_valid = Bool(True)

    def create_widget(self):
        # View items have no widget!
        for child in self.children():
            if isinstance(child, (Pattern, QtWidget)):
                self.delegate = child

    def init_widget(self):
        pass

    def init_layout(self):
        super(AbstractQtWidgetItem, self).init_layout()
        self._update_index()

    def _update_index(self):
        """ Update where this item is within the model"""
        raise NotImplementedError

    def destroy(self):
        """ Since Views use deferred calls to make items, we
        must be able to check if the item was destroyed before accessing it
        to avoid crashes.
        
        """
        self.is_valid = False
        super(AbstractQtWidgetItem, self).destroy()
