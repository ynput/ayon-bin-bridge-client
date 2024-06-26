import os
import sys

from qtpy import QtWidgets
from ayon_bin_distro.work_handler import worker
from ayon_bin_distro.gui import progress_ui
import random
import time


def test_func(progress_item):
    for i in range(101):
        time.sleep(random.uniform(0.01, 0.1))
        progress_item.progress = i


def test_func_no_progress(progress_item):
    for i in range(101):
        time.sleep(random.uniform(0.01, 0.1))


def test_with_fake_data_no_icon():

    app = QtWidgets.QApplication(sys.argv)
    controller = worker.Controller()
    ui = progress_ui.ProgressDialog(controller)

    for i in range(100):
        controller.construct_work_item(func=test_func, progress_title=f"test{i}")

    ui.start()
    sys.exit(app.exec_())


def test_ui_with_fake_data_with_icon():
    icon_path = os.path.join(
        os.path.abspath(os.curdir), "test", "ay-symbol-blackw-full.png"
    )

    app = QtWidgets.QApplication(sys.argv)
    controller = worker.Controller()
    ui = progress_ui.ProgressDialog(controller)

    for i in range(100):
        controller.construct_work_item(
            func=test_func, progress_title=f"test{i}", icon_path=icon_path
        )

    ui.start()
    sys.exit(app.exec_())


def test_no_delet():
    icon_path = os.path.join(
        os.path.abspath(os.curdir), "test", "ay-symbol-blackw-full.png"
    )

    app = QtWidgets.QApplication(sys.argv)
    controller = worker.Controller()
    ui = progress_ui.ProgressDialog(controller, delet_progress_bar_on_finish=False)

    for i in range(100):
        controller.construct_work_item(
            func=test_func, progress_title=f"test{i}", icon_path=icon_path
        )

    ui.start()
    sys.exit(app.exec_())


def test_no_delet_no_progress():
    icon_path = os.path.join(
        os.path.abspath(os.curdir), "test", "ay-symbol-blackw-full.png"
    )

    app = QtWidgets.QApplication(sys.argv)
    controller = worker.Controller()
    ui = progress_ui.ProgressDialog(
        controller, close_on_finish=False, delet_progress_bar_on_finish=False
    )

    for i in range(100):
        controller.construct_work_item(
            func=test_func_no_progress, progress_title=f"test{i}", icon_path=icon_path
        )

    ui.start()
    sys.exit(app.exec_())


def test_with_dep():

    controller = worker.Controller()

    app = QtWidgets.QApplication(sys.argv)
    ui = progress_ui.ProgressDialog(controller, close_on_finish=True)

    itemA = controller.construct_work_item(func=test_func)
    controller.construct_work_item(func=test_func, dependency_id=[itemA.get_uuid()])

    ui.start()
    sys.exit(app.exec_())
