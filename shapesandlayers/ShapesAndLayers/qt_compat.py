try:
    from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg, uic, sip
    _QT6 = True
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg, uic
    try:
        import sip
    except ImportError:
        sip = None
    _QT6 = False


def _alias(obj, name, value):
    if not hasattr(obj, name):
        setattr(obj, name, value)


if _QT6:
    qt = QtCore.Qt

    # Old Qt5-style enum names used throughout the plugin.
    _alias(QtWidgets.QAbstractItemView, "ExtendedSelection", QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
    _alias(QtWidgets.QAbstractItemView, "SingleSelection", QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
    _alias(QtWidgets.QHeaderView, "ResizeToContents", QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
    _alias(QtCore.QEvent, "MouseButtonRelease", QtCore.QEvent.Type.MouseButtonRelease)

    _alias(qt, "ControlModifier", qt.KeyboardModifier.ControlModifier)
    _alias(qt, "Tool", qt.WindowType.Tool)
    _alias(qt, "BlankCursor", qt.CursorShape.BlankCursor)

    _alias(qt, "ItemIsSelectable", qt.ItemFlag.ItemIsSelectable)
    _alias(qt, "ItemIsEnabled", qt.ItemFlag.ItemIsEnabled)
    _alias(qt, "ItemIsEditable", qt.ItemFlag.ItemIsEditable)
    _alias(qt, "ItemIsUserCheckable", qt.ItemFlag.ItemIsUserCheckable)

    _alias(qt, "Checked", qt.CheckState.Checked)
    _alias(qt, "Unchecked", qt.CheckState.Unchecked)

    # Qt6 nests data roles under Qt.ItemDataRole.
    _alias(qt, "UserRole", qt.ItemDataRole.UserRole)
    _alias(qt, "DisplayRole", qt.ItemDataRole.DisplayRole)
    _alias(qt, "EditRole", qt.ItemDataRole.EditRole)
    _alias(qt, "DecorationRole", qt.ItemDataRole.DecorationRole)

    # Standard buttons are nested in Qt6 as well.
    _alias(QtWidgets.QMessageBox, "Yes", QtWidgets.QMessageBox.StandardButton.Yes)
    _alias(QtWidgets.QMessageBox, "No", QtWidgets.QMessageBox.StandardButton.No)
    _alias(QtWidgets.QMessageBox, "Ok", QtWidgets.QMessageBox.StandardButton.Ok)
    _alias(QtWidgets.QMessageBox, "Cancel", QtWidgets.QMessageBox.StandardButton.Cancel)
