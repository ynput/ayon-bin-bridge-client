import os
import sys
from PyQt5.QtWidgets import QApplication

from ayon_bin_distro.work_handler import worker
from ayon_bin_distro.gui import progress_ui
import random
import time
from typing import Union


def test_func(progress_item):
    for i in range(101):
        # print(f" i finished {i}% off the work \n the args are: {args} and the kargs are: {kargs}")
        time.sleep(random.uniform(0.01, 0.1))
        # time.sleep(0.1)
        progress_item.progress = i


def main():
    icon_path = os.path.join(
        os.path.abspath(os.curdir), "test", "ay-symbol-blackw-full.png"
    )

    app = QApplication(sys.argv)
    controller = worker.Controller()
    ui = progress_ui.ProgressDialog(controller)

    for i in range(100):
        controller.construct_work_item(func=test_func, progress_title=f"test{i}")

    ui.start()
    sys.exit(app.exec_())
