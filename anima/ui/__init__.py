# -*- coding: utf-8 -*-

import os
from anima import logger

# Choose between PyQt4 or PySide
PYSIDE = 'PySide'
PYSIDE2 = 'PySide2'
PYSIDE6 = "PySide6"
PYQT4 = 'PyQt4'
QTPY = 'QtPy'  # support for https://www.gihub.com/motttoso/Qt.py

# set the default
qt_lib_key = "QT_LIB"
qt_lib = PYSIDE

ICON_CACHE = {}
FONT_CACHE = {}


if qt_lib_key in os.environ:
    qt_lib = os.environ[qt_lib_key]
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_lib.lower()


def IS_PYSIDE():
    return qt_lib == PYSIDE


def IS_PYSIDE2():
    return qt_lib == PYSIDE2

def IS_PYSIDE6():
    return qt_lib.lower() == PYSIDE6.lower()

def IS_PYQT4():
    return qt_lib == PYQT4


def IS_QTPY():
    return qt_lib == QTPY


def SET_PYSIDE():
    logger.debug('setting environment to PySide')
    global qt_lib
    qt_lib = PYSIDE


def SET_PYSIDE2():
    logger.debug('setting environment to PySide2')
    global qt_lib
    qt_lib = PYSIDE2

def SET_PYSIDE6():
    logger.debug("setting environment to PySide6")
    global qt_lib
    qt_lib = PYSIDE6
    # also set the qt_api key for QtPy
    os.environ["QT_API"] = qt_lib.lower()


def SET_PYQT4():
    logger.debug('setting environment to PyQt4')
    global qt_lib
    qt_lib = PYQT4


def SET_QT():
    logger.debug('setting environment to Qt')
    global qt_lib
    qt_lib = QTPY
