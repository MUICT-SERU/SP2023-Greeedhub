from Qt import QtCore, __binding__


# GENERAL

# The original object; Context, Instance or Plugin
Item = QtCore.Qt.UserRole + 9

# The internal .id of any item
Id = QtCore.Qt.UserRole + 7

# The display name of an item
Label = QtCore.Qt.DisplayRole + 10

# The item has not been used
IsIdle = QtCore.Qt.UserRole + 8

IsChecked = QtCore.Qt.UserRole + 0
IsOptional = QtCore.Qt.UserRole + 11
IsProcessing = QtCore.Qt.UserRole + 1
HasFailed = QtCore.Qt.UserRole + 3
HasSucceeded = QtCore.Qt.UserRole + 4
HasProcessed = QtCore.Qt.UserRole + 6

# PLUGINS

# Available, context-relevant plug-ins
Actions = QtCore.Qt.UserRole + 2


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)
        self.items = list()

        # Common schema
        self.schema = {
            Id: "id",
            IsIdle: "is_idle",
            IsProcessing: "is_processing",
            HasProcessed: "has_processed",
            HasSucceeded: "has_succeeded",
            HasFailed: "has_failed",
            Actions: "actions",
            IsOptional: "optional"
        }

    def __iter__(self):
        """Yield each row of model"""
        for index in range(len(self.items)):
            yield self.createIndex(index, 0)

    def data(self, index, role):
        if role == Item:
            return self.items[index.row()]

    def append(self, item):
        """Append item to end of model"""
        self.beginInsertRows(QtCore.QModelIndex(),
                             self.rowCount(),
                             self.rowCount())

        self.items.append(item)
        self.endInsertRows()

    def rowCount(self, parent=None):
        return len(self.items)

    def columnCount(self, parent):
        return 2

    def reset(self):
        self.beginResetModel()
        self.items[:] = []
        self.endResetModel()

    def update_with_result(self, result):
        for record in result["records"]:
            print(record.msg)


class PluginModel(TableModel):
    def __init__(self):
        super(PluginModel, self).__init__()

        self.schema.update({
            Label: "label",
            IsChecked: "active",
        })

    def append(self, item):
        item.is_idle = True
        item.is_processing = False
        item.has_processed = False
        item.has_succeeded = False
        item.has_failed = False
        item.label = item.label or item.__name__
        return super(PluginModel, self).append(item)

    def data(self, index, role):
        item = self.items[index.row()]
        key = self.schema.get(role)

        if key is None:
            return

        if role == Actions:
            actions = list(item.actions)

            # Context specific actions
            for action in actions:
                if action.on == "failed" and not item.has_failed:
                    actions.remove(action)
                if action.on == "succeeded" and not item.has_succeeded:
                    actions.remove(action)
                if action.on == "processed" and not item.has_processed:
                    actions.remove(action)
                if action.on == "notProcessed" and item.has_processed:
                    actions.remove(action)

            # Discard empty groups
            i = 0
            try:
                action = actions[i]
            except IndexError:
                pass
            else:
                while action:
                    try:
                        action = actions[i]
                    except IndexError:
                        break

                    isempty = False

                    if action.__type__ == "category":
                        try:
                            next_ = actions[i + 1]
                            if next_.__type__ != "action":
                                isempty = True
                        except IndexError:
                            isempty = True

                        if isempty:
                            actions.pop(i)

                    i += 1

            return actions

        key = self.schema.get(role)

        if key is None:
            return

        value = getattr(item, key, None)

        if value is None:
            value = super(PluginModel, self).data(index, role)

        return value

    def setData(self, index, value, role):
        item = self.items[index.row()]
        key = self.schema.get(role)

        if key is None:
            return

        setattr(item, key, value)

        if __binding__ in ("PyQt4", "PySide"):
            self.dataChanged.emit(index, index)
        else:
            self.dataChanged.emit(index, index, [role])

    def update_with_result(self, result):
        item = result["plugin"]

        index = self.items.index(item)
        index = self.createIndex(index, 0)
        self.setData(index, False, IsIdle)
        self.setData(index, False, IsProcessing)
        self.setData(index, True, HasProcessed)
        self.setData(index, result["success"], HasSucceeded)
        self.setData(index, not result["success"], HasFailed)
        super(PluginModel, self).update_with_result(result)


class InstanceModel(TableModel):
    def __init__(self):
        super(InstanceModel, self).__init__()

        self.schema.update({
            Label: "label",
            IsChecked: "publish",
        })

    def append(self, item):
        item.data["has_succeeded"] = False
        item.data["has_failed"] = False
        item.data["is_idle"] = True
        item.data["optional"] = item.data.get("optional", True)
        item.data["publish"] = item.data.get("publish", True)
        item.data["label"] = item.data.get("label", item.data["name"])
        return super(InstanceModel, self).append(item)

    def data(self, index, role):
        super(InstanceModel, self).data(index, role)

        item = self.items[index.row()]
        key = self.schema.get(role)

        if not key:
            return

        value = item.data.get(key)

        if value is None:
            value = super(InstanceModel, self).data(index, role)

        return value

    def setData(self, index, value, role):
        item = self.items[index.row()]
        key = self.schema.get(role)

        if key is None:
            return

        item.data[key] = value

        if __binding__ in ("PyQt4", "PySide"):
            self.dataChanged.emit(index, index)
        else:
            self.dataChanged.emit(index, index, [role])

    def update_with_result(self, result):
        item = result["instance"]

        if item is None:
            return

        index = self.items.index(item)
        index = self.createIndex(index, 0)
        self.setData(index, False, IsIdle)
        self.setData(index, False, IsProcessing)
        self.setData(index, True, HasProcessed)
        self.setData(index, result["success"], HasSucceeded)
        self.setData(index, not result["success"], HasFailed)
        super(InstanceModel, self).update_with_result(result)
