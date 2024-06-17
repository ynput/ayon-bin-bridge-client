import random
import os
from qtpy import QtWidgets, QtCore, QtGui
from ..work_handler import worker

STYLE_SHEET_DIR = os.path.join(os.path.dirname(__file__), "style_data")

DEFAULT_STYLE_SHEET = None
with open(os.path.join(STYLE_SHEET_DIR, "progress_default_style.qss"), "r") as f:
    DEFAULT_STYLE_SHEET = f.read()

FAILED_STYLE_SHEET = None
with open(os.path.join(STYLE_SHEET_DIR, "progress_failed_style.qss"), "r") as f:
    FAILED_STYLE_SHEET = f.read()

FINISHED_STYLE_SHEET = None
with open(os.path.join(STYLE_SHEET_DIR, "progress_finished_style.qss"), "r") as f:
    FINISHED_STYLE_SHEET = f.read()


class ProgressBar(QtWidgets.QWidget):

    def __init__(self, progress, parent):

        super().__init__(parent)

        self._progress = progress

        icon_label = None
        text_label = None
        if isinstance(progress, worker.ProgressItem):
            if progress.icon:
                icon_label = QtWidgets.QLabel(self)
                pixmap = QtGui.QPixmap(progress.icon)
                scaled_pixmap = pixmap.scaled(
                    18, 18, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
                )
                icon_label.setPixmap(scaled_pixmap)

            text_label = QtWidgets.QLabel(progress.title, self)
        progress_bar = QtWidgets.QProgressBar(self)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if icon_label:
            layout.addWidget(icon_label, 0)
        if text_label:
            layout.addWidget(text_label)

        layout.addWidget(progress_bar)

        self._progress_bar = progress_bar
        self._icon_label = icon_label
        self._text_label = text_label

    def is_finished(self):
        return self._progress.finished and not self._progress.failed

    @property
    def progress_bar(self):
        return self._progress_bar

    def update_progress(self):
        if self._progress.is_failed:
            self._progress_bar.setValue(100)
            self._progress_bar.setFormat("Failed")
            self._progress_bar.setStyleSheet(FAILED_STYLE_SHEET)
            return
        if self._progress.progress == -1:
            self._progress_bar.setValue(
                self._progress_bar.value() + random.uniform(-1, 3)
            )
            self._progress_bar.setFormat("Processing")
            return

        self._progress_bar.setValue(self._progress.progress)
        self._progress_bar.setFormat(f"{self._progress.progress}%")


class MultiProgressWidget(QtWidgets.QWidget):

    def __init__(self, controller, parent, delet_progress_bar_on_finish: bool = True):
        super().__init__(parent)

        self._controller = controller
        self._progress_bar_by_id = {}

        self._delet_progress_bar_on_finish: bool = delet_progress_bar_on_finish

        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QtWidgets.QWidget(self)
        progress_widget = QtWidgets.QWidget(content_widget)
        progress_layout = QtWidgets.QVBoxLayout(progress_widget)
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(progress_widget, 0)
        content_layout.addStretch(1)
        scroll_area.setWidget(content_widget)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_area)

        self._scroll_area = scroll_area
        self._progress_layout = progress_layout
        self.setMinimumSize(400, 300)

    def update_progress_bars(self):

        for item_id, progress in self._controller.get_progress_items():
            if item_id in self._progress_bar_by_id:
                continue
            self._add_progress_bar(item_id, progress)

        for progress_bar_instance in self._progress_bar_by_id.values():
            progress_bar_instance.update_progress()
            if progress_bar_instance.is_finished():
                if self._delet_progress_bar_on_finish:
                    progress_bar_instance.setVisible(False)
                else:

                    progress_bar_instance.progress_bar.setStyleSheet(
                        FINISHED_STYLE_SHEET
                    )
                    progress_bar_instance.progress_bar.setValue(100)
                    progress_bar_instance.progress_bar.setFormat("Done")

    def _add_progress_bar(self, item_id, progress):
        progress_bar_instance = ProgressBar(progress, self)
        progress_bar_instance.progress_bar.setStyleSheet(DEFAULT_STYLE_SHEET)

        self._progress_bar_by_id[item_id] = progress_bar_instance
        self._progress_layout.addWidget(progress_bar_instance, 0)

    def _close_window(self):
        self.close()


class ProgressDialog(QtWidgets.QDialog):

    def __init__(
        self,
        controller,
        delet_progress_bar_on_finish: bool = True,
        close_on_finish: bool = False,
    ):
        super().__init__()

        self._controller: worker.Controller = controller
        self._close_on_finish = close_on_finish

        widget = MultiProgressWidget(
            controller=controller,
            parent=self,
            delet_progress_bar_on_finish=delet_progress_bar_on_finish,
        )
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(widget)
        timer = QtCore.QTimer()
        timer.setInterval(100)
        timer.timeout.connect(self._update_progress_elements)

        self._widget = widget
        self._timer = timer

    def start(self):
        self._controller.start()
        self._timer.start()
        self.show()

    def _update_progress_elements(self):
        if self._controller.work_finished:
            self._timer.stop()
            if self._close_on_finish:
                self.close()
            return

        self._widget.update_progress_bars()
