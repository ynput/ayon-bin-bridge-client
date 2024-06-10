import threading
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QProgressBar, QLabel, QScrollArea, 
                             QSpacerItem, QSizePolicy)
from qtpy.QtGui import QPixmap
from qtpy.QtCore import Qt
from qtpy.QtCore import QObject, Signal, Slot, QThread, QCoreApplication


class AyonProgressBar(QWidget):
    progress_changed = Signal(int)

    def __init__(self, text, multiProgressParent, icon_path=None, parent=None):
        super().__init__(parent)

        self.multiProgressParent = multiProgressParent
        
        self.layout = QHBoxLayout()
      
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
    
    def set_progress(self, value):
        self.progress_bar.setValue(value)
   
    # @Slot(int)
    # def set_progress(self, value):
    #     if self.thread() != QThread.currentThread():
    #         # If called from a different thread, emit a signal to invoke set_progress in the main thread
    #         self.progress_changed.emit(value)
    #     else:
    #         # If called from the main thread, directly set the progress
    #         self.progress_bar.setValue(value)

    def set_text(self, text:str):
        self.text_label.setText(text)
    
    def close_progress_bar(self):
        self.multiProgressParent.remove_progress_bar(self)
        return
        

class AyonMultiProgressWidget(QWidget):
    def __init__(self):
        self.thread_lock = threading.Lock()
        self.progress_bar_list = []
        with self.thread_lock:
            super().__init__()

            self.layout = QVBoxLayout(self)
            
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            
            self.scroll_widget = QWidget()
            self.scroll_layout = QVBoxLayout(self.scroll_widget)
            self.scroll_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
            self.scroll_area.setWidget(self.scroll_widget)
            self.layout.addWidget(self.scroll_area)
           
            self.setMinimumSize(400, 300)


    def add_progress_bar(self, text, icon_path=None):
        with self.thread_lock:
            progress_bar_instance = AyonProgressBar(icon_path=icon_path, text=text, multiProgressParent=self)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, progress_bar_instance)
            self.scroll_layout.update()
            return progress_bar_instance 
    
    def remove_progress_bar(self, progress_bar:AyonProgressBar):
        with self.thread_lock:

            element = self.scroll_layout.indexOf(progress_bar)
            if element == -1:
                return

            self.scroll_layout.removeWidget(progress_bar)
            progress_bar.deleteLater()
        return

    def close_window(self):
        with self.thread_lock:
            self.scroll_layout.removeWidget(self.scroll_widget)
            self.scroll_widget.setParent(None)
            super().close()

