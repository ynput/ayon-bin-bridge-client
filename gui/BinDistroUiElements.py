import threading
from PyQt5.QtCore import pyqtSignal
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QProgressBar, QLabel, QScrollArea, 
                             QSpacerItem, QSizePolicy)
from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt

class AyonProgressBar(QWidget):
    set_progress_signal = pyqtSignal(int)
    set_text_signal = pyqtSignal(str)
    close_progress_bar_signal = pyqtSignal()

    def __init__(self, text, multi_progress_parent, icon_path=None, parent=None):
        super().__init__(parent)

        self.set_progress_signal.connect(self._set_progress)
        self.set_text_signal.connect(self._set_text)
        self.close_progress_bar_signal.connect(self._close_progress_bar)

        self.multi_progress_parent = multi_progress_parent
        
        self.layout = QHBoxLayout()
        
        self.icon_label = None
        if icon_path:
            self.icon_label = QLabel()
            pixmap = QPixmap(icon_path)
            scaled_pixmap = pixmap.scaled(18, 18, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
            self.layout.addWidget(self.icon_label)

        self.text_label = QLabel(text)
        self.layout.addWidget(self.text_label)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)
   
    def __del__(self):
        self.progress_bar.deleteLater()
        self.text_label.deleteLater()
        if self.icon_label:
            self.icon_label.deleteLater()
        self.multi_progress_parent = None

    def set_progress(self, value):
        self.set_progress_signal.emit(value)

    def _set_progress(self, value):
        self.progress_bar.setValue(value)

    def set_text(self, text:str):
        self.set_text_signal.emit(text)
   
    def _set_text(self, text:str):
        self.text_label.setText(text)

    def close_progress_bar(self):
        self.close_progress_bar_signal.emit()

    def _close_progress_bar(self):
        self.multi_progress_parent.remove_progress_bar(self)

        self.deleteLater()
        return


class AyonMultiProgressWidget(QWidget):
    remove_progress_bar_signal = pyqtSignal(object)
    close_window_signal = pyqtSignal()

    def __init__(self):
        self.thread_lock = threading.Lock()
        self.progress_bar_list = []

        with self.thread_lock:
            super().__init__()

            self.remove_progress_bar_signal.connect(self._remove_progress_bar)
            self.close_window_signal.connect(self._close_window)

            self.layout = QVBoxLayout(self)
            
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            
            self.scroll_widget = QWidget()
            self.scroll_layout = QVBoxLayout(self.scroll_widget)
            self.scroll_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
            self.scroll_area.setWidget(self.scroll_widget)
            self.layout.addWidget(self.scroll_area)
           
            self.setMinimumSize(400, 300)


    def add_progress_bar(self, text:str, icon_path:str=""):
        with self.thread_lock:
            progress_bar_instance = AyonProgressBar(icon_path=icon_path, text=text, multi_progress_parent=self)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, progress_bar_instance)
            self.scroll_layout.update()
            return progress_bar_instance 
        
    def remove_progress_bar(self, progress_bar):
        self.remove_progress_bar_signal.emit(progress_bar)

    def _remove_progress_bar(self, progress_bar):
        with self.thread_lock:
            element = self.scroll_layout.indexOf(progress_bar)
            if element == -1:
                return
            self.scroll_layout.removeWidget(progress_bar)
            progress_bar.deleteLater()

    def close_window(self):
        self.close_window_signal.emit()

    def _close_window(self):
        with self.thread_lock:
            self.scroll_layout.removeWidget(self.scroll_widget)
            self.scroll_widget.setParent(None)
            super().close()
