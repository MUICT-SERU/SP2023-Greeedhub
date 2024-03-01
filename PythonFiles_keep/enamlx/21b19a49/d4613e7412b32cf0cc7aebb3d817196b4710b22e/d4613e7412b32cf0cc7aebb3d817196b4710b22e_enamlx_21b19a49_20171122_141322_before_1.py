# -*- coding: utf-8 -*-
"""
Copyright (c) 2015, Jairus Martin.
Distributed under the terms of the MIT License.
The full license is in the file COPYING.txt, distributed with this software.
Created on Aug 29, 2015
"""
from atom.api import Instance, Callable
from enamlx.widgets.key_event import ProxyKeyEvent
from enaml.qt.qt_control import QtControl
from enaml.qt import QtCore


class QtKeyEvent(QtControl, ProxyKeyEvent):

    # Reference to the original handler
    _keyPressEvent = Callable()

    # Reference to the original handler
    _keyReleaseEvent = Callable()

    #: Widget that this key press handler is overriding
    widget = Instance(QtCore.QObject)

    def create_widget(self):
        """ The KeyEvent uses the parent_widget as it's widget """
        self.widget = self.parent_widget()

    def init_widget(self):
        """ The KeyEvent uses the parent_widget as it's widget """
        super(QtKeyEvent, self).init_widget()
        d = self.declaration
        widget = self.widget
        self._keyPressEvent = widget.keyPressEvent
        self._keyReleaseEvent = widget.keyReleaseEvent
        self.set_enabled(d.enabled)

    def set_enabled(self, enabled):
        widget = self.widget
        if enabled:
            widget.keyPressEvent = lambda event: self.on_key_press(event)
            widget.keyReleaseEvent = lambda event: self.on_key_release(event)
        else:
            # Restore original
            widget.keyPressEvent = self._keyPressEvent
            widget.keyReleaseEvent = self._keyReleaseEvent

    def on_key_press(self, event):
        d = self.declaration
        try:
            if (d.key_code and event.key() == d.key_code) or \
                    (d.key and d.key in event.text()):
                if not d.repeats and event.isAutoRepeat():
                    return
                d.pressed(event)
        finally:
            self._keyPressEvent(event)

    def on_key_release(self, event):
        d = self.declaration
        try:
            if (d.key_code and event.key() == d.key_code) or \
                    (d.key and d.key in event.text()):
                if not d.repeats and event.isAutoRepeat():
                    return
                d.released(event)
        finally:
            self._keyReleaseEvent(event)
